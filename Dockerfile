FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    pandoc \
    texlive-latex-extra \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY *.py ./

# Create necessary directories
RUN mkdir -p /app/dist /app/input /tmp/conversion_images

# Set default command
CMD ["python", "main.py"]

# Add labels for metadata
LABEL maintainer="Markdown Converter CLI"
LABEL description="Docker container for converting Markdown to DOCX/PDF"
LABEL version="1.0"
