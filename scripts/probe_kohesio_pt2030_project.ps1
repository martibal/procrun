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
    "Accept" = "application/sparql-results+xml,application/sparql-results+json;q=0.9"
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

function ConvertFrom-SparqlXml {
    param(
        [Parameter(Mandatory = $true)][string]$Raw,
        [Parameter(Mandatory = $true)][string]$Method,
        [Parameter(Mandatory = $true)][string]$ContentType
    )

    $settings = New-Object System.Xml.XmlReaderSettings
    $settings.DtdProcessing = [System.Xml.DtdProcessing]::Prohibit
    $settings.XmlResolver = $null

    $stringReader = New-Object System.IO.StringReader($Raw)
    $xmlReader = $null
    try {
        $xmlReader = [System.Xml.XmlReader]::Create($stringReader, $settings)
        $document = New-Object System.Xml.XmlDocument
        $document.XmlResolver = $null
        $document.Load($xmlReader)
    }
    catch {
        throw "${Method} returned '${ContentType}' but the body was not valid SPARQL Results XML; response body was not logged."
    }
    finally {
        if ($null -ne $xmlReader) {
            $xmlReader.Dispose()
        }
        $stringReader.Dispose()
    }

    $namespace = New-Object System.Xml.XmlNamespaceManager($document.NameTable)
    $namespace.AddNamespace("sr", "http://www.w3.org/2005/sparql-results#")

    $root = $document.SelectSingleNode("/sr:sparql", $namespace)
    $head = $document.SelectSingleNode("/sr:sparql/sr:head", $namespace)
    $results = $document.SelectSingleNode("/sr:sparql/sr:results", $namespace)
    if ($null -eq $root -or $null -eq $head -or $null -eq $results) {
        throw "${Method} returned XML without the SPARQL Results envelope; response values were not logged."
    }

    $variables = @()
    foreach ($variableNode in @($document.SelectNodes("/sr:sparql/sr:head/sr:variable", $namespace))) {
        $variables += [string]$variableNode.GetAttribute("name")
    }

    $bindings = @()
    foreach ($resultNode in @($document.SelectNodes("/sr:sparql/sr:results/sr:result", $namespace))) {
        $row = [ordered]@{}
        foreach ($bindingNode in @($resultNode.SelectNodes("sr:binding", $namespace))) {
            $name = [string]$bindingNode.GetAttribute("name")
            if ([string]::IsNullOrWhiteSpace($name)) {
                throw "${Method} returned a SPARQL XML binding without a variable name; failing closed."
            }

            $valueNode = $bindingNode.FirstChild
            while ($null -ne $valueNode -and $valueNode.NodeType -ne [System.Xml.XmlNodeType]::Element) {
                $valueNode = $valueNode.NextSibling
            }
            if ($null -eq $valueNode) {
                throw "${Method} returned a SPARQL XML binding without a value node; failing closed."
            }

            $value = [ordered]@{
                type = [string]$valueNode.LocalName
                value = [string]$valueNode.InnerText
            }
            $language = [string]$valueNode.GetAttribute("lang", "http://www.w3.org/XML/1998/namespace")
            if (-not [string]::IsNullOrWhiteSpace($language)) {
                $value["xml:lang"] = $language
            }
            $datatype = [string]$valueNode.GetAttribute("datatype")
            if (-not [string]::IsNullOrWhiteSpace($datatype)) {
                $value["datatype"] = $datatype
            }
            $row[$name] = [pscustomobject]$value
        }
        $bindings += [pscustomobject]$row
    }

    return [pscustomobject]@{
        head = [pscustomobject]@{ vars = $variables }
        results = [pscustomobject]@{ bindings = $bindings }
    }
}

