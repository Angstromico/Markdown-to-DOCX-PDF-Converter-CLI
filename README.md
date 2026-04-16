# Markdown to DOCX/PDF Converter CLI

A powerful command-line tool for converting Markdown files to DOCX and PDF formats using Pandoc. This tool provides a clean, modular interface with colored terminal output and comprehensive error handling.

## What the App Does

The `md-converter-cli` is a Python command-line application that:

- Converts Markdown files (.md) to Microsoft Word documents (.docx)
- Converts Markdown files (.md) to Portable Document Format (.pdf)
- Supports batch conversion to both formats simultaneously
- Provides intelligent PDF engine detection (wkhtmltopdf > pdflatex)
- Offers colored terminal output for better user experience
- Includes comprehensive dependency checking and helpful installation instructions
- Validates input files and creates output directories automatically
- Handles errors gracefully with informative messages

## Folder Structure

```
md-converter-cli/
|-- main.py              # Main CLI entry point and argument parsing
|-- converter.py         # Core conversion logic using Pandoc
|-- utils.py             # Utility functions for validation and helpers
|-- batch_converter.py   # Batch conversion with image processing
|-- requirements.txt     # Python dependencies
|-- setup.sh            # Virtual environment setup script (Linux/macOS)
|-- setup.bat           # Virtual environment setup script (Windows Command Prompt)
|-- setup.ps1           # Virtual environment setup script (Windows PowerShell)
|-- Dockerfile          # Docker container definition
|-- docker-compose.yml   # Docker Compose configuration
|-- docker-compose-batch.yml # Batch conversion Docker configuration
|-- DOCKER.md          # Docker-specific documentation
|-- BATCH_DOCKER.md     # Batch conversion documentation
|-- .gitignore          # Git ignore patterns
|-- README.md           # This documentation
|-- example.md          # Example Markdown file for testing
|-- markdown/           # Directory for batch input files
|-- images/             # Directory for image files
|-- dist/               # Output directory for converted files
```

## Installation Instructions

### Prerequisites

- Python 3.11 or higher
- Pandoc (universal document converter)
- PDF engine (wkhtmltopdf recommended, or pdflatex as fallback)

### Step 1: Install Pandoc

Pandoc is the core engine that powers all conversions.

#### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install pandoc
```

#### macOS
```bash
brew install pandoc
```

#### Windows
1. Download the installer from [https://pandoc.org/installing.html](https://pandoc.org/installing.html)
2. Run the installer and follow the setup wizard
3. Restart your terminal or command prompt

#### Verify Installation
```bash
pandoc --version
```

### Step 2: Install PDF Engine

You need at least one PDF engine for PDF conversion.

#### Option 1: wkhtmltopdf (Recommended)

**Ubuntu/Debian:**
```bash
sudo apt-get install wkhtmltopdf
```

**macOS:**
```bash
brew install wkhtmltopdf
```

**Windows:**
1. Download from [https://wkhtmltopdf.org/](https://wkhtmltopdf.org/)
2. Run the installer
3. Add to PATH if not done automatically

#### Option 2: pdflatex (Alternative)

**Ubuntu/Debian:**
```bash
sudo apt-get install texlive-latex-extra
```

**macOS:**
```bash
brew install --cask mactex
```

**Windows:**
1. Download from [https://www.tug.org/texlive/](https://www.tug.org/texlive/)
2. Install the full TeX Live distribution

### Step 3: Setup Python Virtual Environment

#### Windows

**Option 1: Using the Windows Setup Scripts (Recommended)**

The project includes two Windows-specific setup scripts:

- `setup.bat` for Windows Command Prompt (cmd.exe)
- `setup.ps1` for Windows PowerShell

**Using Command Prompt:**
```batch
# Run the setup script
call setup_pyenv colorama rich
```

**Using PowerShell:**
```powershell
# First, you may need to allow script execution:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then run the setup function
Setup-PyEnv colorama rich
```

**What this does:**
- Creates a virtual environment at `%USERPROFILE%\venvs\testenv`
- Activates the virtual environment automatically
- Installs the specified packages (`colorama` for terminal colors, `rich` for enhanced output)
- Generates a clean `requirements.txt` with just the project dependencies
- Ensures the environment is reproducible and isolated

**Option 2: Manual Windows Setup**

```batch
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### Linux/macOS

**Option 1: Using the Setup Script (Recommended)**

The `setup.sh` script provides a convenient way to set up a Python virtual environment and install dependencies. It includes a `setup_pyenv()` function that:

1. **Creates a virtual environment** at `~/venvs/testenv` if it doesn't exist
2. **Activates the virtual environment** automatically
3. **Installs specified packages** passed as arguments
4. **Exports dependencies** to `requirements.txt` for reproducibility

**Usage:**
```bash
# Source the setup script to load the function
source setup.sh

# Install the required packages for this project
setup_pyenv colorama rich
```

**What this does:**
- Creates and activates a clean Python virtual environment
- Installs only the packages you specify (`colorama` for terminal colors, `rich` for enhanced output)
- Generates a clean `requirements.txt` with just the project dependencies
- Ensures the environment is reproducible and isolated

