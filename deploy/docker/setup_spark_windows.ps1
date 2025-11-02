# ODIBI CORE - Spark Windows Setup Script
# Run with: powershell -ExecutionPolicy Bypass -File setup_spark_windows.ps1

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "ODIBI CORE - Setting up Spark for Windows" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Create Hadoop directory
$hadoopHome = "C:\hadoop"
$hadoopBin = "$hadoopHome\bin"

Write-Host "[1/4] Creating Hadoop directory..." -ForegroundColor Yellow
try {
    New-Item -Path $hadoopBin -ItemType Directory -Force | Out-Null
    Write-Host "  [OK] Created: $hadoopBin" -ForegroundColor Green
} catch {
    Write-Host "  [FAIL] Could not create directory" -ForegroundColor Red
    exit 1
}

# Step 2: Download winutils.exe
Write-Host "[2/4] Downloading winutils.exe..." -ForegroundColor Yellow
$winutilsUrl = "https://github.com/cdarlint/winutils/raw/master/hadoop-3.2.0/bin/winutils.exe"
$winutilsPath = "$hadoopBin\winutils.exe"

try {
    Invoke-WebRequest -Uri $winutilsUrl -OutFile $winutilsPath -UseBasicParsing
    Write-Host "  [OK] Downloaded: $winutilsPath" -ForegroundColor Green
} catch {
    Write-Host "  [FAIL] Download failed" -ForegroundColor Red
    Write-Host ""
    Write-Host "  Manual download:" -ForegroundColor Yellow
    Write-Host "  1. Go to: https://github.com/cdarlint/winutils" -ForegroundColor Yellow
    Write-Host "  2. Download hadoop-3.2.0/bin/winutils.exe" -ForegroundColor Yellow
    Write-Host "  3. Save to: $winutilsPath" -ForegroundColor Yellow
    Write-Host ""
    exit 1
}

# Step 3: Set HADOOP_HOME environment variable
Write-Host "[3/4] Setting HADOOP_HOME environment variable..." -ForegroundColor Yellow

# Set for current session
$env:HADOOP_HOME = $hadoopHome
Write-Host "  [OK] Set for current session" -ForegroundColor Green

# Try to set permanently
try {
    [System.Environment]::SetEnvironmentVariable("HADOOP_HOME", $hadoopHome, "Machine")
    Write-Host "  [OK] Set permanently (system-wide)" -ForegroundColor Green
} catch {
    Write-Host "  [WARN] Could not set permanently (requires admin)" -ForegroundColor Yellow
    Write-Host "  Run PowerShell as Administrator to set permanently" -ForegroundColor Yellow
}

# Step 4: Verify setup
Write-Host "[4/4] Verifying setup..." -ForegroundColor Yellow

$allGood = $true

if (Test-Path $winutilsPath) {
    Write-Host "  [OK] winutils.exe found" -ForegroundColor Green
} else {
    Write-Host "  [FAIL] winutils.exe NOT found!" -ForegroundColor Red
    $allGood = $false
}

if ($env:HADOOP_HOME -eq $hadoopHome) {
    Write-Host "  [OK] HADOOP_HOME set: $env:HADOOP_HOME" -ForegroundColor Green
} else {
    Write-Host "  [FAIL] HADOOP_HOME not set!" -ForegroundColor Red
    $allGood = $false
}

Write-Host ""
Write-Host "======================================================================" -ForegroundColor Cyan

if ($allGood) {
    Write-Host "[SUCCESS] Spark setup complete!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "  1. Restart your terminal (to load HADOOP_HOME)" -ForegroundColor White
    Write-Host "  2. cd d:\projects\odibi_core" -ForegroundColor White
    Write-Host "  3. python -m pytest tests/test_spark_engine.py -v" -ForegroundColor White
    Write-Host "  4. python -m odibi_core.examples.parity_demo" -ForegroundColor White
} else {
    Write-Host "[FAIL] Setup incomplete" -ForegroundColor Red
    Write-Host "Please fix the errors above and try again" -ForegroundColor Yellow
}

Write-Host "======================================================================" -ForegroundColor Cyan
