"""
Markdown converter module for handling DOCX and PDF conversions using Pandoc.
"""

import subprocess
import sys
import re
from pathlib import Path
from typing import Tuple, Optional
from rich.console import Console

from utils import create_output_directory, check_command_exists


def remove_emojis(text):
    """Remove emoji and problematic Unicode characters from text for LaTeX compatibility."""
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F700-\U0001F77F"  # alchemical symbols
        "\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
        "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
        "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
        "\U0001FA00-\U0001FA6F"  # Chess Symbols
        "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
        "\U00002702-\U000027B0"  # Dingbats
        "\U000024C2-\U0001F251"  # Enclosed characters
        "\u200D-\u200F"          # Zero-width characters
        "\uFE0F-\uFEFF"          # Variation selectors and special characters
        "]+",
        flags=re.UNICODE
    )
    return emoji_pattern.sub(r'', text)


class MarkdownConverter:
    """Handles conversion of Markdown files to DOCX and PDF formats."""
    
    def __init__(self, input_file: Path, output_dir: str):
        """
        Initialize the converter.
        
        Args:
            input_file: Path to the input Markdown file
            output_dir: Output directory for converted files
        """
        self.input_file = input_file
        self.output_dir = Path(output_dir)
        self.console = Console()
        
        # Create output directory if it doesn't exist
        create_output_directory(self.output_dir)
    
    def check_dependencies(self) -> None:
        """
        Check if required dependencies are installed.
        
        Raises:
            SystemExit: If Pandoc is not installed
        """
        # Check for Pandoc
        if not check_command_exists('pandoc'):
            self.console.print("[red]x[/red] Pandoc is not installed!")
            self.console.print("\n[yellow]To install Pandoc:[/yellow]")
            self.console.print("  • Ubuntu/Debian: sudo apt-get install pandoc")
            self.console.print("  • macOS: brew install pandoc")
            self.console.print("  • Windows: Download from https://pandoc.org/installing.html")
            sys.exit(1)
        
        self.console.print("[green]+[/green] Pandoc is installed")
        
        # Check for PDF engines
        pdf_engines = self._get_available_pdf_engines()
        if pdf_engines:
            self.console.print(f"[green]+[/green] Available PDF engines: {', '.join(pdf_engines)}")
        else:
            self.console.print("[yellow]![/yellow] No PDF engine found")
            self.console.print("\n[yellow]To install a PDF engine:[/yellow]")
            self.console.print("  • wkhtmltopdf (recommended):")
            self.console.print("    - Ubuntu/Debian: sudo apt-get install wkhtmltopdf")
            self.console.print("    - macOS: brew install wkhtmltopdf")
            self.console.print("    - Windows: Download from https://wkhtmltopdf.org/")
            self.console.print("  • pdflatex (alternative):")
            self.console.print("    - Ubuntu/Debian: sudo apt-get install texlive-latex-extra")
            self.console.print("    - macOS: brew install --cask mactex")
            self.console.print("    - Windows: Download from https://www.tug.org/texlive/")
    
    def _get_available_pdf_engines(self) -> list[str]:
        """Get list of available PDF engines."""
        engines = []
        
        if check_command_exists('wkhtmltopdf'):
            engines.append('wkhtmltopdf')
        
        if check_command_exists('pdflatex'):
            engines.append('pdflatex')
        
        return engines
    
    def convert(self, generate_docx: bool, generate_pdf: bool) -> bool:
        """
        Convert the Markdown file to the specified formats.
        
        Args:
            generate_docx: Whether to generate DOCX output
            generate_pdf: Whether to generate PDF output
            
        Returns:
            bool: True if all conversions succeeded, False otherwise
        """
        success = True
        
        if generate_docx:
            success &= self._convert_to_docx()
        
        if generate_pdf:
            success &= self._convert_to_pdf()
        
        return success
    
    def _convert_to_docx(self) -> bool:
        """Convert Markdown to DOCX format."""
        try:
            output_file = self.output_dir / f"{self.input_file.stem}.docx"
            
            self.console.print(f"[blue]→[/blue] Converting to DOCX: {output_file}")
            
            cmd = [
                'pandoc',
                str(self.input_file),
                '-o', str(output_file)
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            self.console.print(f"[green]+[/green] DOCX file created: {output_file}")
            return True
            
        except subprocess.CalledProcessError as e:
            self.console.print(f"[red]x[/red] DOCX conversion failed: {e.stderr}")
            return False
        except Exception as e:
            self.console.print(f"[red]x[/red] DOCX conversion error: {e}")
            return False
    
    def _convert_to_pdf(self) -> bool:
        """Convert Markdown to PDF format."""
        try:
            output_file = self.output_dir / f"{self.input_file.stem}.pdf"
            
            self.console.print(f"[blue]→[/blue] Converting to PDF: {output_file}")
            
            # Read the original markdown file
            with open(self.input_file, 'r', encoding='utf-8') as f:
                markdown_content = f.read()
            
            # Remove emojis for LaTeX compatibility
            markdown_content = remove_emojis(markdown_content)
            
            # Create temporary file with emojis removed
            temp_file = self.input_file.parent / f"{self.input_file.stem}_no_emoji.md"
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            # Determine which PDF engine to use
            pdf_engines = self._get_available_pdf_engines()
            
            if not pdf_engines:
                self.console.print("[red]x[/red] No PDF engine available for PDF conversion")
                return False
            
            # Use the first available engine (prefer wkhtmltopdf)
            pdf_engine = pdf_engines[0]
            
            cmd = [
                'pandoc',
                str(temp_file),
                '-o', str(output_file),
                '--pdf-engine=pdflatex'
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            # Clean up temporary file
            temp_file.unlink(missing_ok=True)
            
            self.console.print(f"[green]+[/green] PDF file created: {output_file} (using {pdf_engine})")
            return True
            
        except subprocess.CalledProcessError as e:
            self.console.print(f"[red]x[/red] PDF conversion failed: {e.stderr}")
            return False
        except Exception as e:
            self.console.print(f"[red]x[/red] PDF conversion error: {e}")
            return False
