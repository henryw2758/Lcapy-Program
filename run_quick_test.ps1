# KiCAD-to-Lcapy Converter - Quick Test Script (PowerShell)

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "KiCAD-to-Lcapy Converter - Quick Test" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Get script directory and navigate to lcapy
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$lcapyDir = Join-Path $scriptDir "lcapy"

Write-Host "Setting working directory to: $lcapyDir"
Push-Location $lcapyDir

# Check if test file exists
$testFile = "lcapy\tests\test_kicad.sch"
if (-not (Test-Path $testFile)) {
    Write-Host "ERROR: Test file not found at $testFile" -ForegroundColor Red
    Write-Host "Please run this script from the repository root"
    Pop-Location
    exit 1
}

Write-Host "Test file found: $testFile" -ForegroundColor Green
Write-Host ""

# ============================================================
# Test 1: Unit Tests
# ============================================================
Write-Host "============================================================" -ForegroundColor Yellow
Write-Host "Test 1: Running Unit Tests" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Yellow
Write-Host ""

python -m pytest lcapy\tests\test_kicad_converter.py -v --tb=short
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "Unit tests FAILED!" -ForegroundColor Red
    Pop-Location
    exit 1
}

Write-Host ""
Write-Host "Unit tests PASSED!" -ForegroundColor Green
Write-Host ""

# ============================================================
# Test 2: CLI Test - Show Netlist
# ============================================================
Write-Host "============================================================" -ForegroundColor Yellow
Write-Host "Test 2: CLI Test - Generate and Display Netlist" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Yellow
Write-Host ""

python -m lcapy.scripts.kicad_converter lcapy\tests\test_kicad.sch --show-netlist
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "CLI test FAILED!" -ForegroundColor Red
    Pop-Location
    exit 1
}

Write-Host ""
Write-Host "CLI test PASSED!" -ForegroundColor Green
Write-Host ""

# ============================================================
# Test 3: Check Generated Files
# ============================================================
Write-Host "============================================================" -ForegroundColor Yellow
Write-Host "Test 3: Verifying Generated Files" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Yellow
Write-Host ""

$generatedFiles = @(
    "test_kicad_netlist.txt",
    "test_kicad_diagram.svg"
)

$allExists = $true
foreach ($file in $generatedFiles) {
    if (Test-Path $file) {
        $size = (Get-Item $file).Length
        Write-Host "✓ $file ($size bytes)" -ForegroundColor Green
    } else {
        Write-Host "✗ $file NOT FOUND" -ForegroundColor Red
        $allExists = $false
    }
}

if (-not $allExists) {
    Write-Host ""
    Write-Host "Some files were not generated!" -ForegroundColor Red
    Pop-Location
    exit 1
}

Write-Host ""

# ============================================================
# Summary
# ============================================================
Write-Host "============================================================" -ForegroundColor Green
Write-Host "ALL TESTS PASSED! ✓" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""

Write-Host "Summary:" -ForegroundColor Cyan
Write-Host "✓ Unit tests: PASSED (30+ test cases)" -ForegroundColor Green
Write-Host "✓ CLI conversion: PASSED" -ForegroundColor Green
Write-Host "✓ File generation: PASSED" -ForegroundColor Green
Write-Host ""

Write-Host "Generated files:" -ForegroundColor Cyan
Get-Item test_kicad*.* 2>$null | ForEach-Object {
    Write-Host "  - $($_.Name)"
}

Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. View test_kicad_netlist.txt to see generated netlist"
Write-Host "2. Open test_kicad_diagram.svg to see circuit diagram"
Write-Host "3. Run with your own KiCAD files:"
Write-Host "   python -m lcapy.scripts.kicad_converter your_circuit.kicad_sch"
Write-Host "4. See TESTING_GUIDE.md for more test options"
Write-Host ""

Pop-Location
Write-Host "Test complete!" -ForegroundColor Green
