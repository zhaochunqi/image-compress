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
    def _should_process_file(self, file_path, previous_path=None, message=None):
        """Helper method to determine if a file should be processed based on its name.
        Returns the file path to process if it should be processed, None otherwise."""
        filename = os.path.basename(file_path)
        
        # If we have a previous path, check if file changed from hidden to visible
        if previous_path:
            previous_filename = os.path.basename(previous_path)
            if previous_filename.startswith('.') and not filename.startswith('.'):
                log_msg = message or f"Detected change from hidden to visible file: {file_path}"
                logging.info(log_msg)
                return file_path
        
        # Process visible files
        if not filename.startswith('.'):
            return file_path
        else:
            logging.info(f"Skipping hidden file: {file_path}")
            return None
    
    def on_created(self, event):
        if event.is_directory:
            return
        logging.info(f"New file detected: {event.src_path}")
        
        file_to_process = self._should_process_file(event.src_path)
        if file_to_process:
            self.process_image(file_to_process)

    def on_modified(self, event):
        if event.is_directory:
            return
        logging.info(f"File modification detected: {event.src_path}")
        
        # Check if this is a macOS screenshot file that has changed from hidden to visible
        filename = os.path.basename(event.src_path)
        if not filename.startswith('.') and 'Screenshot' in filename:
            # For macOS screenshots, check if there was a hidden version
            dir_path = os.path.dirname(event.src_path)
            hidden_filename = f".{filename}"
            hidden_path = os.path.join(dir_path, hidden_filename)
            
            # If we recently saw a hidden version of this file, treat it as a transition
            if os.path.exists(hidden_path):
                logging.info(f"Detected potential macOS screenshot becoming visible: {event.src_path}")
                previous_path = hidden_path
            else:
                previous_path = None
        else:
            previous_path = None
        
        file_to_process = self._should_process_file(event.src_path, previous_path)
        if file_to_process:
            self.process_image(file_to_process)
            
    def on_moved(self, event):
        if event.is_directory:
            return
        # Capture file rename/move events
        logging.info(f"File moved/renamed: {event.src_path} -> {event.dest_path}")
        
        message = f"Detected rename from hidden to visible file (likely a macOS screenshot): {event.dest_path}"
        file_to_process = self._should_process_file(event.dest_path, event.src_path, message)
        if file_to_process:
            self.process_image(file_to_process)

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
                temp_output_path = output_path + '.temp'
                
                if CONVERT_TO_WEBP:
                    logging.info("Saving in WebP format")
                    if LOSSLESS:
                        logging.info("Using lossless compression mode")
                        img.save(temp_output_path, 'WEBP', lossless=True)
                    else:
                        logging.info(f"Using lossy compression mode, quality: {COMPRESSION_QUALITY}")
                        img.save(temp_output_path, 'WEBP', quality=COMPRESSION_QUALITY)
                else:
                    logging.info(f"Saving in original format ({ext})")
                    # For JPEG images, always use lossy compression with optimize=True
                    if ext.lower() in ('.jpg', '.jpeg'):
                        # For JPEG images, use progressive format and dynamic quality based on file size
                        logging.info(f"Using optimized JPEG compression with progressive format")
                        if original_size > 1024 * 1024:  # For images larger than 1MB
                            actual_quality = min(COMPRESSION_QUALITY, 85)  # Cap quality at 85 for large images
                        else:
                            actual_quality = COMPRESSION_QUALITY
                        logging.info(f"Using JPEG quality: {actual_quality}")
                        img.save(temp_output_path, 'JPEG', quality=actual_quality, optimize=True, progressive=True)
                    else:
                        # Get the original format for saving
                        original_format = img.format or 'PNG'  # Default to PNG if format is None
                        if LOSSLESS:
                            logging.info("Using lossless compression mode")
                            img.save(temp_output_path, format=original_format, quality=100, optimize=True)
                        else:
                            logging.info(f"Using lossy compression mode, quality: {COMPRESSION_QUALITY}")
                            img.save(temp_output_path, format=original_format, quality=COMPRESSION_QUALITY, optimize=True)
                
                # Compare sizes and keep the smaller file
                temp_size = os.path.getsize(temp_output_path)
                if temp_size >= original_size:
                    logging.info("Compressed file is larger than original, keeping original file")
                    os.remove(temp_output_path)
                    import shutil
                    shutil.copy2(source_path, output_path)
                else:
                    os.rename(temp_output_path, output_path)

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
    # Use PollingObserver instead of default Observer for better compatibility with Docker volumes on macOS
    event_handler = ImageHandler()
    from watchdog.observers.polling import PollingObserver
    observer = PollingObserver(timeout=1)  # 1 second polling interval
    observer.schedule(event_handler, SOURCE_DIR, recursive=False)
    observer.start()
    logging.info("Using polling observer for better Docker volume compatibility")

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