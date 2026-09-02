[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"

$IndexUri = "https://kohesio.ec.europa.eu/en/data/projects-2021-2027/latest"
$Headers = @{
    "User-Agent" = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36"
    "Accept" = "text/html,application/xhtml+xml;q=0.9"
}

function Get-Sha256Hex {
    param(
        [Parameter(Mandatory = $true)][byte[]]$Bytes
    )

    $sha = [System.Security.Cryptography.SHA256]::Create()
    try {
        return ([System.BitConverter]::ToString($sha.ComputeHash($Bytes))).Replace("-", "").ToLowerInvariant()
    }
    finally {
        $sha.Dispose()
    }
}

function ConvertTo-PlainAnchorText {
    param(
        [Parameter(Mandatory = $true)][string]$Html
    )

    $withoutTags = [System.Text.RegularExpressions.Regex]::Replace($Html, "<[^>]+>", " ")
    $decoded = [System.Net.WebUtility]::HtmlDecode($withoutTags)
    return ([System.Text.RegularExpressions.Regex]::Replace($decoded, "\s+", " ")).Trim()
}

function Resolve-LinkUri {
    param(
        [Parameter(Mandatory = $true)][System.Uri]$BaseUri,
        [Parameter(Mandatory = $true)][string]$Href
    )

    $value = [System.Net.WebUtility]::HtmlDecode($Href).Trim()
    if ([string]::IsNullOrWhiteSpace($value)) {
        return $null
    }
    if ($value.StartsWith("#") -or $value.StartsWith("javascript:", [System.StringComparison]::OrdinalIgnoreCase)) {
        return $null
    }

    try {
        return [System.Uri]::new($BaseUri, $value)
    }
    catch {
        return $null
    }
}

# This probe retrieves only the official Kohesio 2021-2027 download INDEX page. It never follows
# a distribution link and never downloads CSV/XLSX/RDF project data. That distinction is mandatory
# under ProcRun's pre-receipt zero-PII boundary.
$webResponse = Invoke-WebRequest `
    -Uri $IndexUri `
    -Method Get `
    -Headers $Headers `
    -UseBasicParsing `
    -TimeoutSec 45

$contentType = [string]$webResponse.Headers["Content-Type"]
if ($contentType -notmatch "(?i)^text/html(?:\s*;|$)") {
    $displayType = if ([string]::IsNullOrWhiteSpace($contentType)) { "<missing>" } else { $contentType }
    throw "Kohesio 2021-2027 metadata probe expected HTML index content but received '${displayType}'; failing closed."
}

$html = [string]$webResponse.Content
$htmlBytes = [System.Text.Encoding]::UTF8.GetBytes($html)
$baseUri = [System.Uri]$IndexUri
$candidates = @()
$seen = @{}

$anchorPattern = '(?is)<a\b[^>]*\bhref\s*=\s*["''](?<href>[^"'']+)["''][^>]*>(?<text>.*?)</a>'
foreach ($match in [System.Text.RegularExpressions.Regex]::Matches($html, $anchorPattern)) {
    $resolved = Resolve-LinkUri -BaseUri $baseUri -Href ([string]$match.Groups["href"].Value)
    if ($null -eq $resolved -or $resolved.Scheme -notin @("http", "https")) {
        continue
    }

    $text = ConvertTo-PlainAnchorText -Html ([string]$match.Groups["text"].Value)
    $searchable = ("{0} {1}" -f $resolved.AbsoluteUri, $text).ToLowerInvariant()
    $looksLikeDistribution = (
        $searchable -match "projects-2021-2027" -or
        $searchable -match "(?:^|[^a-z])csv(?:[^a-z]|$)" -or
        $searchable -match "(?:^|[^a-z])xlsx(?:[^a-z]|$)" -or
        $searchable -match "(?:^|[^a-z])rdf(?:[^a-z]|$)" -or
        $searchable -match "download" -or
        $searchable -match "portugal" -or
        $searchable -match "(?:^|[^a-z])pt(?:[^a-z]|$)"
    )
    if (-not $looksLikeDistribution) {
        continue
    }

    $key = $resolved.AbsoluteUri
    if ($seen.ContainsKey($key)) {
        continue
    }
    $seen[$key] = $true

    $candidates += [ordered]@{
        host = $resolved.Host
        path_and_query = $resolved.PathAndQuery
        anchor_text = $text
    }
}

[ordered]@{
    probe_contract = "kohesio-2021-download-metadata-v1"
    index_uri = $IndexUri
    response_content_type = $contentType
    response_length_bytes = $htmlBytes.Length
    response_sha256 = Get-Sha256Hex -Bytes $htmlBytes
    distribution_bodies_fetched = $false
    candidate_count = $candidates.Count
    candidates = $candidates
} | ConvertTo-Json -Depth 8
