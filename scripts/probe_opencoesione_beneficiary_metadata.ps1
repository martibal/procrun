[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"

$MetadataUri = "https://opencoesione.gov.it/media/opendata/metadati_beneficiari.xls"
$AllowedHost = "opencoesione.gov.it"
$MaxMetadataBytes = 512KB
$OutputDirectory = Join-Path (Get-Location) "data\downloads\research"
$OutputPath = Join-Path $OutputDirectory "opencoesione_beneficiary_metadata.xls"
$TempPath = Join-Path ([System.IO.Path]::GetTempPath()) (
    "procrun-opencoesione-beneficiary-metadata-" + [guid]::NewGuid().ToString("N") + ".xls"
)

function Get-Sha256HexFromFile {
    param([Parameter(Mandatory = $true)][string]$Path)

    $stream = [System.IO.File]::OpenRead($Path)
    $sha = [System.Security.Cryptography.SHA256]::Create()
    try {
        return ([System.BitConverter]::ToString($sha.ComputeHash($stream))).Replace("-", "").ToLowerInvariant()
    }
    finally {
        $sha.Dispose()
        $stream.Dispose()
    }
}

try {
    $uri = [System.Uri]$MetadataUri
    if ($uri.Scheme -ne "https" -or $uri.Host -ne $AllowedHost) {
        throw "Configured OpenCoesione beneficiary metadata URI is outside the approved origin."
    }

    # Research-only metadata retrieval. This exact XLS metadata resource is the only network body
    # this probe may receive. Redirects are disabled so the request cannot silently leave the
    # approved host or change to a project/beneficiary data distribution.
    $response = Invoke-WebRequest `
        -Uri $MetadataUri `
        -Method Get `
        -Headers @{
            "User-Agent" = "ProcRun-source-research/1.0"
            "Accept" = "application/vnd.ms-excel,application/octet-stream;q=0.9"
        } `
        -OutFile $TempPath `
        -PassThru `
        -UseBasicParsing `
        -MaximumRedirection 0 `
        -TimeoutSec 45

    $contentType = [string]$response.Headers["Content-Type"]
    if ($contentType -notmatch "(?i)(application/vnd\.ms-excel|application/octet-stream)") {
        throw "OpenCoesione beneficiary metadata returned unexpected content type '$contentType'."
    }

    $fileInfo = [System.IO.FileInfo]::new($TempPath)
    if (-not $fileInfo.Exists -or $fileInfo.Length -lt 8) {
        throw "OpenCoesione beneficiary metadata download is empty or truncated."
    }
    if ($fileInfo.Length -gt $MaxMetadataBytes) {
        throw "OpenCoesione beneficiary metadata exceeds the 512 KiB safety bound."
    }

    # Legacy XLS is an OLE Compound File. Refuse HTML/XML/ZIP or any other unexpected body even if
    # the server labels it as an Excel download.
    $stream = [System.IO.File]::OpenRead($TempPath)
    try {
        $magic = New-Object byte[] 8
        $read = $stream.Read($magic, 0, $magic.Length)
    }
    finally {
        $stream.Dispose()
    }
    if ($read -ne 8) {
        throw "OpenCoesione beneficiary metadata could not be signature-validated."
    }

    $expectedMagic = [byte[]](0xD0, 0xCF, 0x11, 0xE0, 0xA1, 0xB1, 0x1A, 0xE1)
    for ($i = 0; $i -lt $expectedMagic.Length; $i += 1) {
        if ($magic[$i] -ne $expectedMagic[$i]) {
            throw "OpenCoesione beneficiary metadata is not a legacy XLS/OLE payload; failing closed."
        }
    }

    New-Item -ItemType Directory -Path $OutputDirectory -Force | Out-Null
    Copy-Item -LiteralPath $TempPath -Destination $OutputPath -Force

    [ordered]@{
        probe_contract = "opencoesione-beneficiary-metadata-only-v1"
        metadata_uri = $MetadataUri
        response_content_type = $contentType
        response_length_bytes = $fileInfo.Length
        response_sha256 = Get-Sha256HexFromFile -Path $TempPath
        metadata_only = $true
        beneficiary_operation_csv_called = $false
        project_api_called = $false
        project_data_called = $false
        redirect_following_allowed = $false
        saved_metadata_path = $OutputPath
        next_action = "Upload this metadata XLS for schema/value-rule review; do not fetch an operations CSV yet."
    } | ConvertTo-Json -Depth 6
}
finally {
    if (Test-Path -LiteralPath $TempPath) {
        Remove-Item -LiteralPath $TempPath -Force
    }
}
