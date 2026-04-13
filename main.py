#!/usr/bin/env python3
"""
Markdown to DOCX/PDF Converter CLI
A command-line tool for converting Markdown files to DOCX and PDF formats using Pandoc.
"""

import argparse
import sys
from pathlib import Path
from rich.console import Console
from rich.traceback import install

from converter import MarkdownConverter
from utils import validate_input_file, setup_colored_output

# Install rich traceback for better error display
install()


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        prog='md-converter-cli',
        description='Convert Markdown files to DOCX and PDF formats',
        epilog='Example: python main.py input.md --docx --pdf --output ./dist'
    )
    
    parser.add_argument(
        'input_file',
        help='Path to the input Markdown file'
    )
    
    parser.add_argument(
        '--docx',
        action='store_true',
        help='Generate DOCX output file'
    )
    
    parser.add_argument(
        '--pdf',
        action='store_true',
        help='Generate PDF output file'
    )
    
    parser.add_argument(
        '--output', '-o',
        default='./dist',
        help='Output directory for converted files (default: ./dist)'
    )
    
    return parser


def main():
    """Main entry point for the CLI application."""
    console = Console()
    
    # Setup colored output
    setup_colored_output()
    
    # Parse command line arguments
    parser = create_parser()
    args = parser.parse_args()
    
    try:
        # Validate input file
        input_path = validate_input_file(args.input_file)
        console.print(f"[green]+[/green] Input file validated: {input_path}")
        
        # Determine output formats
        generate_docx = args.docx
        generate_pdf = args.pdf
        
        # If no format specified, generate both
        if not generate_docx and not generate_pdf:
            generate_docx = True
            generate_pdf = True
            console.print("[blue]i[/blue] No format specified, generating both DOCX and PDF")
        
        # Create converter instance
        converter = MarkdownConverter(input_path, args.output)
        
        # Check dependencies
        converter.check_dependencies()
        
        # Perform conversions
        success = converter.convert(generate_docx, generate_pdf)
        
        if success:
            console.print("[green]+[/green] Conversion completed successfully!")
            sys.exit(0)
        else:
            console.print("[red]x[/red] Conversion failed!")
            sys.exit(1)
            
    except FileNotFoundError as e:
        console.print(f"[red]x[/red] File not found: {e}")
        sys.exit(1)
    except ValueError as e:
        console.print(f"[red]x[/red] Invalid input: {e}")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]x[/red] Unexpected error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
