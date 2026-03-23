@echo off
REM Quick test script for KiCAD-to-Lcapy converter

echo ============================================================
echo KiCAD-to-Lcapy Converter - Quick Test
echo ============================================================
echo.

REM Change to lcapy directory
cd /d "%~dp0lcapy"

echo Current directory: %cd%
echo.

REM Check if test file exists
if not exist "lcapy\tests\test_kicad.sch" (
    echo ERROR: Test file not found at lcapy\tests\test_kicad.sch
    echo Please run this script from the repository root
    pause
    exit /b 1
)

echo Running unit tests...
echo ============================================================
python -m pytest lcapy\tests\test_kicad_converter.py -v --tb=short
if errorlevel 1 (
    echo.
    echo Tests failed! Check output above for details.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo Running CLI test...
echo ============================================================
python -m lcapy.scripts.kicad_converter lcapy\tests\test_kicad.sch --show-netlist
if errorlevel 1 (
    echo.
    echo CLI test failed!
    pause
    exit /b 1
)

echo.
echo ============================================================
echo ALL TESTS PASSED!
echo ============================================================
echo.
echo Generated files:
dir /b test_kicad*.* 2>nul
echo.
echo Next steps:
echo 1. Check the generated netlist files
echo 2. View the SVG/PDF diagrams
echo 3. Run with your own KiCAD files:
echo    python -m lcapy.scripts.kicad_converter your_circuit.kicad_sch
echo.
pause
