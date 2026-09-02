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

function Resolve-SafeBaseUri {
    param(
        [Parameter(Mandatory = $true)][System.Uri]$DocumentUri,
        [Parameter(Mandatory = $true)][string]$Html
    )

    $baseMatches = [System.Text.RegularExpressions.Regex]::Matches(
        $Html,
        '(?is)<base\b[^>]*\bhref\s*=\s*["''](?<href>[^"'']+)["'']'
    )
    if ($baseMatches.Count -eq 0) {
        return $DocumentUri
    }
    if ($baseMatches.Count -ne 1) {
        throw "Kohesio HTML shell declared multiple base href values; failing closed."
    }

    $href = [System.Net.WebUtility]::HtmlDecode(
        [string]$baseMatches[0].Groups["href"].Value
    ).Trim()
    try {
        $resolved = [System.Uri]::new($DocumentUri, $href)
    }
    catch {
        throw "Kohesio HTML shell declared an invalid base href; failing closed."
    }

    if ($resolved.Scheme -ne "https" -or $resolved.Host -ne $AllowedHost) {
        throw "Kohesio HTML shell declared a non-approved base origin; failing closed."
    }
    return $resolved
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

function ConvertTo-ServiceContextSnippet {
    param(
        [Parameter(Mandatory = $true)][string]$Text,
        [Parameter(Mandatory = $true)][int]$Index,
        [Parameter(Mandatory = $true)][int]$TokenLength,
        [int]$Before = 600,
        [int]$After = 2200
    )

    $start = [Math]::Max(0, $Index - $Before)
    $endExclusive = [Math]::Min($Text.Length, $Index + $TokenLength + $After)
    $snippet = $Text.Substring($start, $endExclusive - $start)
    $snippet = [System.Text.RegularExpressions.Regex]::Replace($snippet, '[\x00-\x1F\x7F]+', ' ')
    $snippet = [System.Text.RegularExpressions.Regex]::Replace($snippet, '\s+', ' ').Trim()
    if ($snippet.Length -gt 3000) {
        $snippet = $snippet.Substring(0, 3000)
    }
    return $snippet
}

function Get-TargetedServiceContexts {
    param(
        [Parameter(Mandatory = $true)][string]$Text,
        [Parameter(Mandatory = $true)][string[]]$Tokens,
        [int]$MaxPerToken = 2,
        [int]$MaxTotal = 16
    )

    $contexts = @()
    foreach ($token in $Tokens) {
        $searchFrom = 0
        $tokenCount = 0
        while ($searchFrom -lt $Text.Length -and $tokenCount -lt $MaxPerToken) {
            $index = $Text.IndexOf($token, $searchFrom, [System.StringComparison]::OrdinalIgnoreCase)
            if ($index -lt 0) {
                break
            }

            $contexts += [ordered]@{
                token = $token
                snippet = ConvertTo-ServiceContextSnippet `
                    -Text $Text `
                    -Index $index `
                    -TokenLength $token.Length
            }
            $tokenCount += 1
            if ($contexts.Count -ge $MaxTotal) {
                return $contexts
            }
            $searchFrom = $index + [Math]::Max(1, $token.Length)
        }
    }
    return $contexts
}

# Research-only source-code inspection. This probe retrieves only the official Kohesio HTML shell and
# same-origin JavaScript assets referenced by that shell. It never calls a project API, data-object route,
# SPARQL endpoint, or project distribution. It emits only bounded source-code contexts from public JS.
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
$documentUri = [System.Uri]$IndexUri
$assetBaseUri = Resolve-SafeBaseUri -DocumentUri $documentUri -Html $html
$assetUris = @()
$seen = @{}

$patterns = @(
    '(?is)<script\b[^>]*\bsrc\s*=\s*["''](?<href>[^"'']+)["'']',
    '(?is)<link\b[^>]*\brel\s*=\s*["''][^"'']*(?:modulepreload|preload)[^"'']*["''][^>]*\bhref\s*=\s*["''](?<href>[^"'']+\.js(?:\?[^"'']*)?)["'']'
)

foreach ($pattern in $patterns) {
    foreach ($match in [System.Text.RegularExpressions.Regex]::Matches($html, $pattern)) {
        $uri = Resolve-SafeAssetUri -BaseUri $assetBaseUri -Href ([string]$match.Groups["href"].Value)
        if ($null -eq $uri -or $seen.ContainsKey($uri.AbsoluteUri)) {
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

$serviceTokens = @(
    "getProjectsFilters",
    "getProjects(",
    "getProject(",
    "getFilter(",
    "getBeneficiariesFilters",
    "getBeneficiaries(",
    "this.http.get(",
    ".http.get(",
    "entityURL",
    "apiURL",
    "/projects",
    "projects?",
    "beneficiaryIdentifier",
    "uniqueIdentifier"
)

$assetResults = @()
$totalContextCount = 0
$MaxContextCountAcrossAssets = 20

foreach ($assetUri in $assetUris) {
    $response = Invoke-WebRequest `
        -Uri $assetUri.AbsoluteUri `
        -Method Get `
        -Headers @{
            "User-Agent" = $Headers["User-Agent"]
            "Accept" = "application/javascript,text/javascript;q=0.9,*/*;q=0.1"
        } `
        -UseBasicParsing `
        -TimeoutSec 45

    $contentType = [string]$response.Headers["Content-Type"]
    if ($contentType -notmatch "(?i)(javascript|ecmascript|text/plain)") {
        throw "Frontend asset '$($assetUri.AbsolutePath)' returned unexpected content type '${contentType}'."
    }

    $text = [string]$response.Content
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($text)
    $remaining = [Math]::Max(0, $MaxContextCountAcrossAssets - $totalContextCount)
    $contexts = @()
    if ($remaining -gt 0) {
        $contexts = @(Get-TargetedServiceContexts `
            -Text $text `
            -Tokens $serviceTokens `
            -MaxPerToken 2 `
            -MaxTotal ([Math]::Min(16, $remaining)))
        $totalContextCount += $contexts.Count
    }

    $assetResults += [ordered]@{
        path = $assetUri.AbsolutePath
        content_type = $contentType
        length_bytes = $bytes.Length
        sha256 = Get-Sha256Hex -Bytes $bytes
        targeted_service_contexts = $contexts
    }
}

[ordered]@{
    probe_contract = "kohesio-frontend-service-context-v1"
    index_uri = $IndexUri
    asset_base_uri = $assetBaseUri.AbsoluteUri
    index_sha256 = Get-Sha256Hex -Bytes ([System.Text.Encoding]::UTF8.GetBytes($html))
    project_api_called = $false
    distribution_body_fetched = $false
    javascript_asset_count = $assetResults.Count
    service_context_count = $totalContextCount
    service_context_limit = $MaxContextCountAcrossAssets
    max_context_chars = 3000
    assets = $assetResults
} | ConvertTo-Json -Depth 12
