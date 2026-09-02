[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"

$Endpoints = @(
    "https://linkedopendata.eu/w/api.php",
    "https://dev.linkedopendata.eu/w/api.php"
)
$Headers = @{
    "User-Agent" = "ProcRun-Research/1.0 (property-metadata-only)"
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

function Invoke-PropertyMetadataRequest {
    param(
        [Parameter(Mandatory = $true)][hashtable]$Parameters
    )

    $lastError = $null
    foreach ($endpoint in $Endpoints) {
        try {
            $uri = New-QueryUri -BaseUri $endpoint -Parameters $Parameters
            $response = Invoke-RestMethod -Uri $uri -Method Get -Headers $Headers -TimeoutSec 30
            $script:SuccessfulEndpoint = $endpoint
            return $response
        }
        catch {
            $lastError = $_
        }
    }

    throw "EUKG property metadata request failed on all approved metadata endpoints: $($lastError.Exception.Message)"
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
    probe_contract = "eukg-property-metadata-only-v1"
    endpoint = $script:SuccessfulEndpoint
    known_properties = $known
    property_searches = $searches
} | ConvertTo-Json -Depth 8
