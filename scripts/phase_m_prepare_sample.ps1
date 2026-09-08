param(
    [string]$Server = "62.238.117.62",
    [string]$SshUser = "root",
    [string]$Seed = "phase-m-2026-09-08-v1",
    [int]$SampleSize = 30,
    [string]$OutputDir = "docs/phase_m/reviews"
)

$ErrorActionPreference = "Stop"
$SshKey = Join-Path $env:USERPROFILE ".ssh\procrun_hetzner"

if (-not (Test-Path $SshKey)) { throw "Missing SSH key: $SshKey" }
if ($SampleSize -lt 30) { throw "Phase M requires SampleSize >= 30." }
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
    if ($LASTEXITCODE -ne 0) { throw "Remote Phase M SQL failed." }
    return $result
}

$countSql = @'
COPY (
    WITH latest AS (
        SELECT DISTINCT ON (component_id)
            component_id, state, cutoff_date, as_of, inserted_at, version_id
        FROM procrun.assessment_versions
        ORDER BY component_id, cutoff_date DESC, as_of DESC, inserted_at DESC, version_id DESC
    )
    SELECT state, count(*) AS n
    FROM latest
    GROUP BY state
    ORDER BY state
) TO STDOUT WITH CSV HEADER;
'@

Write-Host "Checking current production state population before revealing the deterministic sample..."
$countCsv = Invoke-RemoteSql $countSql
$countPath = Join-Path $OutputDir "phase_m_population_${Seed}.csv"
$countCsv | Set-Content -Path $countPath -Encoding UTF8

$counts = @{}
($countCsv | ConvertFrom-Csv) | ForEach-Object { $counts[$_.state] = [int]$_.n }
$closedN = if ($counts.ContainsKey("CLOSED")) { $counts["CLOSED"] } else { 0 }
$openN = if ($counts.ContainsKey("OPEN")) { $counts["OPEN"] } else { 0 }
$unresolvedN = if ($counts.ContainsKey("UNRESOLVED")) { $counts["UNRESOLVED"] } else { 0 }

Write-Host "Current latest-state population: CLOSED=$closedN OPEN=$openN UNRESOLVED=$unresolvedN"

function Sample-Sql([string]$state) {
@"
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
        accepted_evidence_ids,
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
        c.description AS component_description,
        c.scope_evidence,
        p.project_title,
        a.cutoff_date,
        a.rule_version,
        ps.source_url AS funding_source_url,
        CASE WHEN a.state = 'CLOSED' THEN (
            SELECT candidate->>'tier'
            FROM jsonb_array_elements(a.matching_candidates) AS candidate
            WHERE candidate->>'disposition' = 'HIGH_CONFIDENCE'
            ORDER BY candidate->>'evidence_id'
            LIMIT 1
        ) ELSE NULL END AS match_tier,
        CASE WHEN a.state = 'CLOSED' THEN es.source_url ELSE NULL END AS procurement_source_url
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
    WHERE a.state = '$state'
),
sampled AS (
    SELECT *
    FROM eligible
    ORDER BY md5('$Seed' || ':' || component_id)
    LIMIT $SampleSize
)
SELECT
    '$state' AS sample_kind,
    row_number() OVER (ORDER BY md5('$Seed' || ':' || component_id)) AS sample_index,
    component_id,
    operation_code,
    category,
    component_description,
    project_title,
    scope_evidence,
    cutoff_date,
    rule_version,
    coalesce(match_tier, '') AS match_tier,
    funding_source_url,
    coalesce(procurement_source_url, '') AS procurement_source_url,
    ''::text AS human_verdict,
    ''::text AS human_reason,
    ''::text AS reviewer,
    ''::text AS reviewed_at
FROM sampled
ORDER BY sample_index
) TO STDOUT WITH CSV HEADER;
"@
}

$closedPath = Join-Path $OutputDir "phase_m_closed_${Seed}.csv"
$openPath = Join-Path $OutputDir "phase_m_open_${Seed}.csv"

if ($closedN -gt 0) {
    Invoke-RemoteSql (Sample-Sql "CLOSED") | Set-Content -Path $closedPath -Encoding UTF8
    Write-Host "Wrote deterministic CLOSED sample to $closedPath"
} else {
    "sample_kind,sample_index,component_id,operation_code,category,component_description,project_title,scope_evidence,cutoff_date,rule_version,match_tier,funding_source_url,procurement_source_url,human_verdict,human_reason,reviewer,reviewed_at" | Set-Content -Path $closedPath -Encoding UTF8
    Write-Host "No CLOSED rows exist; wrote header-only file to $closedPath"
}

if ($openN -gt 0) {
    Invoke-RemoteSql (Sample-Sql "OPEN") | Set-Content -Path $openPath -Encoding UTF8
    Write-Host "Wrote deterministic OPEN sample to $openPath"
} else {
    "sample_kind,sample_index,component_id,operation_code,category,component_description,project_title,scope_evidence,cutoff_date,rule_version,match_tier,funding_source_url,procurement_source_url,human_verdict,human_reason,reviewer,reviewed_at" | Set-Content -Path $openPath -Encoding UTF8
    Write-Host "No OPEN rows exist; wrote header-only file to $openPath"
}

$manifestPath = Join-Path $OutputDir "phase_m_manifest_${Seed}.txt"
@"
Phase M deterministic sample manifest
seed=$Seed
sample_size=$SampleSize
closed_population=$closedN
open_population=$openN
unresolved_population=$unresolvedN
created_at=$((Get-Date).ToString("yyyy-MM-ddTHH:mm:ssK"))
git_commit=$((git rev-parse HEAD).Trim())
sampling_order=md5(seed || ':' || component_id)
"@ | Set-Content -Path $manifestPath -Encoding UTF8

if ($closedN -lt $SampleSize -or $openN -lt $SampleSize) {
    Write-Error "Phase M sample-size gate NOT MET: requires >= $SampleSize current production CLOSED and >= $SampleSize OPEN. Current CLOSED=$closedN OPEN=$openN. Files were still generated for traceability. Do not calculate or publish a passing accuracy result. Under the continuation rule this remains an active validation/remediation gate."
    exit 2
}

Write-Host "Phase M sample-size gate met. Human review may begin."
