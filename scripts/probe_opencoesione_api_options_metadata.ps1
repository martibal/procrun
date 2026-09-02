[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"

$ApiUri = "https://opencoesione.gov.it/api/progetti.json"
$AllowedHost = "opencoesione.gov.it"
$MaxBodyBytes = 128KB
$MaxShapePaths = 500

function Get-JsonShapePaths {
    param(
        [Parameter(Mandatory = $true)]$Value,
        [string]$Prefix = "",
        [int]$Depth = 0,
        [ref]$PathCount
    )

    if ($Depth -gt 8 -or $PathCount.Value -ge $MaxShapePaths) {
        return @()
    }

    $paths = @()
    if ($null -eq $Value) {
        return $paths
    }

    if ($Value -is [System.Collections.IDictionary]) {
        $properties = @($Value.Keys | ForEach-Object { [string]$_ })
        foreach ($name in $properties) {
            if ($PathCount.Value -ge $MaxShapePaths) { break }
            $path = if ([string]::IsNullOrWhiteSpace($Prefix)) { $name } else { "$Prefix.$name" }
            $paths += $path
            $PathCount.Value += 1
            $paths += Get-JsonShapePaths -Value $Value[$name] -Prefix $path -Depth ($Depth + 1) -PathCount $PathCount
        }
        return $paths
    }

    if ($Value -is [System.Management.Automation.PSCustomObject]) {
        foreach ($property in @($Value.PSObject.Properties)) {
            if ($PathCount.Value -ge $MaxShapePaths) { break }
            $name = [string]$property.Name
            $path = if ([string]::IsNullOrWhiteSpace($Prefix)) { $name } else { "$Prefix.$name" }
            $paths += $path
            $PathCount.Value += 1
            $paths += Get-JsonShapePaths -Value $property.Value -Prefix $path -Depth ($Depth + 1) -PathCount $PathCount
        }
        return $paths
    }

    if ($Value -is [System.Collections.IEnumerable] -and -not ($Value -is [string])) {
        $arrayPrefix = if ([string]::IsNullOrWhiteSpace($Prefix)) { "[]" } else { "$Prefix[]" }
        foreach ($item in $Value) {
            $paths += Get-JsonShapePaths -Value $item -Prefix $arrayPrefix -Depth ($Depth + 1) -PathCount $PathCount
            if ($PathCount.Value -ge $MaxShapePaths) { break }
        }
    }
    return $paths
}

$uri = [System.Uri]$ApiUri
if ($uri.Scheme -ne "https" -or $uri.Host -ne $AllowedHost -or $uri.AbsolutePath -ne "/api/progetti.json") {
    throw "Configured OpenCoesione API metadata URI is outside the frozen route."
}

$handler = [System.Net.Http.HttpClientHandler]::new()
$handler.AllowAutoRedirect = $false
$handler.AutomaticDecompression = [System.Net.DecompressionMethods]::GZip -bor [System.Net.DecompressionMethods]::Deflate
$client = [System.Net.Http.HttpClient]::new($handler)
$client.Timeout = [TimeSpan]::FromSeconds(45)
$request = [System.Net.Http.HttpRequestMessage]::new([System.Net.Http.HttpMethod]::new("OPTIONS"), $uri)
$request.Headers.Accept.ParseAdd("application/json")
$request.Headers.UserAgent.ParseAdd("ProcRun-source-research/1.0")
$response = $null
$stream = $null
$memory = $null

try {
    # Metadata-only HTTP request. This script never issues GET and never asks for a project id.
    $response = $client.SendAsync(
        $request,
        [System.Net.Http.HttpCompletionOption]::ResponseHeadersRead
    ).GetAwaiter().GetResult()

    $statusCode = [int]$response.StatusCode
    $location = $response.Headers.Location
    if ($statusCode -ge 300 -and $statusCode -lt 400) {
        $locationText = if ($null -eq $location) { "<missing>" } else { [string]$location }
        throw "OpenCoesione OPTIONS metadata route redirected to '$locationText'; redirects are disabled."
    }
    if (-not $response.IsSuccessStatusCode) {
        throw "OpenCoesione OPTIONS metadata route returned HTTP $statusCode."
    }

    $contentType = if ($null -eq $response.Content.Headers.ContentType) { "" } else { [string]$response.Content.Headers.ContentType }
    if ($contentType -notmatch "(?i)^application/(?:[a-z0-9.+-]*\+)?json(?:\s*;|$)") {
        throw "OpenCoesione OPTIONS returned unexpected content type '$contentType'."
    }

    $declaredLength = $response.Content.Headers.ContentLength
    if ($null -ne $declaredLength -and $declaredLength -gt $MaxBodyBytes) {
        throw "OpenCoesione OPTIONS metadata body exceeds the 128 KiB safety bound."
    }

    $stream = $response.Content.ReadAsStreamAsync().GetAwaiter().GetResult()
    $memory = [System.IO.MemoryStream]::new()
    $buffer = New-Object byte[] 8192
    $total = 0
    while (($read = $stream.Read($buffer, 0, $buffer.Length)) -gt 0) {
        $total += $read
        if ($total -gt $MaxBodyBytes) {
            throw "OpenCoesione OPTIONS metadata body exceeded the 128 KiB safety bound while reading."
        }
        $memory.Write($buffer, 0, $read)
    }

    $bodyBytes = $memory.ToArray()
    $bodyText = [System.Text.Encoding]::UTF8.GetString($bodyBytes)
    try {
        $metadata = $bodyText | ConvertFrom-Json
    }
    catch {
        throw "OpenCoesione OPTIONS metadata body was not valid JSON."
    }

    $pathCount = 0
    $shapePaths = @(Get-JsonShapePaths -Value $metadata -PathCount ([ref]$pathCount) | Sort-Object -Unique)
    if ($pathCount -ge $MaxShapePaths) {
        throw "OpenCoesione OPTIONS metadata shape exceeded the bounded path limit; failing closed."
    }

    $projectionPattern = '(?i)(^|\.)(fields?|select|projection|include|exclude|omit|serializer|output|columns?)(\.|\[\]|$)'
    $filterPattern = '(?i)(^|\.)(filters?|search|ordering|page|limit|offset|tema|natura|territorio|programma|ciclo)(\.|\[\]|$)'
    $identityPattern = '(?i)(soggett|beneficiar|codice_fiscale|codicefiscale|fiscal|tax|email|telefono|phone|contact|fornitor|aggiudicat|supplier|persona)'

    $projectionPaths = @($shapePaths | Where-Object { $_ -match $projectionPattern })
    $filterPaths = @($shapePaths | Where-Object { $_ -match $filterPattern })
    $identityPaths = @($shapePaths | Where-Object { $_ -match $identityPattern })
    $allowHeader = @($response.Headers.Allow | ForEach-Object { [string]$_ })

    [ordered]@{
        probe_contract = "opencoesione-api-options-metadata-v1"
        endpoint = $ApiUri
        method = "OPTIONS"
        http_status = $statusCode
        response_content_type = $contentType
        response_length_bytes = $bodyBytes.Length
        redirects_followed = $false
        project_list_get_called = $false
        project_detail_called = $false
        response_body_logged = $false
        allowed_methods = $allowHeader
        metadata_shape_path_count = $shapePaths.Count
        metadata_shape_paths = $shapePaths
        projection_candidate_paths = $projectionPaths
        filter_candidate_paths = $filterPaths
        identity_candidate_paths = $identityPaths
    } | ConvertTo-Json -Depth 8
}
finally {
    if ($null -ne $memory) { $memory.Dispose() }
    if ($null -ne $stream) { $stream.Dispose() }
    if ($null -ne $response) { $response.Dispose() }
    $request.Dispose()
    $client.Dispose()
    $handler.Dispose()
}
