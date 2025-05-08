import os
import shutil
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def organize_pdfs():
    """Organize PDFs from multiple directories into a single directory."""
    # Create the target directory
    target_dir = "docs/insurance"
    os.makedirs(target_dir, exist_ok=True)
    
    # Source directories
    source_dirs = [
        "docs/insurance",
        "docs/Insurance PDFs"
    ]
    
    # Process each source directory
    for source_dir in source_dirs:
        if not os.path.exists(source_dir):
            logger.warning(f"Source directory {source_dir} does not exist, skipping...")
            continue
            
        logger.info(f"Processing directory: {source_dir}")
        
        # Walk through the directory
        for root, _, files in os.walk(source_dir):
            for file in files:
                if file.lower().endswith('.pdf'):
                    source_path = os.path.join(root, file)
                    target_path = os.path.join(target_dir, file)
                    
                    # If file already exists in target, add a number to the filename
                    if os.path.exists(target_path):
                        base, ext = os.path.splitext(file)
                        counter = 1
                        while os.path.exists(target_path):
                            target_path = os.path.join(target_dir, f"{base}_{counter}{ext}")
                            counter += 1
                    
                    try:
                        shutil.copy2(source_path, target_path)
                        logger.info(f"Copied {source_path} to {target_path}")
                    except Exception as e:
                        logger.error(f"Error copying {source_path}: {str(e)}")
    
    logger.info("PDF organization completed!")

if __name__ == "__main__":
    organize_pdfs() 