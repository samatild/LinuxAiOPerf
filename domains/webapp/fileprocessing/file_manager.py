"""
File Manager for handling file upload, extraction, and management operations.
"""

import os
import tarfile
import shutil
import glob
import logging
from typing import Optional, Tuple


class FileManager:
    """
    Handles file upload, extraction, and management operations.
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
    
    def create_unique_directory(self, base_path: str) -> Tuple[str, str]:
        """
        Create a unique directory for file processing.
        
        Args:
            base_path: Base path for creating unique directories
            
        Returns:
            Tuple of (unique_id, unique_dir_path)
        """
        import os
        unique_id = os.urandom(24).hex()
        unique_dir = os.path.join(base_path, unique_id)
        os.makedirs(unique_dir)
        self.logger.info(f"Created unique directory: {unique_dir}")
        return unique_id, unique_dir
    
    def save_uploaded_file(self, uploaded_file, unique_dir: str) -> str:
        """
        Save uploaded file to unique directory.
        
        Args:
            uploaded_file: Flask uploaded file object
            unique_dir: Directory to save the file
            
        Returns:
            Path to saved file
        """
        tar_path = os.path.join(unique_dir, uploaded_file.filename)
        uploaded_file.save(tar_path)
        self.logger.info(f"Saved uploaded file: {tar_path}")
        return tar_path
    
    def extract_tarfile(self, tar_path: str, extract_dir: str) -> None:
        """
        Extract tarfile to specified directory.
        
        Args:
            tar_path: Path to tarfile
            extract_dir: Directory to extract to
            
        Raises:
            tarfile.ReadError: If tarfile is corrupted or invalid
        """
        try:
            with tarfile.open(tar_path, 'r:gz') as tar_ref:
                tar_ref.extractall(extract_dir)
                self.logger.info(f"Extracted tarfile to: {extract_dir}")
        except tarfile.ReadError as e:
            self.logger.error(f"Failed to extract tarfile: {e}")
            raise
    
    def reorganize_extracted_files(self, unique_dir: str) -> None:
        """
        Reorganize extracted files by moving contents from subdirectories.
        
        Args:
            unique_dir: Directory containing extracted files
        """
        os.chdir(unique_dir)
        os.system('mv *_linuxaioperfcheck/* .')
        self.logger.info("Reorganized extracted files")
    
    def copy_script_file(self, source_base: str, unique_dir: str) -> str:
        """
        Copy the main script to the processing directory.
        
        Args:
            source_base: Base source directory
            unique_dir: Destination directory
            
        Returns:
            Path to copied script
        """
        script_path = os.path.join(source_base, 'domains', 'webapp', 'execution', 'linuxaioperf.py')
        script_dest = os.path.join(unique_dir, 'linuxaioperf.py')
        shutil.copyfile(script_path, script_dest)
        self.logger.info(f"Copied script to: {script_dest}")
        return script_dest
    
    def copy_domain_directories(self, source_base: str, unique_dir: str) -> None:
        """
        Copy core and domains directories to processing directory.
        
        Args:
            source_base: Base source directory
            unique_dir: Destination directory
        """
        # Copy core directory
        core_path = os.path.join(source_base, 'core')
        core_dest = os.path.join(unique_dir, 'core')
        if os.path.exists(core_path):
            shutil.copytree(core_path, core_dest)
            self.logger.info("Copied core directory")
        
        # Copy domains directory
        domains_path = os.path.join(source_base, 'domains')
        domains_dest = os.path.join(unique_dir, 'domains')
        if os.path.exists(domains_path):
            shutil.copytree(domains_path, domains_dest)
            self.logger.info("Copied domains directory")
    
    def process_upload(self, uploaded_file, base_path: str, source_base: str) -> Tuple[str, str]:
        """
        Complete file processing workflow.
        
        Args:
            uploaded_file: Flask uploaded file object
            base_path: Base path for unique directories
            source_base: Base path for source files
            
        Returns:
            Tuple of (unique_id, unique_dir)
            
        Raises:
            tarfile.ReadError: If uploaded file is not a valid tarfile
        """
        # Create unique directory
        unique_id, unique_dir = self.create_unique_directory(base_path)
        
        # Save uploaded file
        tar_path = self.save_uploaded_file(uploaded_file, unique_dir)
        
        # Extract tarfile
        self.extract_tarfile(tar_path, unique_dir)
        
        # Reorganize files
        self.reorganize_extracted_files(unique_dir)
        
        # Copy script
        self.copy_script_file(source_base, unique_dir)
        
        # Copy domain directories
        self.copy_domain_directories(source_base, unique_dir)
        
        return unique_id, unique_dir
