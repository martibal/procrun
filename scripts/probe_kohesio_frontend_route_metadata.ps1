[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"

$IndexUri = "https://kohesio.ec.europa.eu/en/data/projects-2021-2027/latest"
$AllowedHost = "kohesio.ec.europa.eu"
$Headers = @{
    "User-Agent" = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36"
    "Accept" = "text/html,application/xhtml+xml;q=0.9"
}

function Get-Sha256Hex {
    param([Parameter(Mandatory = $true)][byte[]]$Bytes)

    $sha = [System.Security.Cryptography.SHA256]::Create()
    try {
        return ([System.BitConverter]::ToString($sha.ComputeHash($Bytes))).Replace("-", "").ToLowerInvariant()
    }
    finally {
        $sha.Dispose()
    }
}

function Resolve-SafeAssetUri {
    param(
        [Parameter(Mandatory = $true)][System.Uri]$BaseUri,
        [Parameter(Mandatory = $true)][string]$Href
    )

    try {
        $resolved = [System.Uri]::new($BaseUri, [System.Net.WebUtility]::HtmlDecode($Href).Trim())
    }
    catch {
        return $null
    }

    if ($resolved.Scheme -ne "https" -or $resolved.Host -ne $AllowedHost) {
        return $null
    }
    if ($resolved.AbsolutePath -notmatch "(?i)\.js$") {
        return $null
    }
    return $resolved
}

# This probe retrieves only Kohesio frontend HTML and same-origin JavaScript assets referenced by it.
# It never calls /api/projects, /api/data/object, SPARQL, CSV/XLSX/RDF distributions, or any project API.
$indexResponse = Invoke-WebRequest `
    -Uri $IndexUri `
    -Method Get `
    -Headers $Headers `
    -UseBasicParsing `
    -TimeoutSec 45

$indexType = [string]$indexResponse.Headers["Content-Type"]
if ($indexType -notmatch "(?i)^text/html(?:\s*;|$)") {
    throw "Expected Kohesio HTML shell; received '${indexType}'."
}

$html = [string]$indexResponse.Content
$baseUri = [System.Uri]$IndexUri
$assetUris = @()
$seen = @{}

$patterns = @(
    '(?is)<script\b[^>]*\bsrc\s*=\s*["''](?<href>[^"'']+)["'']',
    '(?is)<link\b[^>]*\brel\s*=\s*["''][^"'']*(?:modulepreload|preload)[^"'']*["''][^>]*\bhref\s*=\s*["''](?<href>[^"'']+\.js(?:\?[^"'']*)?)["'']'
)

foreach ($pattern in $patterns) {
    foreach ($match in [System.Text.RegularExpressions.Regex]::Matches($html, $pattern)) {
        $uri = Resolve-SafeAssetUri -BaseUri $baseUri -Href ([string]$match.Groups["href"].Value)
        if ($null -eq $uri) {
            continue
        }
        if ($seen.ContainsKey($uri.AbsoluteUri)) {
            continue
        }
        $seen[$uri.AbsoluteUri] = $true
        $assetUris += $uri
    }
}

if ($assetUris.Count -eq 0) {
    throw "Kohesio HTML shell exposed no same-origin JavaScript asset references; failing closed."
}
if ($assetUris.Count -gt 24) {
    throw "Kohesio HTML shell exposed more than 24 JavaScript assets; refusing unbounded metadata retrieval."
}

$apiLiteralPattern = '(?i)(?:https://kohesio\.ec\.europa\.eu)?/api/[A-Za-z0-9_./?=&${}:\-]+'
$parameterKeywords = @(
    "fields",
    "field",
    "select",
    "projection",
    "countryCode",
    "programmingPeriod",
    "programming_period",
    "page",
    "size"
)
$assetResults = @()
$allApiLiterals = @{}

foreach ($assetUri in $assetUris) {
    $assetHeaders = @{
        "User-Agent" = $Headers["User-Agent"]
        "Accept" = "application/javascript,text/javascript;q=0.9,*/*;q=0.1"
    }
    $response = Invoke-WebRequest `
        -Uri $assetUri.AbsoluteUri `
        -Method Get `
        -Headers $assetHeaders `
        -UseBasicParsing `
        -TimeoutSec 45

    $contentType = [string]$response.Headers["Content-Type"]
    if ($contentType -notmatch "(?i)(javascript|ecmascript|text/plain)") {
        throw "Frontend asset '$($assetUri.AbsolutePath)' returned unexpected content type '${contentType}'."
    }

    $text = [string]$response.Content
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($text)
    $literals = @{}
    foreach ($match in [System.Text.RegularExpressions.Regex]::Matches($text, $apiLiteralPattern)) {
        $literal = [string]$match.Value
        if ($literal.Length -gt 300) {
            continue
        }
        $literals[$literal] = $true
        $allApiLiterals[$literal] = $true
    }

    $keywords = @()
    foreach ($keyword in $parameterKeywords) {
        if ($text.IndexOf($keyword, [System.StringComparison]::OrdinalIgnoreCase) -ge 0) {
            $keywords += $keyword
        }
    }

    $assetResults += [ordered]@{
        path = $assetUri.AbsolutePath
        content_type = $contentType
        length_bytes = $bytes.Length
        sha256 = Get-Sha256Hex -Bytes $bytes
        api_literals = @($literals.Keys | Sort-Object)
        parameter_keywords_present = $keywords
    }
}

[ordered]@{
    probe_contract = "kohesio-frontend-route-metadata-v1"
    index_uri = $IndexUri
    index_sha256 = Get-Sha256Hex -Bytes ([System.Text.Encoding]::UTF8.GetBytes($html))
    project_api_called = $false
    distribution_body_fetched = $false
    javascript_asset_count = $assetResults.Count
    api_literals = @($allApiLiterals.Keys | Sort-Object)
    assets = $assetResults
} | ConvertTo-Json -Depth 10
