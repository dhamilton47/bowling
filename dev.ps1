param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$CommandArgs
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$PythonExe = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
$ManagePy = Join-Path $ProjectRoot "manage.py"

if (-not (Test-Path $PythonExe)) {
    Write-Error ".venv Python interpreter not found at $PythonExe"
    exit 1
}

if (-not $CommandArgs -or $CommandArgs.Count -eq 0) {
    Write-Host "Usage:"
    Write-Host "  .\dev.ps1 <manage.py command> [args]"
    Write-Host "  .\dev.ps1 pip <pip args>"
    Write-Host "  .\dev.ps1 python <python args>"
    Write-Host "Examples:"
    Write-Host "  .\dev.ps1 check"
    Write-Host "  .\dev.ps1 migrate"
    Write-Host "  .\dev.ps1 runserver"
    Write-Host "  .\dev.ps1 pip install django"
    exit 0
}

$mode = $CommandArgs[0].ToLowerInvariant()

if ($mode -eq "pip") {
    $pipArgs = if ($CommandArgs.Count -gt 1) { $CommandArgs[1..($CommandArgs.Count - 1)] } else { @() }
    & $PythonExe -m pip @pipArgs
    exit $LASTEXITCODE
}

if ($mode -eq "python") {
    $pyArgs = if ($CommandArgs.Count -gt 1) { $CommandArgs[1..($CommandArgs.Count - 1)] } else { @() }
    & $PythonExe @pyArgs
    exit $LASTEXITCODE
}

& $PythonExe $ManagePy @CommandArgs
exit $LASTEXITCODE
