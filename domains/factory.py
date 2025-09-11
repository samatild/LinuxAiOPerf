"""
Factory for creating domain-specific data processors.
"""

import logging
from typing import Dict, Any, Optional
from core.base import BaseDataProcessor, DataProcessorError

# Performance Analysis domains
from .perfanalysis.cpu.mpstat import CPUProcessor
from .perfanalysis.disk.diskiostat import DiskIostatProcessor
from .perfanalysis.disk.diskmetrics import DiskMetricsProcessor
from .perfanalysis.disk.diskhighres import DiskHighResProcessor
from .perfanalysis.memory.vmstat import MemoryProcessor
from .perfanalysis.network.sarnet import NetworkProcessor

# Process Information domains
# NOTE: Process info and system config processors are not used in the current implementation.
# They only provide legacy function wrappers for backward compatibility.

# HTML Generation is handled by the original functions/generate_html.py
# which uses the domain modules for legacy function wrappers


class ProcessorFactory:
    """
    Factory class for creating domain-specific data processors.
    """
    
    # Registry of available processors
    _processors = {
        # Performance Analysis processors
        'cpu': CPUProcessor,
        'diskiostat': DiskIostatProcessor,
        'diskmetrics': DiskMetricsProcessor,
        'diskhighres': DiskHighResProcessor,
        'memory': MemoryProcessor,
        'network': NetworkProcessor,
        
        # Process Information processors
        # NOTE: Process info and system config processors are not used in the current implementation.
        # They only provide legacy function wrappers for backward compatibility.
        
        # HTML Generation is handled by functions/generate_html.py
    }
    
    @classmethod
    def create_processor(
        self, 
        processor_type: str, 
        input_file: str, 
        output_dir: str = ".", 
        logger: Optional[logging.Logger] = None
    ) -> BaseDataProcessor:
        """
        Create a data processor instance.
        
        Args:
            processor_type: Type of processor to create
            input_file: Path to input data file
            output_dir: Directory for output files
            logger: Logger instance
            
        Returns:
            Data processor instance
            
        Raises:
            DataProcessorError: If processor type is not supported
        """
        if processor_type not in self._processors:
            available_types = ', '.join(self._processors.keys())
            raise DataProcessorError(
                f"Unknown processor type: {processor_type}. "
                f"Available types: {available_types}"
            )
        
        processor_class = self._processors[processor_type]
        return processor_class(input_file, output_dir, logger)
    
    @classmethod
    def get_available_processors(cls) -> Dict[str, str]:
        """
        Get list of available processor types and their descriptions.
        
        Returns:
            Dictionary mapping processor types to descriptions
        """
        return {
            # Performance Analysis processors
            'cpu': 'CPU performance data from mpstat',
            'diskiostat': 'Disk I/O statistics from iostat (per device)',
            'diskmetrics': 'Disk metrics from iostat (per metric)',
            'diskhighres': 'High-resolution disk statistics',
            'memory': 'Memory performance data from vmstat',
            'network': 'Network performance data from sar network',
            
            # HTML Generation is handled by functions/generate_html.py
        }
    
    @classmethod
    def register_processor(cls, processor_type: str, processor_class: type) -> None:
        """
        Register a new processor type.
        
        Args:
            processor_type: Name of the processor type
            processor_class: Processor class to register
        """
        if not issubclass(processor_class, BaseDataProcessor):
            raise DataProcessorError(
                f"Processor class must inherit from BaseDataProcessor"
            )
        
        cls._processors[processor_type] = processor_class
