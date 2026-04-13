# Windows Setup Guide

This guide provides step-by-step instructions for setting up the Markdown to DOCX/PDF Converter CLI on Windows.

## Prerequisites

- Windows 10 or later
- Administrator privileges (for installing some dependencies)

## Step 1: Install Python

1. Download Python 3.11 or higher from [python.org](https://www.python.org/downloads/)
2. Run the installer
3. **Important:** Check the box that says "Add Python to PATH"
4. Complete the installation

**Verify installation:**
```cmd
python --version
```

## Step 2: Install Pandoc

1. Download the Windows installer from [pandoc.org](https://pandoc.org/installing.html)
2. Run the installer
3. Follow the setup wizard
4. Restart your command prompt or PowerShell

**Verify installation:**
```cmd
pandoc --version
```

## Step 3: Install PDF Engine

Choose one of the following options:

### Option A: wkhtmltopdf (Recommended)

1. Download from [wkhtmltopdf.org](https://wkhtmltopdf.org/downloads.html)
2. Run the installer
3. Make sure it's added to your PATH during installation

### Option B: MiKTeX (LaTeX)

1. Download from [miktex.org](https://miktex.org/download)
2. Run the installer
3. Choose the complete installation

## Step 4: Set Up the Project

### Option 1: Using Windows Setup Scripts (Recommended)

#### Using Command Prompt (cmd.exe):

```cmd
# Navigate to the project directory
cd "c:\path\to\Markdown-to-DOCX-PDF-Converter-CLI"

# Run the setup script
call setup_pyenv colorama rich
```

#### Using PowerShell:

```powershell
# Navigate to the project directory
cd "c:\path\to\Markdown-to-DOCX-PDF-Converter-CLI"

# Allow script execution (if needed)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Run the setup function
Setup-PyEnv colorama rich
```

### Option 2: Manual Setup

```cmd
# Navigate to the project directory
cd "c:\path\to\Markdown-to-DOCX-PDF-Converter-CLI"

# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Step 5: Test the Installation

```cmd
# Test with the example file
python main.py example.md
```

You should see output like:
```
+ Input file validated: C:\path\to\example.md
i No format specified, generating both DOCX and PDF
+ Pandoc is installed
+ Available PDF engines: wkhtmltopdf
→ Converting to DOCX: C:\path\to\dist\example.docx
+ DOCX file created: C:\path\to\dist\example.docx
→ Converting to PDF: C:\path\to\dist\example.pdf
+ PDF file created: C:\path\to\dist\example.pdf (using wkhtmltopdf)
+ Conversion completed successfully!
```

## Common Windows Issues and Solutions

### Issue 1: "Python is not recognized"

**Solution:** Reinstall Python and make sure to check "Add Python to PATH" during installation.

### Issue 2: "Pandoc is not recognized"

**Solution:** 
1. Restart your command prompt after installing Pandoc
2. Make sure Pandoc was added to PATH during installation
3. If not, add Pandoc's installation directory to your PATH manually

### Issue 3: PowerShell execution policy error

**Solution:** Run this command in PowerShell:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Issue 4: Virtual environment activation fails

**Solution:** Make sure you're using the correct activation command:
- Command Prompt: `venv\Scripts\activate`
- PowerShell: `venv\Scripts\Activate.ps1`

### Issue 5: Unicode encoding errors

**Solution:** The application has been updated to use ASCII-safe characters for Windows compatibility. If you still encounter issues, try:
```cmd
set PYTHONIOENCODING=utf-8
python main.py example.md
```

## Usage Examples

### Basic Conversion
```cmd
python main.py input.md
```

### Convert to DOCX only
```cmd
python main.py input.md --docx
```

### Convert to PDF only
```cmd
python main.py input.md --pdf
```

### Custom output directory
```cmd
python main.py input.md --output C:\MyDocuments
```

### Batch processing (Command Prompt)
```cmd
for %f in (*.md) do python main.py "%f" --output ./batch-output
```

### Batch processing (PowerShell)
```powershell
Get-ChildItem *.md | ForEach-Object {
    python main.py $_.Name --output ./batch-output
}
```

## Environment Variables (Optional)

You can set these environment variables to customize the behavior:

```cmd
# Set default output directory
set MD_CONVERTER_OUTPUT=C:\MyDocuments

# Set preferred PDF engine
set MD_CONVERTER_PDF_ENGINE=wkhtmltopdf
```

## Support

If you encounter any issues:

1. Check that all prerequisites are installed correctly
2. Verify that the tools are in your PATH
3. Test with the provided `example.md` file
4. Check the main README.md for additional troubleshooting

For additional support, please open an issue on the project repository.
