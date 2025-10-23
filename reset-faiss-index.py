#!/usr/bin/env python3
"""
Script to reset the FAISS index and chunk map to fix compatibility issues
"""

import os
import shutil
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def reset_faiss_files():
    """Reset FAISS index and related files"""
    
    files_to_reset = [
        "faiss_index.bin",
        "chunk_map.pkl",
        "documents.pkl"
    ]
    
    backup_dir = "backup_faiss_files"
    
    try:
        # Create backup directory if it doesn't exist
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
            logger.info(f"Created backup directory: {backup_dir}")
        
        # Backup existing files
        for file_name in files_to_reset:
            if os.path.exists(file_name):
                backup_path = os.path.join(backup_dir, file_name)
                shutil.copy2(file_name, backup_path)
                logger.info(f"Backed up {file_name} to {backup_path}")
        
        # Remove existing files
        for file_name in files_to_reset:
            if os.path.exists(file_name):
                os.remove(file_name)
                logger.info(f"Removed {file_name}")
        
        logger.info("FAISS files reset successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error resetting FAISS files: {str(e)}")
        return False

if __name__ == "__main__":
    reset_faiss_files()