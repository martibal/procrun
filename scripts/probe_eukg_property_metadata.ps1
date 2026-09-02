[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"

# Use only the current public EU Knowledge Graph Wikibase API. The former
# dev.linkedopendata.eu host is intentionally excluded because it no longer
# resolves publicly and must never mask the error from the production host.
$Endpoint = "https://linkedopendata.eu/w/api.php"
$Headers = @{
    "User-Agent" = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36"
    "Accept" = "application/json,text/plain,*/*"
    "Referer" = "https://linkedopendata.eu/wiki/Main_Page"
}

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

function Invoke-PropertyMetadataRequest {
    param(
        [Parameter(Mandatory = $true)][hashtable]$Parameters
    )

    $attemptErrors = @()

    # Try a normal GET first. If the edge/WAF rejects query-string API calls,
    # retry the same read-only Wikibase action as form-encoded POST. Both calls
    # carry exactly the same property-only parameters.
    try {
        $uri = New-QueryUri -BaseUri $Endpoint -Parameters $Parameters
        $response = Invoke-RestMethod -Uri $uri -Method Get -Headers $Headers -TimeoutSec 30
        $script:SuccessfulEndpoint = $Endpoint
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
            -Body $Parameters `
            -TimeoutSec 30
        $script:SuccessfulEndpoint = $Endpoint
        $script:SuccessfulTransport = "POST"
        return $response
    }
    catch {
        $attemptErrors += Format-RequestFailure -Method "POST" -ErrorRecord $_
    }

    $details = $attemptErrors -join " | "
    throw "EUKG property metadata request failed on the public Wikibase API. ${details}"
}

function Get-EnglishMetadataValue {
    param(
        [Parameter(Mandatory = $false)]$Container
    )

    if ($null -eq $Container) {
        return $null
    }
    $property = $Container.PSObject.Properties["en"]
    if ($null -eq $property -or $null -eq $property.Value) {
        return $null
    }
    return $property.Value.value
}

# Only property entities are requested. No Q/item/project entity is ever requested.
$KnownPropertyIds = @(
    "P20",   # candidate start date; must be confirmed
    "P33",   # candidate end date; must be confirmed
    "P32",   # country
    "P35",   # instance/type
    "P127",  # coordinates
    "P474",  # total budget
    "P835",  # EU contribution
    "P836",  # summary
    "P841",  # beneficiary property metadata only; field itself is forbidden in ProcRun data queries
    "P1367", # CCI ID candidate
    "P1584"  # fund
)

$knownResponse = Invoke-PropertyMetadataRequest -Parameters @{
    action = "wbgetentities"
    ids = ($KnownPropertyIds -join "|")
    props = "labels|descriptions"
    languages = "en"
    format = "json"
}

$known = @()
foreach ($entry in ($knownResponse.entities.PSObject.Properties | Sort-Object Name)) {
    $entity = $entry.Value
    $known += [ordered]@{
        id = $entry.Name
        label = Get-EnglishMetadataValue -Container $entity.labels
        description = Get-EnglishMetadataValue -Container $entity.descriptions
    }
}

# Search is explicitly restricted to Wikibase property entities.
$SearchTerms = @(
    "operation identifier",
    "operation code",
    "operation name",
    "start date",
    "end date",
    "programme",
    "programme code",
    "programming period",
    "NUTS",
    "last update"
)

$searches = [ordered]@{}
foreach ($term in $SearchTerms) {
    $response = Invoke-PropertyMetadataRequest -Parameters @{
        action = "wbsearchentities"
        search = $term
        language = "en"
        type = "property"
        limit = "5"
        format = "json"
    }

    $rows = @()
    foreach ($item in @($response.search)) {
        $rows += [ordered]@{
            id = $item.id
            label = $item.label
            description = $item.description
        }
    }
    $searches[$term] = $rows
}

[ordered]@{
    probe_contract = "eukg-property-metadata-only-v2"
    endpoint = $script:SuccessfulEndpoint
    transport = $script:SuccessfulTransport
    known_properties = $known
    property_searches = $searches
} | ConvertTo-Json -Depth 8
