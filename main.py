import os
import time
import traceback
import logging
from pathlib import Path
from PIL import Image
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Check format support
def check_format_support():
    supported_formats = Image.registered_extensions()
    webp_supported = '.webp' in supported_formats.values()
    return webp_supported

# Get configuration from environment variables
SOURCE_DIR = os.getenv('SOURCE_DIR', '/app/source')
COMPRESSED_DIR = os.getenv('COMPRESSED_DIR', '/app/compressed')
COMPRESSION_QUALITY = int(os.getenv('COMPRESSION_QUALITY', '100'))
LOSSLESS = os.getenv('LOSSLESS', 'false').lower() == 'true'
CONVERT_TO_WEBP = os.getenv('CONVERT_TO_WEBP', 'true').lower() == 'true'

# Check format support
WEBP_SUPPORTED = check_format_support()

# Ensure directories exist
Path(SOURCE_DIR).mkdir(parents=True, exist_ok=True)
Path(COMPRESSED_DIR).mkdir(parents=True, exist_ok=True)

class ImageHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        logging.info(f"New file detected: {event.src_path}")
        self.process_image(event.src_path)

    def on_modified(self, event):
        if event.is_directory:
            return
        logging.info(f"File modification detected: {event.src_path}")
        self.process_image(event.src_path)

    def process_image(self, source_path):
        try:
            # Check if file is an image
            logging.info(f"Checking if file is an image: {source_path}")
            if not self._is_image(source_path):
                logging.info(f"File is not an image, skipping: {source_path}")
                return

            # Get output file path
            filename = os.path.basename(source_path)
            name, ext = os.path.splitext(filename)
            output_ext = '.webp' if CONVERT_TO_WEBP else ext
            output_path = os.path.join(COMPRESSED_DIR, f"{name}{output_ext}")
            logging.info(f"Output path: {output_path}")

            # Get original file size
            original_size = os.path.getsize(source_path)
            logging.info(f"Opening image: {source_path} (original size: {original_size:,} bytes)")
            with Image.open(source_path) as img:
                logging.info(f"Image info - Mode: {img.mode}, Size: {img.size}, Format: {img.format}")

                # Convert RGBA images
                if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
                    logging.info(f"Converting image mode from {img.mode} to RGBA")
                    img = img.convert('RGBA')
                else:
                    logging.info(f"Converting image mode from {img.mode} to RGB")
                    img = img.convert('RGB')

                # Save compressed image
                logging.info("Starting to save processed image...")
                if CONVERT_TO_WEBP:
                    logging.info("Saving in WebP format")
                    if LOSSLESS:
                        logging.info("Using lossless compression mode")
                        img.save(output_path, 'WEBP', lossless=True)
                    else:
                        logging.info(f"Using lossy compression mode, quality: {COMPRESSION_QUALITY}")
                        img.save(output_path, 'WEBP', quality=COMPRESSION_QUALITY)
                else:
                    logging.info(f"Saving in original format ({ext})")
                    if LOSSLESS:
                        logging.info("Using lossless compression mode")
                        img.save(output_path, quality=100, optimize=True)
                    else:
                        logging.info(f"Using lossy compression mode, quality: {COMPRESSION_QUALITY}")
                        img.save(output_path, quality=COMPRESSION_QUALITY, optimize=True)

                logging.info(f"Image processing completed: {source_path} -> {output_path}")
                if os.path.exists(output_path):
                    compressed_size = os.path.getsize(output_path)
                    size_reduction = original_size - compressed_size
                    reduction_percent = (size_reduction / original_size) * 100
                    logging.info("Compression results:")
                    logging.info(f"  - Original size: {original_size:,} bytes")
                    logging.info(f"  - Compressed size: {compressed_size:,} bytes")
                    logging.info(f"  - Reduced by: {size_reduction:,} bytes ({reduction_percent:.1f}%)")
                else:
                    logging.warning("Warning: Output file was not created successfully")

        except Exception as e:
            logging.error(f"Error processing image {source_path}:")
            logging.error(f"Error type: {type(e).__name__}")
            logging.error(f"Error message: {str(e)}")
            logging.error("Error traceback:")
            logging.error(traceback.format_exc())

    def _is_image(self, file_path):
        try:
            Image.open(file_path)
            return True
        except Exception as e:
            logging.error(f"Error checking file type: {str(e)}")
            return False

def main():
    # Check configuration conflicts
    if LOSSLESS and COMPRESSION_QUALITY < 100:
        logging.warning("\nWarning: Configuration conflict detected!")
        logging.warning("Both lossless compression (LOSSLESS=true) and lossy quality setting (COMPRESSION_QUALITY=%d) are enabled" % COMPRESSION_QUALITY)
        logging.warning("In lossless mode, compression quality setting will be ignored, images will be saved at highest quality\n")

    # Create event handler and observer
    event_handler = ImageHandler()
    observer = Observer()
    observer.schedule(event_handler, SOURCE_DIR, recursive=False)
    observer.start()

    logging.info("=== Image Compression Service Started ===")
    logging.info(f"Monitoring folder: {os.path.abspath(SOURCE_DIR)}")
    logging.info(f"Output folder: {os.path.abspath(COMPRESSED_DIR)}")
    logging.info("\nCurrent configuration:")
    logging.info(f"Compression quality: {COMPRESSION_QUALITY}")
    logging.info(f"Lossless compression: {LOSSLESS}")
    logging.info(f"Convert to WebP: {CONVERT_TO_WEBP}")
    logging.info("\nWaiting for image files...")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        logging.info("Monitoring stopped")

    observer.join()

if __name__ == '__main__':
    main()