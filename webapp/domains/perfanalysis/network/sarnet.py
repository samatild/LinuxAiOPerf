"""
Network domain processor for sar network data.
"""

import os
import tempfile
import logging
from typing import List
import pandas as pd
import plotly.graph_objects as go

from core.base import BaseDataProcessor, DataProcessorError
from core.datetime_utils import (parse_collection_date, enrich_timestamps,
                                 normalize_ampm_timestamps)


class NetworkProcessor(BaseDataProcessor):
    """
    Processor for network performance data from sar network.
    """
    def __init__(self, input_file: str, output_dir: str = ".",
                 logger: logging.Logger = None):
        super().__init__(input_file, output_dir, logger)
        self.temp_file = None

    def extract_header(self) -> str:
        """Extract header from sar network data."""
        try:
            with open(self.input_file, 'r') as f:
                for line in f:
                    if "IFACE" in line:
                        # Drop AM/PM tokens before renaming first column so
                        # RHEL 12-hour timestamps don't inject a spurious
                        # column (e.g. "12:31:29 PM IFACE …" → "Timestamp IFACE …")
                        columns = [c for c in line.split()
                                   if c.upper() not in ('AM', 'PM')]
                        columns[0] = "Timestamp"
                        return " ".join(columns).strip()
            raise DataProcessorError(
                "No valid header found in sar network file")
        except IOError as e:
            raise DataProcessorError(f"Failed to read sar network file: {e}")

    def filter_data_lines(self) -> List[str]:
        """Filter sar network data lines."""
        filtered_lines = []
        try:
            with open(self.input_file, 'r') as f:
                for line in f:
                    # Skip header lines, Linux info, and empty lines
                    if ("IFACE" not in line and
                            "Linux" not in line and
                            line.strip()):
                        # Convert HH:MM:SS AM/PM to 24-hour so the timestamp
                        # column count stays consistent with the header
                        cleaned_line = normalize_ampm_timestamps(line).strip()
                        filtered_lines.append(cleaned_line)
            return filtered_lines
        except IOError as e:
            raise DataProcessorError(f"Failed to filter sar network data: {e}")

    def process_data(self) -> pd.DataFrame:
        """Process sar network data into DataFrame."""
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
            raise DataProcessorError(
                f"Failed to process sar network data: {e}")

    def create_plots(self, df: pd.DataFrame) -> List[go.Figure]:
        """Create network performance plots."""
        try:
            if df.empty:
                self.logger.warning("No data available for network plots")
                return []

            # Convert rxkB/s and txkB/s to MB/s
            if 'rxkB/s' in df.columns:
                df['rxkB/s'] = df['rxkB/s'] / 1024
                df.rename(columns={'rxkB/s': 'rxMB/s'}, inplace=True)

            if 'txkB/s' in df.columns:
                df['txkB/s'] = df['txkB/s'] / 1024
                df.rename(columns={'txkB/s': 'txMB/s'}, inplace=True)

            # Get column references
            time_col = df.columns[0]  # Timestamp column
            interface_col = df.columns[1]  # Interface column
            metric_cols = df.columns[2:]  # Metric columns

            # Convert timestamp column to datetime, enriching with the actual
            # collection date from info.txt to avoid using today's date.
            ts_series = df[time_col].astype(str)
            collection_date = parse_collection_date(self.input_file)
            if collection_date is not None:
                ts_series = enrich_timestamps(ts_series, collection_date)
                ts_fmt = '%Y-%m-%d %H:%M:%S'
            else:
                ts_fmt = '%H:%M:%S'
            df[time_col] = pd.to_datetime(ts_series, format=ts_fmt)

            figures = []

            # Create a plot for each metric
            for metric in metric_cols:
                fig = go.Figure()

                # Add traces for each interface
                for interface in df[interface_col].unique():
                    interface_data = df[df[interface_col] == interface]
                    x = interface_data[time_col]  # Timestamp
                    y = pd.to_numeric(interface_data[metric])  # Metric values
                    fig.add_trace(
                        go.Scatter(
                            x=x, y=y, mode='lines',
                            name=interface
                        )
                    )

                # Apply layout
                layout = self.get_common_plot_layout(
                    title=f'Network {metric}',
                    y_title='Value'
                )
                fig.update_layout(**layout)

                figures.append(fig)

            return figures
        except Exception as e:
            raise DataProcessorError(f"Failed to create network plots: {e}")

    def __del__(self):
        """Clean up temporary file if it exists."""
        if (hasattr(self, 'temp_file') and self.temp_file and
                os.path.exists(self.temp_file.name)):
            try:
                os.unlink(self.temp_file.name)
            except OSError:
                pass
