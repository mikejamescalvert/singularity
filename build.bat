@echo off
echo Building Singularity...
echo.

REM Check if PyInstaller is installed
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo PyInstaller not found. Installing...
    pip install pyinstaller
    echo.
)

REM Build the executable
echo Running PyInstaller...
pyinstaller --clean Singularity.spec

echo.
if exist "dist\Singularity.exe" (
    echo Build successful!
    echo Executable location: dist\Singularity.exe
) else (
    echo Build failed. Check the output above for errors.
)

echo.
pause
