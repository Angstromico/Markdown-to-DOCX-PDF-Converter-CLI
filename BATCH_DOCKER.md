# Batch Docker Conversion Guide

This guide explains how to use the batch conversion system for processing multiple markdown files with automatic image handling in Docker.

## Overview

The batch converter processes all markdown files in the `markdown/` directory, automatically handling images from the `images/` directory:

1. **Scans** all `.md` files in `markdown/` folder
2. **Extracts** image references from each file
3. **Copies** required images to temporary container location
4. **Modifies** markdown links to use temporary paths
5. **Converts** all files to DOCX and PDF
6. **Cleans up** temporary images automatically

## Directory Structure

```
project/
|-- markdown/                    # Input markdown files
|   |-- file1.md
|   |-- file2.md
|   `-- file3.md
|-- images/                      # Image files
|   |-- image1.png
|   |-- image2.jpg
|   `-- logo.png
|-- dist/                        # Output files (created automatically)
|   |-- file1.docx
|   |-- file1.pdf
|   |-- file2.docx
|   |-- file2.pdf
|   |-- file3.docx
|   `-- file3.pdf
|-- batch_converter.py           # Batch conversion script
|-- docker-compose-batch.yml     # Docker configuration
`-- BATCH_DOCKER.md              # This guide
```

## Quick Start

### 1. Prepare Your Files

Place your markdown files in the `markdown/` directory:
```bash
mkdir -p markdown images
# Copy your .md files to markdown/
# Copy your images to images/
```

### 2. Run Batch Conversion

```bash
# Build and run batch conversion
docker-compose -f docker-compose-batch.yml up batch-converter

# For PowerShell users
docker-compose -f docker-compose-batch.yml up batch-converter
```

### 3. Check Results

```bash
ls -la dist/
```

## Usage Examples

### Basic Batch Conversion

Convert all markdown files with both DOCX and PDF:
```bash
docker-compose -f docker-compose-batch.yml up batch-converter
```

### DOCX Only

```bash
docker-compose -f docker-compose-batch.yml run --rm batch-converter python batch_converter.py --no-pdf
```

### PDF Only

```bash
docker-compose -f docker-compose-batch.yml run --rm batch-converter python batch_converter.py --no-docx
```

### Custom Directories

```bash
docker-compose -f docker-compose-batch.yml run --rm batch-converter python batch_converter.py --markdown-dir /app/docs --images-dir /app/assets --output-dir /app/output
```

## Image Processing

### How It Works

1. **Detection**: The script scans each markdown file for image references:
   - Markdown format: `![alt](image.png)`
   - HTML format: `<img src="image.png">`

2. **Temporary Setup**: Required images are copied to `/tmp/conversion_images/` in the container

3. **Link Modification**: Markdown links are updated to point to temporary paths:
   - Original: `![alt](image.png)`
   - Modified: `![alt](/tmp/conversion_images/image.png)`

4. **Conversion**: Pandoc processes files with accessible images

5. **Cleanup**: Temporary images are automatically removed

### Supported Image Formats

- PNG, JPG, JPEG, GIF, SVG, BMP
- Any format supported by Pandoc

### Image Path Examples

**Original Markdown:**
```markdown
![Logo](logo.png)
<img src="screenshot.jpg" width="500"/>
![Diagram](./images/diagram.png)
```

**Processed in Container:**
```markdown
![Logo](/tmp/conversion_images/logo.png)
<img src="/tmp/conversion_images/screenshot.jpg" width="500"/>
![Diagram](/tmp/conversion_images/diagram.png)
```

## Advanced Usage

### Interactive Shell Mode

For testing and debugging:
```bash
docker-compose -f docker-compose-batch.yml --profile shell up batch-converter-shell
```

Once inside the container:
```bash
# Test single file
python batch_converter.py --markdown-dir /app/markdown --images-dir /app/images

# Check available files
ls -la /app/markdown/
ls -la /app/images/
```

### Custom Parameters

```bash
docker-compose -f docker-compose-batch.yml run --rm batch-converter python batch_converter.py \
  --markdown-dir /app/my-docs \
  --images-dir /app/my-images \
  --output-dir /app/my-output \
  --docx \
  --pdf
```