**Note:** The `setup_pyenv` function will overwrite your `requirements.txt` with the current environment state. For this project, we've already cleaned up the requirements.txt to include only the necessary dependencies.

**Option 2: Manual Setup**

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Quick Start for Windows

1. **Install Python 3.11+** from [python.org](https://www.python.org/downloads/)
2. **Install Pandoc** from [pandoc.org](https://pandoc.org/installing.html)
3. **Install wkhtmltopdf** from [wkhtmltopdf.org](https://wkhtmltopdf.org/)
4. **Set up the environment:**
   ```batch
   # Using Command Prompt
   call setup_pyenv colorama rich
   ```
   ```powershell
   # Using PowerShell
   Setup-PyEnv colorama rich
   ```
5. **Convert your first file:**
   ```batch
   python main.py example.md
   ```

## Image Formatting for PDF and Word Output

For images to appear correctly in PDF and Word output, they must use Markdown image syntax instead of HTML `<img>` tags. This ensures proper rendering by Pandoc.

### Correct Image Format

Use this format for images in your Markdown files:

```markdown
<p align="center">
  ![Image Description](./images/your-image.png){width=300px}
</p>
```

### Incorrect Format (Will not work in PDF/Word)

Avoid HTML `<img>` tags:

```markdown
<img src="./images/your-image.png" alt="Image Description" width="300"/>
```

### Image Format Examples

**Basic centered image:**
```markdown
<p align="center">
  ![Screenshot](./images/screenshot.png){width=500px}
</p>
```

**Image with specific width:**
```markdown
<p align="center">
  ![Logo](./images/logo.png){width=200px}
</p>
```

**Multiple images:**
```markdown
<p align="center">
  ![First Image](./images/image1.png){width=400px}
</p>

<p align="center">
  ![Second Image](./images/image2.jpg){width=300px}
</p>
```

### Important Notes

- **Use Markdown syntax**: `![alt text](path){width=Xpx}` instead of `<img>` tags
- **Center with HTML**: Wrap in `<p align="center">` for centering
- **Specify width**: Use `{width=Xpx}` for consistent sizing
- **Relative paths**: Use relative paths like `./images/` for Docker compatibility
- **File extensions**: Use common formats (.png, .jpg, .jpeg, .gif)

### Why This Matters

Pandoc processes Markdown images differently than HTML tags. Using the proper Markdown syntax ensures:
- Images appear correctly in both PDF and Word output
- Consistent rendering across different conversion engines
- Proper image sizing and positioning
- Docker compatibility with relative paths

## Usage Examples

### Basic Usage

Convert a Markdown file to both DOCX and PDF (default behavior):
```bash
python main.py input.md
```

### Format-Specific Conversion

Generate only DOCX:
```bash
python main.py input.md --docx
```

Generate only PDF:
```bash
python main.py input.md --pdf
```

Generate both formats explicitly:
```bash
python main.py input.md --docx --pdf
```

### Custom Output Directory

Specify a custom output directory:
```bash
python main.py input.md --output ./my-output
```

Combine format flags with custom output:
```bash
python main.py input.md --docx --pdf --output ./documents
```

### Command Line Options

- `input_file`: Path to the input Markdown file (required)
- `--docx`: Generate DOCX output file
- `--pdf`: Generate PDF output file
- `--output`, `-o`: Output directory for converted files (default: ./dist)

## Example Output

### Successful Conversion
```
✓ Input file validated: /home/user/documents/example.md
✓ Pandoc is installed
✓ Available PDF engines: wkhtmltopdf
ℹ No format specified, generating both DOCX and PDF
→ Converting to DOCX: /home/user/documents/dist/example.docx
✓ DOCX file created: /home/user/documents/dist/example.docx
→ Converting to PDF: /home/user/documents/dist/example.pdf
✓ PDF file created: /home/user/documents/dist/example.pdf (using wkhtmltopdf)
✓ Conversion completed successfully!
```

### Missing Dependencies
```
✗ Pandoc is not installed!

To install Pandoc:
  • Ubuntu/Debian: sudo apt-get install pandoc
  • macOS: brew install pandoc
  • Windows: Download from https://pandoc.org/installing.html
```

## Troubleshooting

### Common Issues

#### 1. "Pandoc is not installed"
**Solution:** Install Pandoc following the instructions in Step 1 above.

#### 2. "No PDF engine found"
**Solution:** Install either wkhtmltopdf or pdflatex following the instructions in Step 2.

#### 3. "Input file does not exist"
**Solution:** Ensure the file path is correct and the file exists. Use absolute paths if needed.

#### 4. "Input file must have .md extension"
**Solution:** Rename your file to have a .md extension or convert it to Markdown format first.

#### 5. "Permission denied" when creating output directory
**Solution:** Check directory permissions or choose a different output directory you have write access to.

#### 6. PDF conversion fails with LaTeX errors
**Solution:** Try installing wkhtmltopdf instead of pdflatex, or check your Markdown for complex LaTeX syntax that might not be supported.

### Debug Mode

For detailed error information, you can run the script with Python's verbose mode:
```bash
python -v main.py input.md
```

### Log Files

The application doesn't create persistent log files, but you can redirect output to a file for debugging:
```bash
python main.py input.md 2>&1 | tee conversion.log
```

## Advanced Usage

### Batch Processing

While the tool processes one file at a time, you can easily batch process multiple files using shell loops:

#### Linux/macOS
```bash
for file in *.md; do
    python main.py "$file" --output ./batch-output
done
```

#### Windows (Command Prompt)
```batch
for %f in (*.md) do python main.py "%f" --output ./batch-output
```

#### Windows (PowerShell)
```powershell
Get-ChildItem *.md | ForEach-Object {
    python main.py $_.Name --output ./batch-output
}
```

### Integration with Other Tools

The tool can be easily integrated into build scripts, CI/CD pipelines, or other automation tools:

#### Makefile Example
```makefile
.PHONY: convert-docs
convert-docs:
	python main.py README.md --docx --pdf --output ./docs
```

#### GitHub Actions Example
```yaml
- name: Convert documentation
  run: |
    python main.py README.md --docx --pdf --output ./docs
```

## Docker Support

For consistent Linux-style output across all operating systems, you can use Docker to run the converter in a containerized environment.

### Quick Start with Docker

1. **Build the Docker image:**
   ```bash
   docker build -t md-converter-cli .
   ```

2. **Convert with default file (RFC-Updating-Page.md):**
   ```bash
   docker-compose up md-converter
   ```

3. **Convert with custom file:**
   ```bash
   # PowerShell
   $env:INPUT_FILE="./your-file.md"; docker-compose up md-converter
   
   # Command Prompt
   set INPUT_FILE=./your-file.md && docker-compose up md-converter
   
   # Or create .env file with: INPUT_FILE=./your-file.md
   ```

### Docker Benefits

- **Consistent Output**: Get Linux-style PDF rendering regardless of host OS
- **No Local Dependencies**: Skip installing Pandoc, LaTeX, or wkhtmltopdf
- **Isolated Environment**: Clean, reproducible conversions
- **Cross-Platform**: Works same on Windows, macOS, and Linux

### Docker Configuration

The `docker-compose.yml` uses environment variable `${INPUT_FILE:-./RFC-Updating-Page.md}` to:
- Use specified file if `INPUT_FILE` environment variable is set
- Fall back to `RFC-Updating-Page.md` if not specified
- Always output to `dist/input.pdf` and `dist/input.docx`

For detailed Docker documentation, see [DOCKER.md](DOCKER.md).

## Batch Conversion with Docker

For converting multiple markdown files with automatic image handling, use the batch conversion system:

### Quick Start

1. **Prepare your files:**
   ```bash
   mkdir -p markdown images
   # Copy your .md files to markdown/
   # Copy your images to images/
   ```

2. **Run batch conversion:**
   ```bash
   docker-compose -f docker-compose-batch.yml up batch-converter
   ```

3. **Check results:**
   ```bash
   ls -la dist/
   ```

### Features

- **Mass Processing**: Converts all `.md` files in `markdown/` directory
- **Automatic Image Handling**: Detects and processes images from `images/` directory
- **Temporary Management**: Copies images to container, modifies paths, cleans up automatically
- **Linux Consistency**: Same professional output regardless of host OS

### Usage Examples

```bash
# Convert all files (DOCX + PDF)
docker-compose -f docker-compose-batch.yml up batch-converter

# DOCX only
docker-compose -f docker-compose-batch.yml run --rm batch-converter python batch_converter.py --no-pdf

# PDF only
docker-compose -f docker-compose-batch.yml run --rm batch-converter python batch_converter.py --no-docx
```

### Directory Structure

```
project/
|-- markdown/          # Input markdown files
|-- images/           # Image files
|-- dist/             # Output files (created automatically)
|-- batch_converter.py
|-- docker-compose-batch.yml
`-- BATCH_DOCKER.md   # Detailed batch documentation
```

For complete batch conversion documentation, see [BATCH_DOCKER.md](BATCH_DOCKER.md).

## Future Improvements

Planned features for future versions:

- [x] Batch processing of multiple files in a single command
- [x] Docker containerization for easy deployment
- [ ] Support for additional output formats (HTML, EPUB, etc.)
- [ ] Custom CSS styling for PDF output
- [ ] Template system for DOCX formatting
- [ ] Configuration file support for default settings
- [ ] Progress bars for large file conversions
- [ ] Watch mode for automatic conversion on file changes
- [ ] Integration with popular editors (VS Code, etc.)
- [ ] Web API interface for remote conversions

## Contributing

Contributions are welcome! Please feel free to submit pull requests, report bugs, or suggest new features.

## License

This project is open source and available under the MIT License.

## Support

If you encounter any issues not covered in this documentation, please:

1. Check the troubleshooting section above
2. Verify all dependencies are properly installed
3. Ensure your input file is valid Markdown
4. Test with the provided `example.md` file

For additional support, please open an issue on the project repository.
