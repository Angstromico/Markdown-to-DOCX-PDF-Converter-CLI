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
├── main.py              # Main CLI entry point and argument parsing
├── converter.py         # Core conversion logic using Pandoc
├── utils.py             # Utility functions for validation and helpers
├── requirements.txt     # Python dependencies
├── setup.sh            # Virtual environment setup script
├── .gitignore          # Git ignore patterns
├── README.md           # This documentation
└── example.md          # Example Markdown file for testing
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

#### Method 1: Using the Setup Script (Recommended)

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

#### Method 2: Manual Setup

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

## Future Improvements

Planned features for future versions:

- [ ] Batch processing of multiple files in a single command
- [ ] Support for additional output formats (HTML, EPUB, etc.)
- [ ] Custom CSS styling for PDF output
- [ ] Template system for DOCX formatting
- [ ] Configuration file support for default settings
- [ ] Progress bars for large file conversions
- [ ] Watch mode for automatic conversion on file changes
- [ ] Integration with popular editors (VS Code, etc.)
- [ ] Docker containerization for easy deployment
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