### Environment Variables

You can use environment variables for configuration:

```bash
export MARKDOWN_DIR="./docs"
export IMAGES_DIR="./assets"
export OUTPUT_DIR="./output"

docker-compose -f docker-compose-batch.yml run --rm batch-converter \
  python batch_converter.py \
  --markdown-dir $MARKDOWN_DIR \
  --images-dir $IMAGES_DIR \
  --output-dir $OUTPUT_DIR
```

## Troubleshooting

### Images Not Appearing

**Problem**: Images don't appear in generated PDFs

**Solution**: 
1. Verify images exist in `images/` directory
2. Check image names match exactly (case-sensitive)
3. Ensure images are in supported formats

```bash
# Check available images
ls -la images/

# Test single file
docker-compose -f docker-compose-batch.yml run --rm batch-converter python batch_converter.py --markdown-dir /app/markdown --images-dir /app/images
```

### Permission Issues

**Problem**: Permission denied errors

**Solution**: The container runs as root, but output files should be accessible:

```bash
# Fix permissions on output files
sudo chown -R $USER:$USER dist/
```

### Missing Files

**Problem**: "No markdown files found"

**Solution**: Verify directory structure:

```bash
# Check directories
ls -la markdown/
ls -la images/

# Create test files
echo "# Test" > markdown/test.md
```

### Docker Issues

**Problem**: Container fails to start

**Solution**: Rebuild the image:

```bash
docker-compose -f docker-compose-batch.yml build --no-cache
```

## Performance Considerations

### Large Numbers of Files

For batch processing many files:
- Ensure sufficient disk space
- Monitor memory usage
- Consider processing in batches for very large sets

### Image Size

Large images can slow down conversion:
- Optimize images before processing
- Consider resizing large images
- Use appropriate formats (PNG for graphics, JPG for photos)

## Best Practices

### File Organization

- Keep markdown files in `markdown/` directory
- Store all images in `images/` directory
- Use consistent naming conventions
- Avoid spaces in filenames

### Image Optimization

- Use appropriate image formats
- Compress large images
- Maintain reasonable resolution (150-300 DPI for documents)

### Markdown Formatting

- Use relative paths for images
- Test images locally before batch processing
- Validate markdown syntax

## Command Reference

### Batch Converter Options

```bash
python batch_converter.py [OPTIONS]

Options:
  --markdown-dir DIR     Directory with markdown files (default: markdown)
  --images-dir DIR       Directory with images (default: images)
  --output-dir DIR       Output directory (default: dist)
  --docx                 Generate DOCX files (default: True)
  --no-docx              Skip DOCX generation
  --pdf                  Generate PDF files (default: True)
  --no-pdf               Skip PDF generation
```

### Docker Commands

```bash
# Build image
docker-compose -f docker-compose-batch.yml build

# Run batch conversion
docker-compose -f docker-compose-batch.yml up batch-converter

# Run with custom parameters
docker-compose -f docker-compose-batch.yml run --rm batch-converter [COMMAND]

# Interactive shell
docker-compose -f docker-compose-batch.yml --profile shell up batch-converter-shell

# Clean up
docker-compose -f docker-compose-batch.yml down
```

## Integration Examples

### CI/CD Pipeline

```yaml
# GitHub Actions example
- name: Convert documentation
  run: |
    docker-compose -f docker-compose-batch.yml up batch-converter
    ls -la dist/
```

### Makefile Integration

```makefile
.PHONY: convert-batch
convert-batch:
	docker-compose -f docker-compose-batch.yml up batch-converter

clean:
	rm -rf dist/
	docker-compose -f docker-compose-batch.yml down
```

## Security Notes

- Images are processed in isolated container
- Temporary files are automatically cleaned up
- No persistent data stored in container
- Network access limited to image fetching

## Support

For issues with batch conversion:

1. Check file permissions and directory structure
2. Verify image formats and paths
3. Test with single files first
4. Check Docker logs for detailed error messages

The batch converter provides automated, efficient processing of multiple markdown files with intelligent image handling for consistent, professional output.
