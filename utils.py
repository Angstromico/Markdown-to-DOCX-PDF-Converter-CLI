"""
Utility functions for the Markdown converter CLI.
"""

import os
import shutil
import subprocess
from pathlib import Path
from typing import Union
from rich.console import Console


def setup_colored_output() -> None:
    """Setup colored terminal output using colorama."""
    try:
        import colorama
        colorama.init()
    except ImportError:
        # colorama not available, but that's okay on Unix systems
        pass


def check_command_exists(command: str) -> bool:
    """
    Check if a command exists on the system.
    
    Args:
        command: Command name to check
        
    Returns:
        bool: True if command exists, False otherwise
    """
    return shutil.which(command) is not None


def validate_input_file(input_file: str) -> Path:
    """
    Validate the input file exists and has correct extension.
    
    Args:
        input_file: Path to the input file
        
    Returns:
        Path: Validated Path object
        
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file doesn't have .md extension
    """
    path = Path(input_file)
    
    # Check if file exists
    if not path.exists():
        raise FileNotFoundError(f"Input file '{input_file}' does not exist")
    
    # Check if it's a file (not directory)
    if not path.is_file():
        raise FileNotFoundError(f"'{input_file}' is not a file")
    
    # Check file extension
    if path.suffix.lower() != '.md':
        raise ValueError(f"Input file must have .md extension, got '{path.suffix}'")
    
    return path.resolve()


def create_output_directory(output_dir: Union[str, Path]) -> Path:
    """
    Create output directory if it doesn't exist.
    
    Args:
        output_dir: Path to the output directory
        
    Returns:
        Path: Path object for the output directory
    """
    path = Path(output_dir)
    
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
        console = Console()
        console.print(f"[blue]i[/blue] Created output directory: {path}")
    
    return path.resolve()


def get_file_size(file_path: Path) -> str:
    """
    Get human-readable file size.
    
    Args:
        file_path: Path to the file
        
    Returns:
        str: Human-readable file size
    """
    if not file_path.exists():
        return "0 B"
    
    size = file_path.stat().st_size
    
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    
    return f"{size:.1f} TB"


def print_conversion_summary(input_file: Path, output_dir: Path, formats: list[str]) -> None:
    """
    Print a summary of the conversion process.
    
    Args:
        input_file: Original input file
        output_dir: Output directory
        formats: List of formats that were generated
    """
    console = Console()
    
    console.print("\n[bold]Conversion Summary:[/bold]")
    console.print(f"  Input file: {input_file}")
    console.print(f"  Output directory: {output_dir}")
    console.print(f"  Generated formats: {', '.join(formats)}")
    
    for format_type in formats:
        output_file = output_dir / f"{input_file.stem}.{format_type}"
        if output_file.exists():
            size = get_file_size(output_file)
            console.print(f"  {format_type.upper()}: {output_file.name} ({size})")
