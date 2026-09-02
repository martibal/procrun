[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"

$Endpoint = "https://query.linkedopendata.eu/sparql"
$TargetOperationCode = "PACS-FC-01781200"
$AllowedVariables = @(
    "project",
    "operation_identifier",
    "operation_name",
    "summary",
    "programming_period",
    "programme",
    "fund",
    "start_time",
    "end_time",
    "budget",
    "eu_contribution",
    "nuts_code",
    "last_update"
)
$Headers = @{
    "User-Agent" = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36"
    "Accept" = "application/sparql-results+json,application/json;q=0.9"
}

# Phase 2 is deliberately a single exact-code lookup. Every selected predicate is frozen in
# docs/KOHESIO_PROPERTY_ALLOWLIST.md. P841 (beneficiary) is intentionally absent.
$Query = @'
PREFIX kohesio: <https://linkedopendata.eu/prop/direct/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?project ?operation_identifier ?operation_name ?summary ?programming_period
       ?programme ?fund ?start_time ?end_time ?budget ?eu_contribution ?nuts_code ?last_update
WHERE {
  ?project kohesio:P1367 ?operation_identifier .
  FILTER(STR(?operation_identifier) = "PACS-FC-01781200")

  OPTIONAL {
    ?project rdfs:label ?operation_name .
    FILTER(LANG(?operation_name) = "" || LANGMATCHES(LANG(?operation_name), "pt"))
  }
  OPTIONAL {
    ?project kohesio:P836 ?summary .
    FILTER(LANG(?summary) = "" || LANGMATCHES(LANG(?summary), "pt"))
  }
  OPTIONAL { ?project kohesio:P605685 ?programming_period . }
  OPTIONAL { ?project kohesio:P1368 ?programme . }
  OPTIONAL { ?project kohesio:P1584 ?fund . }
  OPTIONAL { ?project kohesio:P20 ?start_time . }
  OPTIONAL { ?project kohesio:P33 ?end_time . }
  OPTIONAL { ?project kohesio:P474 ?budget . }
  OPTIONAL { ?project kohesio:P835 ?eu_contribution . }
  OPTIONAL { ?project kohesio:P192 ?nuts_code . }
  OPTIONAL { ?project kohesio:P1820 ?last_update . }
}
LIMIT 5
'@

function New-QueryUri {
    param(
        [Parameter(Mandatory = $true)][string]$BaseUri,
        [Parameter(Mandatory = $true)][hashtable]$Parameters
    )

    $pairs = foreach ($key in ($Parameters.Keys | Sort-Object)) {
        $encodedKey = [System.Uri]::EscapeDataString([string]$key)
        $encodedValue = [System.Uri]::EscapeDataString([string]$Parameters[$key])
        "${encodedKey}=${encodedValue}"
    }
    return "${BaseUri}?$($pairs -join '&')"
}

function Format-RequestFailure {
    param(
        [Parameter(Mandatory = $true)][string]$Method,
        [Parameter(Mandatory = $true)]$ErrorRecord
    )

    $status = $null
    if ($null -ne $ErrorRecord.Exception.Response) {
        try {
            $status = [int]$ErrorRecord.Exception.Response.StatusCode
        }
        catch {
            $status = $null
        }
    }

    if ($null -ne $status) {
        return "${Method} status=${status}: $($ErrorRecord.Exception.Message)"
    }
    return "${Method}: $($ErrorRecord.Exception.Message)"
}

function Invoke-SafeSparqlRequest {
    $parameters = @{
        query = $Query
        format = "application/sparql-results+json"
    }
    $attemptErrors = @()

    try {
        $uri = New-QueryUri -BaseUri $Endpoint -Parameters $parameters
        $response = Invoke-RestMethod -Uri $uri -Method Get -Headers $Headers -TimeoutSec 45
        $script:SuccessfulTransport = "GET"
        return $response
    }
    catch {
        $attemptErrors += Format-RequestFailure -Method "GET" -ErrorRecord $_
    }

    try {
        $response = Invoke-RestMethod `
            -Uri $Endpoint `
            -Method Post `
            -Headers $Headers `
            -ContentType "application/x-www-form-urlencoded" `
            -Body $parameters `
            -TimeoutSec 45
        $script:SuccessfulTransport = "POST"
        return $response
    }
    catch {
        $attemptErrors += Format-RequestFailure -Method "POST" -ErrorRecord $_
    }

    throw "Kohesio safe SPARQL smoke probe failed. $($attemptErrors -join ' | ')"
}

function Assert-AllowedVariables {
    param(
        [Parameter(Mandatory = $true)]$Response
    )

    $allowed = @{}
    foreach ($name in $AllowedVariables) {
        $allowed[$name] = $true
    }

    foreach ($name in @($Response.head.vars)) {
        if (-not $allowed.ContainsKey([string]$name)) {
            throw "SPARQL response declared unexpected variable '$name'; failing closed."
        }
    }

    foreach ($binding in @($Response.results.bindings)) {
        foreach ($property in $binding.PSObject.Properties) {
            if (-not $allowed.ContainsKey([string]$property.Name)) {
                throw "SPARQL response returned unexpected variable '$($property.Name)'; failing closed."
            }
        }
    }
}

$response = Invoke-SafeSparqlRequest
Assert-AllowedVariables -Response $response

$rows = @($response.results.bindings)

[ordered]@{
    probe_contract = "kohesio-pt2030-safe-project-smoke-v1"
    endpoint = $Endpoint
    transport = $script:SuccessfulTransport
    target_operation_code = $TargetOperationCode
    selected_variables = $AllowedVariables
    row_count = $rows.Count
    coverage_found = ($rows.Count -gt 0)
    rows = $rows
} | ConvertTo-Json -Depth 12
