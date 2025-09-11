"""
System information processor for handling system configuration data.
"""

import os
import logging
from typing import Dict, Any, Optional

from core.base import DataProcessorError


class SystemInfoProcessor:
    """
    Processor for system information and configuration data.
    
    This class doesn't inherit from BaseDataProcessor because it doesn't
    process a single input file - it reads from multiple system files.
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize the system info processor.
        
        Args:
            logger: Logger instance (optional)
        """
        self.logger = logger or self._setup_logger()
    
    def _setup_logger(self) -> logging.Logger:
        """Setup logger for this processor."""
        logger = logging.getLogger(f"{self.__class__.__name__}")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    # This class doesn't need the abstract methods from BaseDataProcessor
    # because it doesn't process a single input file
    
    def extract_system_info(self) -> Dict[str, Any]:
        """
        Extract system information from various system files.
        
        Returns:
            Dictionary containing system information
        """
        try:
            system_info = {}
            
            # Runtime information
            if os.path.exists("info.txt"):
                with open("info.txt", "r") as file:
                    system_info['runtime_info'] = file.read()
            
            # OS release information
            if os.path.exists("os-release"):
                with open("os-release", "r") as file:
                    system_info['os_release'] = file.read()
            
            # Hardware information
            if os.path.exists("lshw.txt"):
                with open("lshw.txt", "r") as file:
                    system_info['hardware_info'] = file.read()
            
            # DMI decode information
            if os.path.exists("dmidecode.txt"):
                with open("dmidecode.txt", "r") as file:
                    system_info['dmi_info'] = file.read()
            
            # Storage information
            if os.path.exists("lsscsi.txt"):
                with open("lsscsi.txt", "r") as file:
                    system_info['scsi_info'] = file.read()
            
            if os.path.exists("lsblk-f.txt"):
                with open("lsblk-f.txt", "r") as file:
                    system_info['block_devices'] = file.read()
            
            if os.path.exists("df-h.txt"):
                with open("df-h.txt", "r") as file:
                    system_info['disk_usage'] = file.read()
            
            if os.path.exists("ls-l-dev-mapper.txt"):
                with open("ls-l-dev-mapper.txt", "r") as file:
                    system_info['device_mapper'] = file.read()
            
            if os.path.exists("parted-l.txt"):
                with open("parted-l.txt", "r") as file:
                    system_info['partition_info'] = file.read()
            
            # CPU and memory information
            if os.path.exists("lscpu.txt"):
                with open("lscpu.txt", "r") as file:
                    system_info['cpu_info'] = file.read()
            
            if os.path.exists("meminfo.txt"):
                with open("meminfo.txt", "r") as file:
                    system_info['memory_info'] = file.read()
            
            # Kernel information
            if os.path.exists("sysctl.txt"):
                with open("sysctl.txt", "r") as file:
                    system_info['kernel_params'] = file.read()
            
            if os.path.exists("lsmod.txt"):
                with open("lsmod.txt", "r") as file:
                    system_info['kernel_modules'] = file.read()
            
            # Security information
            if os.path.exists("apparmor_status.txt"):
                with open("apparmor_status.txt", "r") as file:
                    system_info['apparmor_status'] = file.read()
            elif os.path.exists("sestatus.txt"):
                with open("sestatus.txt", "r") as file:
                    system_info['selinux_status'] = file.read()
            
            return system_info
            
        except Exception as e:
            raise DataProcessorError(f"Failed to extract system information: {e}")
    
    def get_file_contents(self, file_path: str) -> str:
        """
        Get contents of a system file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            File contents as string
        """
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as file:
                    return file.read()
            else:
                return f"File '{file_path}' not found"
        except Exception as e:
            return f"Error reading file '{file_path}': {e}"
