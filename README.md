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

## Configuration

The tool can be configured using environment variables:

| Variable            | Description                         | Default         |
| ------------------- | ----------------------------------- | --------------- |
| SOURCE_DIR          | Directory to monitor for new images | /app/source     |
| COMPRESSED_DIR      | Directory for compressed images     | /app/compressed |
| COMPRESSION_QUALITY | Compression quality (0-100)         | 80              |
| LOSSLESS            | Enable lossless compression         | false           |
| CONVERT_TO_WEBP     | Convert images to WebP format       | true            |

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
```

## macOS Specific Configuration

### Using Delegate Mode for Event Handling

When running this tool on macOS, especially for monitoring screenshot directories, you should use the delegate mode to ensure proper event handling. macOS has specific file system event behaviors that may cause standard monitoring to miss events.

The application automatically uses a polling observer when running on macOS to improve compatibility with Docker volumes and to ensure reliable event detection for screenshots.

### Screenshot Auto-Compression

This tool is particularly useful for automatically compressing and optimizing screenshots on macOS. When you take a screenshot on macOS, the tool will:

1. Detect the new screenshot file
2. Automatically compress it according to your configuration
3. Save the optimized version to your designated output directory

This workflow helps manage disk space by keeping your screenshots optimized without manual intervention.

### macOS Event Detection Notes

On macOS, screenshot files initially appear as hidden files (with a leading dot) before becoming visible. The application has special handling for this behavior to ensure screenshots are properly detected and processed.

If you're experiencing issues with event detection on macOS, try these solutions:

- Ensure the application has proper permissions to access the monitored directory
- Use the polling observer mode (enabled by default)
- Increase the polling interval if needed by modifying the code

```
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
