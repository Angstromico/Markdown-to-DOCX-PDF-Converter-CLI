@echo off
REM Setup script for Python virtual environment and package installation on Windows
REM Usage: setup.bat
REM        call setup_pyenv colorama rich

setlocal enabledelayedexpansion

REM Function to setup Python virtual environment
:setup_pyenv
    set "VENV_DIR=%USERPROFILE%\venvs\testenv"

    REM 1. Create the virtual environment if it doesn't exist
    if not exist "!VENV_DIR!" (
        echo Creating virtual environment at !VENV_DIR!
        python -m venv "!VENV_DIR!"
    )

    REM 2. Activate the virtual environment
    call "!VENV_DIR!\Scripts\activate.bat"

    REM 3. Check if user passed packages
    if "%~1"=="" (
        echo Usage: call setup_pyenv package1 [package2] ...
        exit /b 1
    )

    REM 4. Install all packages passed as arguments
    echo Installing packages: %*
    pip install %*

    REM 5. Export current dependencies to requirements.txt
    echo Exporting dependencies to requirements.txt
    pip freeze > requirements.txt

    echo Environment setup complete. Virtual env: !VENV_DIR!
    goto :eof

REM Example usage - uncomment and modify as needed
REM call :setup_pyenv colorama rich

echo.
echo Windows Setup Script
echo ====================
echo.
echo To set up the environment, run:
echo   call setup_pyenv colorama rich
echo.
echo This will:
echo   1. Create a virtual environment at %USERPROFILE%\venvs\testenv
echo   2. Activate the virtual environment
echo   3. Install the specified packages
echo   4. Export dependencies to requirements.txt
echo.
