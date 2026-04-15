#!/usr/bin/env python3
"""
Batch Markdown Converter with Image Processing
Converts multiple markdown files with automatic image handling for Docker containers.
"""

import os
import re
import shutil
import glob
import sys
from pathlib import Path
from typing import List, Dict, Tuple
from rich.console import Console
from rich.progress import Progress, TaskID

from converter import MarkdownConverter
from utils import validate_input_file

console = Console()


class BatchMarkdownConverter:
    """Handles batch conversion of markdown files with image processing."""
    
    def __init__(self, markdown_dir: str = "markdown", images_dir: str = "images", output_dir: str = "dist"):
        """
        Initialize the batch converter.
        
        Args:
            markdown_dir: Directory containing markdown files
            images_dir: Directory containing images
            output_dir: Directory for output files
        """
        self.markdown_dir = Path(markdown_dir)
        self.images_dir = Path(images_dir)
        self.output_dir = Path(output_dir)
        self.temp_images_dir = Path("/tmp/conversion_images")
        
        # Ensure directories exist
        self.markdown_dir.mkdir(exist_ok=True)
        self.images_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)
        
    def find_markdown_files(self) -> List[Path]:
        """Find all markdown files in the markdown directory."""
        pattern = str(self.markdown_dir / "*.md")
        files = glob.glob(pattern)
        return [Path(f) for f in files]
    
    def extract_images_from_markdown(self, markdown_path: Path) -> List[str]:
        """
        Extract image references from markdown file.
        
        Args:
            markdown_path: Path to markdown file
            
        Returns:
            List of image filenames found in the markdown
        """
        try:
            with open(markdown_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find all image references: ![alt](image.png) and <img src="image.png"/>
            img_pattern = r'(?:!\[.*?\]\(([^)]+)\)|<img[^>]+src=["\']([^"\']+)["\'][^>]*>)'
            matches = re.findall(img_pattern, content, re.IGNORECASE)
            
            # Extract image names from matches (tuple groups)
            images = []
            for match in matches:
                img_path = match[0] if match[0] else match[1]
                img_name = Path(img_path).name
                if img_name:
                    images.append(img_name)
            
            return list(set(images))  # Remove duplicates
            
        except Exception as e:
            console.print(f"[red]x[/red] Error reading {markdown_path}: {e}")
            return []
    
    def setup_temp_images(self, required_images: List[str]) -> bool:
        """
        Copy required images to temporary directory in container.
        
        Args:
            required_images: List of image filenames needed
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create temp directory
            self.temp_images_dir.mkdir(parents=True, exist_ok=True)
            
            console.print(f"[blue]i[/blue] Setting up {len(required_images)} images for conversion...")
            
            copied_count = 0
            for img_name in required_images:
                source_path = self.images_dir / img_name
                temp_path = self.temp_images_dir / img_name
                
                if source_path.exists():
                    shutil.copy2(source_path, temp_path)
                    copied_count += 1
                    console.print(f"[green]+[/green] Copied: {img_name}")
                else:
                    console.print(f"[yellow]![/yellow] Image not found: {img_name}")
            
            console.print(f"[green]+[/green] {copied_count}/{len(required_images)} images ready")
            return True
            
        except Exception as e:
            console.print(f"[red]x[/red] Error setting up images: {e}")
            return False
    
    def modify_markdown_image_links(self, markdown_path: Path, temp_markdown_path: Path) -> bool:
        """
        Modify markdown file to use temporary image paths.
        
        Args:
            markdown_path: Original markdown file
            temp_markdown_path: Path for modified markdown file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(markdown_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Modify image paths to point to temp directory
            def replace_image_path(match):
                alt_text = match.group(1) if match.group(1) else ""
                original_path = match.group(2) if match.group(2) else match.group(3) if match.group(3) else ""
                
                if original_path:
                    img_name = Path(original_path).name
                    new_path = f"/tmp/conversion_images/{img_name}"
                    
                    if match.group(1):  # ![alt](path) format
                        return f"![{alt_text}]({new_path})"
                    else:  # <img src="path"> format
                        return match.group(0).replace(original_path, new_path)
                return match.group(0)
            
            # Pattern for both markdown and HTML image formats
            img_pattern = r'(!\[([^\]]*)\]\(([^)]+)\))|(<img[^>]+src=["\']([^"\']+)["\'][^>]*>)'
            modified_content = re.sub(img_pattern, replace_image_path, content, flags=re.IGNORECASE)
            
            # Write modified content
            with open(temp_markdown_path, 'w', encoding='utf-8') as f:
                f.write(modified_content)
            
            return True
            
        except Exception as e:
            console.print(f"[red]x[/red] Error modifying markdown: {e}")
            return False
    
    def cleanup_temp_images(self):
        """Clean up temporary images from container."""
        try:
            if self.temp_images_dir.exists():
                shutil.rmtree(self.temp_images_dir)
                console.print(f"[green]+[/green] Cleaned up temporary images")
        except Exception as e:
            console.print(f"[yellow]![/yellow] Warning: Could not clean up temp images: {e}")
    
    def convert_single_file(self, markdown_path: Path, generate_docx: bool = True, generate_pdf: bool = True) -> bool:
        """
        Convert a single markdown file with image processing.
        
        Args:
            markdown_path: Path to markdown file
            generate_docx: Whether to generate DOCX
            generate_pdf: Whether to generate PDF
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Extract required images
            required_images = self.extract_images_from_markdown(markdown_path)
            
            # Setup temporary images if needed
            temp_markdown_path = markdown_path
            if required_images:
                if not self.setup_temp_images(required_images):
                    console.print(f"[red]x[/red] Failed to setup images for {markdown_path.name}")
                    return False
                
                # Create modified markdown with temp paths
                temp_markdown_path = Path(f"/tmp/{markdown_path.name}")
                if not self.modify_markdown_image_links(markdown_path, temp_markdown_path):
                    console.print(f"[red]x[/red] Failed to modify image links for {markdown_path.name}")
                    return False
            
            # Convert the file
            converter = MarkdownConverter(temp_markdown_path, str(self.output_dir))
            success = converter.convert(generate_docx, generate_pdf)
            
            # Clean up temporary markdown file if created
            if temp_markdown_path != markdown_path and temp_markdown_path.exists():
                temp_markdown_path.unlink()
            
            return success
            
        except Exception as e:
            console.print(f"[red]x[/red] Error converting {markdown_path.name}: {e}")
            return False
    
    def convert_all(self, generate_docx: bool = True, generate_pdf: bool = True) -> Dict[str, bool]:
        """
        Convert all markdown files in the directory.
        
        Args:
            generate_docx: Whether to generate DOCX files
            generate_pdf: Whether to generate PDF files
            
        Returns:
            Dictionary mapping filenames to success status
        """
        markdown_files = self.find_markdown_files()
        
        if not markdown_files:
            console.print("[yellow]![/yellow] No markdown files found in {self.markdown_dir}")
            return {}
        
        console.print(f"[blue]i[/blue] Found {len(markdown_files)} markdown files")
        
        results = {}
        
        with Progress() as progress:
            task = progress.add_task("Converting files...", total=len(markdown_files))
            
            for md_file in markdown_files:
                console.print(f"\n[blue]i[/blue] Processing: {md_file.name}")
                
                success = self.convert_single_file(md_file, generate_docx, generate_pdf)
                results[md_file.name] = success
                
                if success:
                    console.print(f"[green]+[/green] Successfully converted: {md_file.name}")
                else:
                    console.print(f"[red]x[/red] Failed to convert: {md_file.name}")
                
                progress.advance(task)
        
        # Cleanup temporary images
        self.cleanup_temp_images()
        
        return results
    
    def print_summary(self, results: Dict[str, bool]):
        """Print conversion summary."""
        total = len(results)
        successful = sum(results.values())
        failed = total - successful
        
        console.print(f"\n[bold]Conversion Summary:[/bold]")
        console.print(f"  Total files: {total}")
        console.print(f"  Successful: {successful}")
        console.print(f"  Failed: {failed}")
        
        if failed > 0:
            console.print(f"\n[red]Failed files:[/red]")
            for filename, success in results.items():
                if not success:
                    console.print(f"  - {filename}")


def main():
    """Main entry point for batch conversion."""
    import argparse
    
    parser = argparse.ArgumentParser(
        prog='batch-converter',
        description='Batch convert markdown files with image processing'
    )
    
    parser.add_argument(
        '--markdown-dir',
        default='markdown',
        help='Directory containing markdown files (default: markdown)'
    )
    
    parser.add_argument(
        '--images-dir',
        default='images',
        help='Directory containing images (default: images)'
    )
    
    parser.add_argument(
        '--output-dir',
        default='dist',
        help='Output directory for converted files (default: dist)'
    )
    
    parser.add_argument(
        '--docx',
        action='store_true',
        default=True,
        help='Generate DOCX files (default: True)'
    )
    
    parser.add_argument(
        '--no-docx',
        action='store_true',
        help='Skip DOCX generation'
    )
    
    parser.add_argument(
        '--pdf',
        action='store_true',
        default=True,
        help='Generate PDF files (default: True)'
    )
    
    parser.add_argument(
        '--no-pdf',
        action='store_true',
        help='Skip PDF generation'
    )
    
    args = parser.parse_args()
    
    # Determine output formats
    generate_docx = args.docx and not args.no_docx
    generate_pdf = args.pdf and not args.no_pdf
    
    if not generate_docx and not generate_pdf:
        console.print("[red]x[/red] Error: At least one output format must be specified")
        sys.exit(1)
    
    # Create batch converter
    converter = BatchMarkdownConverter(
        markdown_dir=args.markdown_dir,
        images_dir=args.images_dir,
        output_dir=args.output_dir
    )
    
    # Run conversion
    console.print("[bold]Starting Batch Conversion[/bold]")
    console.print(f"Markdown directory: {args.markdown_dir}")
    console.print(f"Images directory: {args.images_dir}")
    console.print(f"Output directory: {args.output_dir}")
    console.print(f"Formats: {'DOCX' if generate_docx else ''} {'PDF' if generate_pdf else ''}")
    
    results = converter.convert_all(generate_docx, generate_pdf)
    converter.print_summary(results)
    
    # Exit with error code if any conversions failed
    if any(not success for success in results.values()):
        sys.exit(1)


if __name__ == '__main__':
    main()
