param(
    [string]$Lafhvst = "",
    [string]$Python = ""
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

if (-not $Lafhvst) { $Lafhvst = Join-Path (Split-Path -Parent $root) "LAFhvst" }
$Lafhvst = (Resolve-Path -LiteralPath $Lafhvst).Path
if (-not (Test-Path (Join-Path $Lafhvst "core\database.py"))) {
    throw "LAFhvst core not found: $Lafhvst"
}

if (-not $Python) {
    $candidate = Join-Path $Lafhvst ".venv\Scripts\python.exe"
    if (Test-Path $candidate) { $Python = $candidate } else { $Python = "python" }
}

Write-Host "==> LAFhvst : $Lafhvst"
Write-Host "==> Python  : $Python"

Write-Host "==> Installing PyInstaller"
& $Python -m pip install --upgrade pyinstaller
if ($LASTEXITCODE -ne 0) { throw "pip install failed ($LASTEXITCODE)" }

Write-Host "==> Cleaning"
foreach ($dir in @("build", "dist")) {
    if (Test-Path $dir) { Remove-Item $dir -Recurse -Force }
}

$env:HVST_IMPORT_LAFHVST = $Lafhvst
Write-Host "==> Building (onefile)"
& $Python -m PyInstaller --noconfirm --clean "hvst_import\hvst_import.spec" --distpath "dist" --workpath "build"
if ($LASTEXITCODE -ne 0) { throw "PyInstaller failed ($LASTEXITCODE)" }

$exe = Join-Path $root "dist\hvst_import.exe"
if (-not (Test-Path $exe)) { throw "Build output missing: $exe" }
Write-Host "==> Done: $exe"