function ConvertFrom-SparqlWebResponse {
    param(
        [Parameter(Mandatory = $true)]$WebResponse,
        [Parameter(Mandatory = $true)][string]$Method
    )

    $contentType = [string]$WebResponse.Headers["Content-Type"]
    $raw = [string]$WebResponse.Content

    if ($contentType -match "(?i)^application/sparql-results\+xml(?:\s*;|$)") {
        $parsed = ConvertFrom-SparqlXml -Raw $raw -Method $Method -ContentType $contentType
        $script:SuccessfulContentType = $contentType
        return $parsed
    }

    if ($contentType -match "(?i)^application/(sparql-results\+json|json)(?:\s*;|$)") {
        try {
            $parsed = $raw | ConvertFrom-Json
        }
        catch {
            throw "${Method} returned '${contentType}' but the body was not valid JSON; response body was not logged."
        }

        if ($null -eq $parsed -or $null -eq $parsed.head -or $null -eq $parsed.results) {
            $keys = @()
            if ($null -ne $parsed) {
                $keys = @($parsed.PSObject.Properties.Name)
            }
            $keyText = if ($keys.Count -gt 0) { $keys -join "," } else { "<none>" }
            throw "${Method} returned JSON without the SPARQL head/results envelope (top-level keys: ${keyText}); response values were not logged."
        }

        $script:SuccessfulContentType = $contentType
        return $parsed
    }

    $displayType = if ([string]::IsNullOrWhiteSpace($contentType)) { "<missing>" } else { $contentType }
    throw "${Method} returned unsupported SPARQL result content type '${displayType}'; response body was not logged."
}

function Invoke-SafeSparqlRequest {
    $attemptErrors = @()

    # EUKG currently returns standards-compliant SPARQL Results XML for GET even when JSON is
    # requested. Accept either standard tuple-result serialization, but only after strict parsing.
    try {
        $getParameters = @{
            query = $Query
            format = "application/sparql-results+xml"
        }
        $uri = New-QueryUri -BaseUri $Endpoint -Parameters $getParameters
        $webResponse = Invoke-WebRequest `
            -Uri $uri `
            -Method Get `
            -Headers $Headers `
            -UseBasicParsing `
            -TimeoutSec 45
        $response = ConvertFrom-SparqlWebResponse -WebResponse $webResponse -Method "GET"
        $script:SuccessfulTransport = "GET"
        return $response
    }
    catch {
        $attemptErrors += Format-RequestFailure -Method "GET" -ErrorRecord $_
    }

    # qEndpoint documents form-encoded POST. Reuse the exact same allowlisted query; do not
    # broaden the request. JSON or XML is accepted only if it parses as SPARQL Results.
    try {
        $postParameters = @{
            query = $Query
        }
        $webResponse = Invoke-WebRequest `
            -Uri $Endpoint `
            -Method Post `
            -Headers $Headers `
            -ContentType "application/x-www-form-urlencoded" `
            -Body $postParameters `
            -UseBasicParsing `
            -TimeoutSec 45
        $response = ConvertFrom-SparqlWebResponse -WebResponse $webResponse -Method "POST"
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

    if ($null -eq $Response.head -or $null -eq $Response.results) {
        throw "SPARQL response is missing the required head/results envelope; failing closed."
    }

    $allowed = @{}
    foreach ($name in $AllowedVariables) {
        $allowed[$name] = $true
    }

    foreach ($declared in @($Response.head.vars)) {
        $name = [string]$declared
        if ([string]::IsNullOrWhiteSpace($name)) {
            continue
        }
        if (-not $allowed.ContainsKey($name)) {
            throw "SPARQL response declared unexpected variable '$name'; failing closed."
        }
    }

    foreach ($binding in @($Response.results.bindings)) {
        if ($null -eq $binding) {
            continue
        }
        foreach ($property in $binding.PSObject.Properties) {
            $name = [string]$property.Name
            if ([string]::IsNullOrWhiteSpace($name) -or -not $allowed.ContainsKey($name)) {
                throw "SPARQL response returned unexpected variable '$name'; failing closed."
            }
        }
    }
}

$response = Invoke-SafeSparqlRequest
Assert-AllowedVariables -Response $response

$rows = @($response.results.bindings)

[ordered]@{
    probe_contract = "kohesio-pt2030-safe-project-smoke-v4"
    endpoint = $Endpoint
    transport = $script:SuccessfulTransport
    response_content_type = $script:SuccessfulContentType
    target_operation_code = $TargetOperationCode
    selected_variables = $AllowedVariables
    row_count = $rows.Count
    coverage_found = ($rows.Count -gt 0)
    rows = $rows
} | ConvertTo-Json -Depth 12
