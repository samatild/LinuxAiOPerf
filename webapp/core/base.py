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
                               y_title: str = "Value",
                               disable_axis_si_prefix: bool = False
                               ) -> Dict[str, Any]:
        """
        Get common plot layout configuration.

        Args:
            title: Plot title
            x_title: X-axis title
            y_title: Y-axis title
            disable_axis_si_prefix: When True, prevents Plotly from
                applying its own SI-prefix abbreviation (e.g. "15k") to
                y-axis tick labels. Useful when the underlying values are
                already expressed in a scaled unit (e.g. KB/s), where
                Plotly's auto-abbreviation would stack ambiguously with
                the unit already baked into the axis title.

        Returns:
            Layout configuration dictionary
        """
        layout = {
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

        if disable_axis_si_prefix:
            layout['yaxis'] = {
                'exponentformat': "none",
                'separatethousands': True
            }

        return layout

    @staticmethod
    def scale_throughput_series(
        series: pd.Series, base_unit: str = "KB"
    ) -> Tuple[pd.Series, str]:
        """
        Rescale a throughput series (already expressed in ``base_unit``
        per second) to the largest unit that keeps values in a
        human-readable range, avoiding ambiguity with Plotly's automatic
        SI-prefix axis tick abbreviation (e.g. a raw "15000 KB/s" value
        being displayed on the axis as just "15k", which looks like
        "15 thousand KB/s" rather than the correct "15 MB/s").

        Args:
            series: Numeric series already expressed in ``base_unit``/s.
            base_unit: The unit the input series is already expressed in
                (defaults to "KB", matching iostat's kB/s columns).

        Returns:
            Tuple of (rescaled_series, unit_label) where unit_label is
            e.g. "KB/s", "MB/s" or "GB/s".
        """
        units = ["KB", "MB", "GB", "TB"]
        try:
            start_idx = units.index(base_unit)
        except ValueError:
            start_idx = 0

        max_value = series.abs().max()
        scale = 0
        # Each step up divides by 1024, keeping typical values below 1024
        while (
            pd.notna(max_value)
            and max_value >= 1024
            and start_idx + scale < len(units) - 1
        ):
            max_value /= 1024
            scale += 1

        scaled_series = series / (1024 ** scale) if scale else series
        unit_label = f"{units[start_idx + scale]}/s"
        return scaled_series, unit_label

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
