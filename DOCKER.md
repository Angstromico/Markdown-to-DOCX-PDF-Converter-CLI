# Docker Setup Guide

This guide explains how to use Docker to run the Markdown to DOCX/PDF Converter CLI with consistent Linux-style output, regardless of your host operating system.

## Why Use Docker?

- **Consistent Output**: Get the same Linux-style formatting and rendering on Windows, macOS, or Linux
- **No Local Dependencies**: No need to install Pandoc, wkhtmltopdf, or Python packages on your host system
- **Isolation**: Clean, reproducible environment without conflicts with local tools
- **Portability**: Works the same way everywhere

## Prerequisites

- Docker Desktop installed on your system
- Basic familiarity with Docker commands

## Quick Start

### Method 1: Using Docker Compose (Easiest)

1. **Build and run the conversion:**
   ```bash
   docker-compose up md-converter
   ```

2. **Check the output:**
   ```bash
   ls -la dist/
   ```

### Method 2: Using Docker Build and Run

1. **Build the Docker image:**
   ```bash
   docker build -t md-converter-cli .
   ```

2. **Run the conversion:**
   ```bash
   docker run --rm \
     -v "$(pwd)/RFC-Updating-Page.md:/app/input/input.md:ro" \
     -v "$(pwd)/dist:/app/dist" \
     md-converter-cli \
     python main.py input/input.md --output /app/dist
   ```

## Usage Examples

### Convert Your RFC File

```bash
# Using docker-compose with default file (RFC-Updating-Page.md)
docker-compose up md-converter

# Using docker-compose with custom file
INPUT_FILE=./your-file.md docker-compose up md-converter

# Using docker run directly
docker run --rm \
  -v "$(pwd)/RFC-Updating-Page.md:/app/input/input.md:ro" \
  -v "$(pwd)/dist:/app/dist" \
  md-converter-cli \
  python main.py input/input.md --docx --pdf --output /app/dist
```

### Interactive Shell Mode

Get an interactive shell in the container:

```bash
# Using docker-compose with shell profile
docker-compose --profile shell up md-converter-shell

# Or using docker run directly
docker run -it --rm \
  -v "$(pwd):/app/src" \
  -v "$(pwd)/dist:/app/dist" \
  md-converter-cli \
  /bin/bash
```

Once inside the container:
```bash
cd /app/src
python main.py RFC-Updating-Page.md --output /app/dist
ls -la /app/dist
```

### Convert Multiple Files

```bash
# Mount the entire directory and convert files
docker run --rm \
  -v "$(pwd):/app/workspace" \
  -v "$(pwd)/dist:/app/dist" \
  md-converter-cli \
  bash -c "cd /app/workspace && python main.py RFC-Updating-Page.md --output /app/dist"
```

## Volume Mounting Explained

- **Input Files**: Mount your Markdown files to `/app/input/` inside the container
- **Output Directory**: Mount a local `dist/` folder to `/app/dist` to receive converted files
- **Source Code**: Mount the project directory to access all files

## File Paths

- **Container Input Path**: `/app/input/`
- **Container Output Path**: `/app/dist`
- **Container Working Directory**: `/app`

## Docker Compose Services

### md-converter
- **Purpose**: One-shot conversion
- **Usage**: `docker-compose up md-converter`
- **Default**: Converts `RFC-Updating-Page.md` to both DOCX and PDF

### md-converter-shell
- **Purpose**: Interactive shell for testing
- **Usage**: `docker-compose --profile shell up md-converter-shell`
- **Access**: Gives you a bash shell inside the container

## Customization

### Different Input Files

Modify the `docker-compose.yml` to point to different files:

```yaml
volumes:
  - ./your-file.md:/app/input/input.md:ro
```

Or use command line:

```bash
docker run --rm \
  -v "$(pwd)/your-file.md:/app/input/custom.md:ro" \
  -v "$(pwd)/dist:/app/dist" \
  md-converter-cli \
  python main.py input/custom.md --output /app/dist
```

### Different Output Formats

```bash
# DOCX only
docker run --rm \
  -v "$(pwd)/RFC-Updating-Page.md:/app/input/input.md:ro" \
  -v "$(pwd)/dist:/app/dist" \
  md-converter-cli \
  python main.py input/input.md --docx --output /app/dist

# PDF only
docker run --rm \
  -v "$(pwd)/RFC-Updating-Page.md:/app/input/input.md:ro" \
  -v "$(pwd)/dist:/app/dist" \
  md-converter-cli \
  python main.py input/input.md --pdf --output /app/dist
```

## Troubleshooting

### Permission Issues (Linux/macOS)

```bash
# Fix permissions if needed
sudo chown -R $USER:$USER dist/
```

### Docker Not Running

Make sure Docker Desktop is running and you have permissions to use Docker.

### Build Issues

If the build fails, try:

```bash
# Clean build
docker-compose build --no-cache
# or
docker build --no-cache -t md-converter-cli .
```

### Container Not Found

```bash
# Rebuild the image
docker-compose build
```

## Advanced Usage

### Custom Dockerfile

If you need to customize the environment, modify the `Dockerfile`:

```dockerfile
# Add additional system packages
RUN apt-get install -y \
    additional-package \
    && rm -rf /var/lib/apt/lists/*

# Add custom Python packages
COPY custom-requirements.txt .
RUN pip install -r custom-requirements.txt
```

### Environment Variables

Set environment variables in docker-compose.yml:

```yaml
environment:
  - PYTHONUNBUFFERED=1
  - CUSTOM_VAR=value
```

### Multi-stage Build

For production use, you can optimize the image size with multi-stage builds.

## Benefits for Windows Users

1. **Linux Rendering**: Get the exact same PDF rendering as on Linux
2. **No Installation**: Skip installing Pandoc, wkhtmltopdf, and Python packages
3. **Consistency**: Same output across all development machines
4. **Clean System**: No system-wide installations required

## Performance Notes

- First run may be slower due to image building
- Subsequent runs are much faster
- Image size is approximately 500MB-1GB depending on installed packages
- Conversion speed is comparable to native Linux execution
