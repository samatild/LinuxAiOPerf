"""
Base classes and interfaces for Linux AIO Performance Checker data processors.
"""

import os
import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple
import pandas as pd
import plotly.graph_objects as go


class DataProcessorError(Exception):
    """Base exception for data processing errors."""
    pass


class FileNotFoundError(DataProcessorError):
    """Raised when required data files are not found."""
    pass


class DataValidationError(DataProcessorError):
    """Raised when data validation fails."""
    pass


class BaseDataProcessor(ABC):
    """
    Abstract base class for all data processors.

    This class defines the common interface and shared functionality
    for processing different types of system performance data.
    """

    def __init__(
        self,
        input_file: str,
        output_dir: str = ".",
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize the data processor.

        Args:
            input_file: Path to the input data file
            output_dir: Directory for temporary output files
            logger: Logger instance (optional)
        """
        self.input_file = input_file
        self.output_dir = output_dir
        self.logger = logger or self._setup_logger()
        self._validate_input_file()

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

    def _validate_input_file(self) -> None:
        """Validate that the input file exists and is readable."""
        if not os.path.exists(self.input_file):
            raise FileNotFoundError(f"Input file not found: {self.input_file}")
        if not os.access(self.input_file, os.R_OK):
            raise DataProcessorError(
                f"Cannot read input file: {self.input_file}"
            )

        if os.path.getsize(self.input_file) == 0:
            raise DataValidationError(
                f"Input file is empty: {self.input_file}"
            )

    @abstractmethod
    def extract_header(self) -> str:
        """
        Extract the header line from the input file.

        Returns:
            Header line as a string
        """
        pass

    @abstractmethod
    def filter_data_lines(self) -> List[str]:
        """
        Filter and clean data lines from the input file.

        Returns:
            List of filtered data lines
        """
        pass

    @abstractmethod
    def process_data(self) -> pd.DataFrame:
        """
        Process the filtered data into a pandas DataFrame.

        Returns:
            Processed DataFrame
        """
        pass

    @abstractmethod
    def create_plots(self, df: pd.DataFrame) -> List[go.Figure]:
        """
        Create plotly figures from the processed data.

        Args:
            df: Processed DataFrame

        Returns:
            List of plotly figures
        """
        pass

    def write_filtered_data(self, output_file: str, header: str,
                            data_lines: List[str]) -> None:
        """
        Write filtered data to a temporary file.

        Args:
            output_file: Path to output file
            header: Header line
            data_lines: List of data lines
        """
        try:
            with open(output_file, 'w') as f:
                f.write(header + '\n')
                for line in data_lines:
                    f.write(line + '\n')
            self.logger.debug(f"Written filtered data to {output_file}")
        except IOError as e:
            raise DataProcessorError(f"Failed to write filtered data: {e}")

    def get_common_plot_layout(self, title: str, x_title: str = "Timestamp",
                               y_title: str = "Value") -> Dict[str, Any]:
        """
        Get common plot layout configuration.

        Args:
            title: Plot title
            x_title: X-axis title
            y_title: Y-axis title

        Returns:
            Layout configuration dictionary
        """
        return {
            'template': "seaborn",
            'title': title,
            'xaxis_title': x_title,
            'yaxis_title': y_title,
            'height': 500,
            'xaxis': {
                'rangeselector': {
                    'buttons': [
                        dict(count=5, label="5m", step="minute",
                             stepmode="backward"),
                        dict(count=1, label="1m", step="minute",
                             stepmode="backward"),
                        dict(count=30, label="30s", step="second",
                             stepmode="backward"),
                        dict(count=1, label="1s", step="second",
                             stepmode="backward"),
                        dict(step="all")
                    ]
                },
                'type': "date",
                'tickformat': "%Y-%m-%d %H:%M:%S"
            }
        }

    def process(self) -> Tuple[pd.DataFrame, List[go.Figure]]:
        """
        Main processing pipeline.

        Returns:
            Tuple of (processed_dataframe, plotly_figures)
        """
        try:
            self.logger.info(f"Starting processing of {self.input_file}")

            # Extract header
            header = self.extract_header()
            self.logger.debug(f"Extracted header: {header}")

            # Filter data lines
            data_lines = self.filter_data_lines()
            self.logger.debug(f"Filtered {len(data_lines)} data lines")

            # Process data
            df = self.process_data()
            self.logger.debug(f"Processed data shape: {df.shape}")

            # Create plots
            figures = self.create_plots(df)
            self.logger.info(f"Created {len(figures)} plots")

            return df, figures
        except Exception as e:
            self.logger.error(f"Processing failed: {e}")
            raise DataProcessorError(
                f"Failed to process {self.input_file}: {e}")


class SystemInfoProcessor(BaseDataProcessor):
    """
    Base class for system information processors (non-time-series data).
    """
    @abstractmethod
    def extract_system_info(self) -> Dict[str, Any]:
        """
        Extract system information from the input file.

        Returns:
            Dictionary containing system information
        """
        pass

    def process(self) -> Dict[str, Any]:
        """
        Process system information.

        Returns:
            Dictionary containing system information
        """
        try:
            self.logger.info(
                f"Starting system info processing of {self.input_file}")
            return self.extract_system_info()
        except Exception as e:
            self.logger.error(f"System info processing failed: {e}")
            raise DataProcessorError(
                f"Failed to process system info {self.input_file}: {e}")


class ProcessInfoProcessor(BaseDataProcessor):
    """
    Base class for process information processors (pidstat, top, iotop).
    """
    @abstractmethod
    def extract_process_data(self) -> Tuple[Dict[str, str], set, str]:
        """
        Extract process data organized by timestamps.

        Returns:
            Tuple of (chunks_dict, timestamps_set, js_object_string)
        """
        pass

    def process(self) -> Tuple[Dict[str, str], set, str]:
        """
        Process process information.

        Returns:
            Tuple of (chunks_dict, timestamps_set, js_object_string)
        """
        try:
            self.logger.info(
                f"Starting process info processing of {self.input_file}")
            return self.extract_process_data()
        except Exception as e:
            self.logger.error(f"Process info processing failed: {e}")
            raise DataProcessorError(
                f"Failed to process process info {self.input_file}: {e}")
