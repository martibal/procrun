[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"

$MetadataUri = "https://opencoesione.gov.it/media/opendata/metadati_database_OC.xlsx"
$AllowedHost = "opencoesione.gov.it"
$MaxWorkbookBytes = 2MB
$MaxProjectRows = 300
$MaxCellChars = 1500
$Headers = @{
    "User-Agent" = "ProcRun-source-research/1.0"
    "Accept" = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,application/octet-stream;q=0.9"
}

Add-Type -AssemblyName System.IO.Compression.FileSystem

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

function Get-ZipEntryText {
    param(
        [Parameter(Mandatory = $true)][System.IO.Compression.ZipArchive]$Archive,
        [Parameter(Mandatory = $true)][string]$EntryName,
        [switch]$Optional
    )

    $entry = $Archive.GetEntry($EntryName)
    if ($null -eq $entry) {
        if ($Optional) {
            return $null
        }
        throw "OpenCoesione metadata workbook is missing required XLSX entry '$EntryName'."
    }
    if ($entry.Length -gt $MaxWorkbookBytes) {
        throw "XLSX entry '$EntryName' exceeds the metadata safety bound."
    }

    $stream = $entry.Open()
    $reader = [System.IO.StreamReader]::new($stream, [System.Text.Encoding]::UTF8, $true)
    try {
        $text = $reader.ReadToEnd()
    }
    finally {
        $reader.Dispose()
        $stream.Dispose()
    }

    if ($text -match "(?i)<!DOCTYPE") {
        throw "XLSX metadata XML contains a DTD declaration; failing closed."
    }
    return $text
}

function ConvertTo-SafeXml {
    param([Parameter(Mandatory = $true)][string]$Text)

    if ($Text -match "(?i)<!DOCTYPE") {
        throw "XLSX metadata XML contains a DTD declaration; failing closed."
    }

    $document = [System.Xml.XmlDocument]::new()
    $document.XmlResolver = $null
    $document.PreserveWhitespace = $false
    $document.LoadXml($Text)
    return $document
}

function Get-SharedStrings {
    param([Parameter(Mandatory = $true)][System.IO.Compression.ZipArchive]$Archive)

    $text = Get-ZipEntryText -Archive $Archive -EntryName "xl/sharedStrings.xml" -Optional
    if ($null -eq $text) {
        return @()
    }

    $document = ConvertTo-SafeXml -Text $text
    $values = @()
    foreach ($item in $document.SelectNodes("//*[local-name()='si']")) {
        $parts = @()
        foreach ($textNode in $item.SelectNodes(".//*[local-name()='t']")) {
            $parts += [string]$textNode.InnerText
        }
        $values += ($parts -join "")
    }
    return $values
}

function Get-CellText {
    param(
        [Parameter(Mandatory = $true)][System.Xml.XmlElement]$Cell,
        [Parameter(Mandatory = $true)][object[]]$SharedStrings
    )

    $type = $Cell.GetAttribute("t")
    if ($type -eq "inlineStr") {
        $parts = @()
        foreach ($textNode in $Cell.SelectNodes(".//*[local-name()='is']//*[local-name()='t']")) {
            $parts += [string]$textNode.InnerText
        }
        $value = $parts -join ""
    }
    else {
        $valueNode = $Cell.SelectSingleNode("./*[local-name()='v']")
        if ($null -eq $valueNode) {
            return ""
        }
        $raw = [string]$valueNode.InnerText
        if ($type -eq "s") {
            $index = 0
            if (-not [int]::TryParse($raw, [ref]$index)) {
                throw "Shared-string cell contained a non-integer index; failing closed."
            }
            if ($index -lt 0 -or $index -ge $SharedStrings.Count) {
                throw "Shared-string cell referenced an out-of-range index; failing closed."
            }
            $value = [string]$SharedStrings[$index]
        }
        else {
            $value = $raw
        }
    }

    $value = [System.Text.RegularExpressions.Regex]::Replace([string]$value, '[\x00-\x1F\x7F]+', ' ')
    $value = [System.Text.RegularExpressions.Regex]::Replace($value, '\s+', ' ').Trim()
    if ($value.Length -gt $MaxCellChars) {
        $value = $value.Substring(0, $MaxCellChars)
    }
    return $value
}

function Resolve-WorkbookEntryName {
    param([Parameter(Mandatory = $true)][string]$Target)

    $normalized = $Target.Replace("\\", "/").Trim()
    if ($normalized.Contains("..")) {
        throw "Workbook relationship contains parent traversal; failing closed."
    }
    if ($normalized.StartsWith("/")) {
        $normalized = $normalized.TrimStart("/")
    }
    elseif (-not $normalized.StartsWith("xl/")) {
        $normalized = "xl/" + $normalized
    }
    return $normalized
}

$tempPath = Join-Path ([System.IO.Path]::GetTempPath()) ("procrun-opencoesione-metadata-" + [guid]::NewGuid().ToString("N") + ".xlsx")
$archive = $null

try {
    $requestedUri = [System.Uri]$MetadataUri
    if ($requestedUri.Scheme -ne "https" -or $requestedUri.Host -ne $AllowedHost) {
        throw "Configured OpenCoesione metadata URI is outside the approved origin."
    }

    # Metadata-only research probe. Redirects are disabled so this exact URI is the only network resource fetched.
    $response = Invoke-WebRequest `
        -Uri $MetadataUri `
        -Method Get `
        -Headers $Headers `
        -OutFile $tempPath `
        -PassThru `
        -MaximumRedirection 0 `
        -UseBasicParsing `
        -TimeoutSec 45

    $contentType = [string]$response.Headers["Content-Type"]
    if ($contentType -notmatch "(?i)(spreadsheetml|octet-stream|application/zip)") {
        throw "OpenCoesione metadata workbook returned unexpected content type '$contentType'."
    }

    $fileInfo = [System.IO.FileInfo]::new($tempPath)
    if (-not $fileInfo.Exists -or $fileInfo.Length -lt 4) {
        throw "OpenCoesione metadata workbook download is empty or truncated."
    }
    if ($fileInfo.Length -gt $MaxWorkbookBytes) {
        throw "OpenCoesione metadata workbook exceeds the 2 MiB safety bound."
    }

    $prefix = [System.IO.File]::ReadAllBytes($tempPath)
    if ($prefix[0] -ne 0x50 -or $prefix[1] -ne 0x4B) {
        throw "OpenCoesione metadata workbook is not an XLSX/ZIP payload."
    }

    $archive = [System.IO.Compression.ZipFile]::OpenRead($tempPath)
    if ($archive.Entries.Count -gt 500) {
        throw "OpenCoesione metadata workbook contains more than 500 ZIP entries; failing closed."
    }

    $sharedStrings = @(Get-SharedStrings -Archive $archive)
    $workbookXml = ConvertTo-SafeXml -Text (Get-ZipEntryText -Archive $archive -EntryName "xl/workbook.xml")
    $relsXml = ConvertTo-SafeXml -Text (Get-ZipEntryText -Archive $archive -EntryName "xl/_rels/workbook.xml.rels")

    $relationshipTargets = @{}
    foreach ($relationship in $relsXml.SelectNodes("//*[local-name()='Relationship']")) {
        $relationshipTargets[[string]$relationship.GetAttribute("Id")] = Resolve-WorkbookEntryName -Target ([string]$relationship.GetAttribute("Target"))
    }

    $sheetDescriptors = @()
    foreach ($sheet in $workbookXml.SelectNodes("//*[local-name()='sheet']")) {
        $relationshipId = $sheet.GetAttribute("id", "http://schemas.openxmlformats.org/officeDocument/2006/relationships")
        if ([string]::IsNullOrWhiteSpace($relationshipId) -or -not $relationshipTargets.ContainsKey($relationshipId)) {
            throw "Workbook sheet is missing a resolvable relationship; failing closed."
        }
        $sheetDescriptors += [ordered]@{
            name = [string]$sheet.GetAttribute("name")
            entry = [string]$relationshipTargets[$relationshipId]
        }
    }

    if ($sheetDescriptors.Count -eq 0 -or $sheetDescriptors.Count -gt 100) {
        throw "OpenCoesione metadata workbook exposed an invalid sheet count; failing closed."
    }

    $projectSheets = @($sheetDescriptors | Where-Object { $_.name -match "(?i)progett" })
    if ($projectSheets.Count -eq 0) {
        throw "OpenCoesione metadata workbook exposed no project-related sheet; failing closed."
    }

    $suspiciousTerms = @(
        "codice_fiscale", "codice fiscale", "cod_fisc", "beneficiario", "beneficiari",
        "soggetto", "soggetti", "cognome", "nome persona", "email", "e-mail", "telefono",
        "partita_iva", "partita iva", "piva", "fornitore", "aggiudicatario", "realizzatore",
        "contraente", "contact", "supplier", "tax id"
    )
    $scopeTerms = @("sintesi", "descrizione", "description", "titolo", "denominazione", "oggetto")

    $projectSheetResults = @()
    $suspiciousHits = @()
    $scopeHits = @()
    $totalProjectRows = 0

    foreach ($descriptor in $projectSheets) {
        $sheetXml = ConvertTo-SafeXml -Text (Get-ZipEntryText -Archive $archive -EntryName $descriptor.entry)
        $rows = @()
        foreach ($rowNode in $sheetXml.SelectNodes("//*[local-name()='sheetData']/*[local-name()='row']")) {
            if ($totalProjectRows -ge $MaxProjectRows) {
                throw "Project metadata exceeded the bounded row limit; failing closed."
            }

            $cells = @()
            $rowValues = @()
            foreach ($cellNode in $rowNode.SelectNodes("./*[local-name()='c']")) {
                $value = Get-CellText -Cell $cellNode -SharedStrings $sharedStrings
                if ([string]::IsNullOrWhiteSpace($value)) {
                    continue
                }
                $cell = [ordered]@{
                    ref = [string]$cellNode.GetAttribute("r")
                    value = $value
                }
                $cells += $cell
                $rowValues += $value
            }

            if ($cells.Count -eq 0) {
                continue
            }

            $totalProjectRows += 1
            $rowNumber = [string]$rowNode.GetAttribute("r")
            $rows += [ordered]@{
                row = $rowNumber
                cells = $cells
            }

            $joined = ($rowValues -join " | ").ToLowerInvariant()
            foreach ($term in $suspiciousTerms) {
                if ($joined.Contains($term.ToLowerInvariant())) {
                    $suspiciousHits += [ordered]@{
                        sheet = $descriptor.name
                        row = $rowNumber
                        term = $term
                        text = ($rowValues -join " | ")
                    }
                }
            }
            foreach ($term in $scopeTerms) {
                if ($joined.Contains($term.ToLowerInvariant())) {
                    $scopeHits += [ordered]@{
                        sheet = $descriptor.name
                        row = $rowNumber
                        term = $term
                        text = ($rowValues -join " | ")
                    }
                }
            }
        }

        $projectSheetResults += [ordered]@{
            name = $descriptor.name
            entry = $descriptor.entry
            nonempty_row_count = $rows.Count
            rows = $rows
        }
    }

    [ordered]@{
        probe_contract = "opencoesione-project-metadata-v1"
        metadata_uri = $MetadataUri
        response_content_type = $contentType
        response_length_bytes = $fileInfo.Length
        response_sha256 = Get-Sha256HexFromFile -Path $tempPath
        metadata_only = $true
        project_data_called = $false
        subject_data_called = $false
        api_project_record_called = $false
        all_sheet_names = @($sheetDescriptors | ForEach-Object { $_.name })
        project_sheet_count = $projectSheets.Count
        project_metadata_row_count = $totalProjectRows
        suspicious_term_hits = $suspiciousHits
        scope_term_hits = $scopeHits
        project_sheets = $projectSheetResults
    } | ConvertTo-Json -Depth 14
}
finally {
    if ($null -ne $archive) {
        $archive.Dispose()
    }
    if (Test-Path -LiteralPath $tempPath) {
        Remove-Item -LiteralPath $tempPath -Force
    }
}
