param(
    [string]$Server = "62.238.117.62",
    [string]$SshUser = "root",
    [string]$Seed = "classification-quality-2026-09-v1",
    [int]$SampleSize = 300,
    [int]$DoubleReviewSize = 30,
    [string]$OutputDir = "docs/classification_quality/reviews"
)

$ErrorActionPreference = "Stop"
$SshKey = Join-Path $env:USERPROFILE ".ssh\procrun_hetzner"

if (-not (Test-Path $SshKey)) { throw "Missing SSH key: $SshKey" }
if ($SampleSize -lt 300) { throw "Classification quality gate requires SampleSize >= 300." }
if ($DoubleReviewSize -lt 30) { throw "Classification quality gate requires DoubleReviewSize >= 30." }
if ($DoubleReviewSize -gt $SampleSize) { throw "DoubleReviewSize cannot exceed SampleSize." }
if ($Seed -notmatch '^[A-Za-z0-9._-]+$') { throw "Seed contains unsupported characters." }

if (-not (Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null
}

function Invoke-RemoteSql([string]$sql) {
    $result = $sql | ssh -T `
        -o ConnectTimeout=10 `
        -o ConnectionAttempts=1 `
        -i $SshKey `
        "${SshUser}@${Server}" `
        "sudo -u postgres psql -d procrun -q"
    if ($LASTEXITCODE -ne 0) { throw "Remote classification-quality SQL failed." }
    return $result
}

$countSql = @'
COPY (
WITH latest_assessment AS (
    SELECT DISTINCT ON (component_id)
        component_id, state, cutoff_date, as_of, inserted_at, version_id
    FROM procrun.assessment_versions
    ORDER BY component_id, cutoff_date DESC, as_of DESC, inserted_at DESC, version_id DESC
),
latest_component AS (
    SELECT DISTINCT ON (component_id)
        component_id, category, as_of, inserted_at, version_id
    FROM procrun.component_versions
    ORDER BY component_id, as_of DESC, inserted_at DESC, version_id DESC
)
SELECT a.state, c.category, count(*) AS n
FROM latest_assessment a
JOIN latest_component c USING (component_id)
GROUP BY a.state, c.category
ORDER BY a.state, c.category
) TO STDOUT WITH CSV HEADER;
'@

$populationCsv = Invoke-RemoteSql $countSql
$populationPath = Join-Path $OutputDir "classification_quality_population_${Seed}.csv"
$populationCsv | Set-Content -Path $populationPath -Encoding UTF8
$population = @($populationCsv | ConvertFrom-Csv)
$totalPopulation = ($population | Measure-Object -Property n -Sum).Sum
if ($null -eq $totalPopulation) { $totalPopulation = 0 }
$totalPopulation = [int]$totalPopulation

Write-Host "Current eligible classification population: $totalPopulation"

$sampleSql = @"
COPY (
WITH latest_assessment AS (
    SELECT DISTINCT ON (component_id)
        version_id,
        component_id,
        operation_code,
        state,
        cutoff_date,
        rule_version,
        matching_candidates,
        accepted_evidence_version_ids,
        as_of,
        inserted_at
    FROM procrun.assessment_versions
    ORDER BY component_id, cutoff_date DESC, as_of DESC, inserted_at DESC, version_id DESC
),
latest_component AS (
    SELECT DISTINCT ON (component_id)
        component_id,
        operation_code,
        category,
        description,
        scope_evidence,
        as_of,
        inserted_at,
        version_id
    FROM procrun.component_versions
    ORDER BY component_id, as_of DESC, inserted_at DESC, version_id DESC
),
latest_project AS (
    SELECT DISTINCT ON (operation_code)
        operation_code,
        project_title,
        source_record_version_id,
        as_of,
        inserted_at,
        version_id
    FROM procrun.funding_project_versions
    ORDER BY operation_code, as_of DESC, inserted_at DESC, version_id DESC
),
eligible AS (
    SELECT
        a.component_id,
        a.operation_code,
        c.category,
        split_part(c.category, ':', 1) AS predicted_sector,
        c.description AS component_description,
        c.scope_evidence,
        p.project_title,
        a.state AS predicted_state,
        a.cutoff_date,
        a.rule_version,
        ps.source_url AS funding_source_url,
        CASE WHEN a.state = 'CLOSED' THEN es.source_url ELSE NULL END AS procurement_source_url,
        row_number() OVER (
            PARTITION BY c.category, a.state
            ORDER BY md5('$Seed' || ':' || a.component_id)
        ) AS stratum_rank,
        md5('$Seed' || ':' || a.component_id) AS sample_hash,
        md5('$Seed' || ':double:' || a.component_id) AS double_hash
    FROM latest_assessment a
    JOIN latest_component c ON c.component_id = a.component_id
    JOIN latest_project p ON p.operation_code = a.operation_code
    JOIN procrun.source_record_versions ps ON ps.version_id = p.source_record_version_id
    LEFT JOIN procrun.procurement_evidence_versions pe
      ON pe.version_id = CASE
          WHEN cardinality(a.accepted_evidence_version_ids) > 0 THEN a.accepted_evidence_version_ids[1]
          ELSE NULL
      END
    LEFT JOIN procrun.source_record_versions es ON es.version_id = pe.source_record_version_id
),
sampled AS (
    SELECT *
    FROM eligible
    ORDER BY stratum_rank, category, predicted_state, sample_hash
    LIMIT $SampleSize
),
marked AS (
    SELECT
        sampled.*,
        row_number() OVER (ORDER BY double_hash) <= $DoubleReviewSize AS double_review_required
    FROM sampled
)
SELECT
    row_number() OVER (ORDER BY stratum_rank, category, predicted_state, sample_hash) AS sample_index,
    component_id,
    operation_code,
    category AS predicted_category,
    predicted_sector,
    predicted_state,
    component_description,
    project_title,
    scope_evidence,
    cutoff_date,
    rule_version,
    funding_source_url,
    coalesce(procurement_source_url, '') AS procurement_source_url,
    CASE WHEN double_review_required THEN 'yes' ELSE 'no' END AS double_review_required,
    ''::text AS need_present,
    ''::text AS correct_need_category,
    ''::text AS correct_sector_or_null,
    ''::text AS correct_state,
    ''::text AS evidence_sufficient,
    ''::text AS duplicate,
    ''::text AS over_specific,
    ''::text AS error_class,
    ''::text AS reviewer,
    ''::text AS reviewed_at,
    ''::text AS reviewer_2,
    ''::text AS need_present_2,
    ''::text AS correct_need_category_2,
    ''::text AS correct_sector_or_null_2,
    ''::text AS correct_state_2,
    ''::text AS evidence_sufficient_2,
    ''::text AS reviewed_at_2
FROM marked
ORDER BY sample_index
) TO STDOUT WITH CSV HEADER;
"@

$samplePath = Join-Path $OutputDir "classification_quality_${Seed}.csv"
Invoke-RemoteSql $sampleSql | Set-Content -Path $samplePath -Encoding UTF8

$manifestPath = Join-Path $OutputDir "classification_quality_manifest_${Seed}.txt"
@"
ProcRun classification quality benchmark manifest
seed=$Seed
sample_size_required=$SampleSize
double_review_required=$DoubleReviewSize
eligible_population=$totalPopulation
created_at=$((Get-Date).ToString("yyyy-MM-ddTHH:mm:ssK"))
git_commit=$((git rev-parse HEAD).Trim())
sampling=stratified round-robin by category/state, deterministic md5 within stratum
double_review_selection=deterministic md5(seed || ':double:' || component_id)
canonical_gate=docs/CLASSIFICATION_QUALITY_LAUNCH_GATE.md
"@ | Set-Content -Path $manifestPath -Encoding UTF8

Write-Host "Wrote benchmark sample to $samplePath"
Write-Host "Wrote manifest to $manifestPath"

if ($totalPopulation -lt $SampleSize) {
    Write-Error "Classification quality sample-size gate NOT MET: population=$totalPopulation required=$SampleSize. Files remain for traceability. Do not declare PASS or reduce the locked threshold."
    exit 2
}

Write-Host "Classification quality sample-size gate met. Freeze the sample before review begins."
