# Setup script for Python virtual environment and package installation on Windows PowerShell
# Usage: .\setup.ps1
#        Setup-PyEnv colorama rich

function Setup-PyEnv {
    param(
        [Parameter(Mandatory=$true, Position=0)]
        [string[]]$Packages
    )
    
    $VenvDir = "$env:USERPROFILE\venvs\testenv"
    
    # 1. Create the virtual environment if it doesn't exist
    if (-not (Test-Path $VenvDir)) {
        Write-Host "Creating virtual environment at $VenvDir"
        python -m venv $VenvDir
    }
    
    # 2. Activate the virtual environment
    & "$VenvDir\Scripts\Activate.ps1"
    
    # 3. Install all packages passed as arguments
    Write-Host "Installing packages: $($Packages -join ', ')"
    pip install @Packages
    
    # 4. Export current dependencies to requirements.txt
    Write-Host "Exporting dependencies to requirements.txt"
    pip freeze | Out-File -FilePath "requirements.txt" -Encoding UTF8
    
    Write-Host "Environment setup complete. Virtual env: $VenvDir"
}

# Display usage information
Write-Host ""
Write-Host "Windows PowerShell Setup Script"
Write-Host "================================"
Write-Host ""
Write-Host "To set up the environment, run:"
Write-Host "  Setup-PyEnv colorama rich"
Write-Host ""
Write-Host "This will:"
Write-Host "  1. Create a virtual environment at $env:USERPROFILE\venvs\testenv"
Write-Host "  2. Activate the virtual environment"
Write-Host "  3. Install the specified packages"
Write-Host "  4. Export dependencies to requirements.txt"
Write-Host ""

# Example usage - uncomment to run automatically
# Setup-PyEnv colorama rich
