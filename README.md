# Image Compress

A powerful and efficient image compression tool that automatically monitors a directory for new images and compresses them using various optimization techniques. It supports both lossy and lossless compression, with optional WebP conversion for better compression ratios.

## Features

- 🔄 Real-time directory monitoring for new images
- 🖼️ Supports multiple image formats
- 🎯 Configurable compression quality
- ✨ Optional WebP conversion
- 🔒 Lossless compression option
- 📊 Detailed compression statistics
- 🐳 Docker support for easy deployment

## Requirements

- Python 3.x
- Docker (optional)
- PIL/Pillow library
- watchdog library

## Installation

### Using Docker (Recommended)

1. Clone the repository:
   ```bash
   git clone https://github.com/zhaochunqi/image_compress.git
   cd image_compress
   ```

2. Build and run using Docker Compose:
   ```bash
   docker-compose up -d
   ```

### Manual Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/zhaochunqi/image_compress.git
   cd image_compress
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the script:
   ```bash
   python image_compressor.py
   ```

## Configuration

The tool can be configured using environment variables:

| Variable | Description | Default |
|----------|-------------|----------|
| SOURCE_DIR | Directory to monitor for new images | /app/source |
| COMPRESSED_DIR | Directory for compressed images | /app/compressed |
| COMPRESSION_QUALITY | Compression quality (0-100) | 80 |
| LOSSLESS | Enable lossless compression | false |
| CONVERT_TO_WEBP | Convert images to WebP format | true |

### Docker Compose Configuration

You can modify these settings in the `compose.yml` file:

```yaml
services:
  image-compressor:
    environment:
      - SOURCE_DIR=/app/source
      - COMPRESSED_DIR=/app/compressed
      - COMPRESSION_QUALITY=80
      - LOSSLESS=true
      - CONVERT_TO_WEBP=true
```

## Usage

1. Place your images in the source directory
2. The tool will automatically detect and process new images
3. Compressed images will be saved in the compressed directory
4. Check the logs for detailed compression statistics

### Example Output

```
=== Image Compression Service Started ===
Monitoring folder: /app/source
Output folder: /app/compressed

Current configuration:
Compression quality: 80
Lossless compression: true
Convert to WebP: true

Compression results:
  - Original size: 1,234,567 bytes
  - Compressed size: 234,567 bytes
  - Reduced by: 1,000,000 bytes (81.0%)
```

## Image Format Support

- Input formats: JPEG, PNG, GIF, BMP, TIFF
- Output formats: Original format or WebP (configurable)

## Performance

- Supports both RGB and RGBA images
- Automatic color mode conversion
- Optimized for both quality and file size
- Real-time processing with minimal delay

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the MIT License.