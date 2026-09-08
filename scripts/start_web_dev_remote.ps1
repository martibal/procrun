param(
    [string]$Server = "62.238.117.62",
    [string]$SshUser = "root",
    [int]$LocalDbPort = 55432,
    [string]$DbName = "procrun",
    [string]$DbUser = "procrun_web_dev"
)

$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSScriptRoot
$WebDir = Join-Path $RepoRoot "web"
$SshKey = Join-Path $env:USERPROFILE ".ssh\procrun_hetzner"

if (-not (Test-Path $SshKey)) {
    throw "Missing SSH key: $SshKey"
}

if (-not (Test-Path (Join-Path $WebDir "package.json"))) {
    throw "Could not find the ProcRun web directory at $WebDir"
}

function Test-LocalPort([int]$Port) {
    $client = [System.Net.Sockets.TcpClient]::new()
    try {
        $task = $client.ConnectAsync("127.0.0.1", $Port)
        if (-not $task.Wait(250)) {
            return $false
        }
        return $client.Connected
    }
    catch {
        return $false
    }
    finally {
        $client.Dispose()
    }
}

if (Test-LocalPort $LocalDbPort) {
    throw "Local port $LocalDbPort is already in use. Close the existing tunnel/process or choose another -LocalDbPort."
}

$sshArgs = @(
    "-i", $SshKey,
    "-N",
    "-T",
    "-o", "ExitOnForwardFailure=yes",
    "-o", "ServerAliveInterval=30",
    "-o", "ServerAliveCountMax=3",
    "-L", "127.0.0.1:${LocalDbPort}:127.0.0.1:5432",
    "${SshUser}@${Server}"
)

Write-Host "Opening encrypted SSH tunnel to the central ProcRun PostgreSQL instance..."
$sshProcess = Start-Process -FilePath "ssh" -ArgumentList $sshArgs -NoNewWindow -PassThru

try {
    $ready = $false
    for ($i = 0; $i -lt 40; $i++) {
        if ($sshProcess.HasExited) {
            throw "SSH tunnel exited before PostgreSQL became reachable."
        }
        if (Test-LocalPort $LocalDbPort) {
            $ready = $true
            break
        }
        Start-Sleep -Milliseconds 250
    }

    if (-not $ready) {
        throw "SSH tunnel did not become ready on 127.0.0.1:$LocalDbPort."
    }

    $plainPassword = $env:PROCRUN_DEV_DB_PASSWORD
    $securePassword = $null

    if ([string]::IsNullOrWhiteSpace($plainPassword)) {
        $securePassword = Read-Host "Password for PostgreSQL role $DbUser" -AsSecureString
        $plainPassword = [System.Net.NetworkCredential]::new("", $securePassword).Password
    }

    if ([string]::IsNullOrWhiteSpace($plainPassword)) {
        throw "Database password cannot be empty."
    }

    $encodedPassword = [System.Uri]::EscapeDataString($plainPassword)
    $previousDatabaseUrl = $env:PROCRUN_DATABASE_URL
    $env:PROCRUN_DATABASE_URL = "postgresql://${DbUser}:${encodedPassword}@127.0.0.1:${LocalDbPort}/${DbName}"

    try {
        Write-Host "Central database connected through SSH. Starting Next.js locally..."
        Push-Location $WebDir
        try {
            npm run dev
        }
        finally {
            Pop-Location
        }
    }
    finally {
        if ($null -eq $previousDatabaseUrl) {
            Remove-Item Env:PROCRUN_DATABASE_URL -ErrorAction SilentlyContinue
        }
        else {
            $env:PROCRUN_DATABASE_URL = $previousDatabaseUrl
        }
        $plainPassword = $null
        $encodedPassword = $null
        if ($securePassword) {
            $securePassword.Dispose()
        }
    }
}
finally {
    if ($sshProcess -and -not $sshProcess.HasExited) {
        Stop-Process -Id $sshProcess.Id -Force
    }
}
