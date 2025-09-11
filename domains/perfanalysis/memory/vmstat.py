"""
Memory domain processor for vmstat data.
"""

import os
import tempfile
import logging
from typing import List
import pandas as pd
import plotly.graph_objects as go

from core.base import BaseDataProcessor, DataProcessorError


class MemoryProcessor(BaseDataProcessor):
    """
    Processor for memory performance data from vmstat.
    """
    def __init__(self, input_file: str, output_dir: str = ".",
                 logger: logging.Logger = None):
        super().__init__(input_file, output_dir, logger)
        self.temp_file = None

    def extract_header(self) -> str:
        """Extract header from vmstat data."""
        try:
            with open(self.input_file, 'r') as f:
                for line in f:
                    if "swpd" in line:
                        return line.strip()
            raise DataProcessorError(
                "No valid header found in vmstat file")
        except IOError as e:
            raise DataProcessorError(f"Failed to read vmstat file: {e}")

    def filter_data_lines(self) -> List[str]:
        """Filter vmstat data lines."""
        filtered_lines = []
        try:
            with open(self.input_file, 'r') as f:
                for line in f:
                    # Skip header lines and empty lines
                    if ("procs" not in line and "swpd" not in line and
                            line.strip()):
                        filtered_lines.append(line.strip())
            return filtered_lines
        except IOError as e:
            raise DataProcessorError(f"Failed to filter vmstat data: {e}")

    def process_data(self) -> pd.DataFrame:
        """Process vmstat data into DataFrame."""
        try:
            # Create temporary file for cleaned data
            self.temp_file = tempfile.NamedTemporaryFile(
                mode='w', delete=False, suffix='.csv')

            # Write filtered data to temp file
            header = self.extract_header()
            data_lines = self.filter_data_lines()

            self.temp_file.write(header + '\n')
            for line in data_lines:
                self.temp_file.write(line + '\n')
            self.temp_file.close()

            # Read into DataFrame
            df = pd.read_csv(self.temp_file.name, sep=r'\s+')

            # Clean up temp file
            os.unlink(self.temp_file.name)
            self.temp_file = None

            return df
        except Exception as e:
            # Clean up temp file on error
            if self.temp_file and os.path.exists(self.temp_file.name):
                os.unlink(self.temp_file.name)
            raise DataProcessorError(f"Failed to process vmstat data: {e}")

    def create_plots(self, df: pd.DataFrame) -> List[go.Figure]:
        """Create memory performance plots."""
        try:
            if df.empty:
                self.logger.warning("No data available for memory plots")
                return []

            # Convert timestamp column to datetime
            df[df.columns[0]] = pd.to_datetime(
                df[df.columns[0]], format="%Y-%m-%d-%H:%M:%S"
            )

            # Create a single figure for memory metrics
            fig = go.Figure()

            # Define memory columns to plot
            memory_cols = ['swpd', 'free', 'inact', 'active']

            for col in memory_cols:
                if col in df.columns:
                    # Convert to GB (assuming values are in KB)
                    y = pd.to_numeric(df[col]) / 1048576
                    fig.add_trace(
                        go.Scatter(
                            x=df[df.columns[0]],
                            y=y,
                            mode='lines',
                            name=col
                        )
                    )

            # Apply layout
            layout = self.get_common_plot_layout(
                title='Memory Utilization',
                y_title='Value (GB)'
            )
            layout['height'] = 900
            fig.update_layout(**layout)

            return [fig]
        except Exception as e:
            raise DataProcessorError(f"Failed to create memory plots: {e}")

    def __del__(self):
        """Clean up temporary file if it exists."""
        if (hasattr(self, 'temp_file') and self.temp_file and
                os.path.exists(self.temp_file.name)):
            try:
                os.unlink(self.temp_file.name)
            except OSError:
                pass
