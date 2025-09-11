"""
Disk I/O statistics processor for iostat data (per-device view).
"""

import os
import tempfile
import logging
from typing import List, Dict, Any, Tuple
import pandas as pd
import plotly.graph_objects as go

from core.base import BaseDataProcessor, DataProcessorError


class DiskIostatProcessor(BaseDataProcessor):
    """
    Processor for disk performance data from iostat (per-device view).
    """
    
    def __init__(self, input_file: str, output_dir: str = ".", logger: logging.Logger = None):
        super().__init__(input_file, output_dir, logger)
        self.temp_file = None
    
    def extract_header(self) -> str:
        """Extract header from iostat data."""
        try:
            with open(self.input_file, 'r') as f:
                for line in f:
                    if "Device" in line:
                        return line.strip()
            raise DataProcessorError("No valid header found in iostat file")
        except IOError as e:
            raise DataProcessorError(f"Failed to read iostat file: {e}")
    
    def filter_data_lines(self) -> List[str]:
        """Filter iostat data lines for disk devices."""
        filtered_lines = []
        try:
            with open(self.input_file, 'r') as f:
                for line in f:
                    # Filter for disk devices (sd*, dm-*, nvme*)
                    if any(device_type in line for device_type in ['sd', 'dm-', 'nvme']):
                        filtered_lines.append(line.strip())
            return filtered_lines
        except IOError as e:
            raise DataProcessorError(f"Failed to filter iostat data: {e}")
    
    def process_data(self) -> pd.DataFrame:
        """Process iostat data into DataFrame."""
        try:
            # Create temporary file for cleaned data
            self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv')
            
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
            raise DataProcessorError(f"Failed to process iostat data: {e}")
    
    def create_plots(self, df: pd.DataFrame) -> List[go.Figure]:
        """Create disk performance plots (per-device view)."""
        try:
            if df.empty:
                self.logger.warning("No data available for disk plots")
                return []
            
            # Get device labels and metric columns
            device_labels = df.iloc[:, 1]  # Second column contains device names
            metric_cols = df.columns[2:]   # Skip timestamp and device columns
            
            # Convert timestamp column to datetime
            df[df.columns[0]] = pd.to_datetime(
                df[df.columns[0]], format="%Y-%m-%d-%H:%M:%S"
            )
            
            figures = []
            
            # Create a plot for each device
            for device in device_labels.unique():
                fig = go.Figure()
                
                # Filter data for this device
                device_data = df[df[df.columns[1]] == device]
                
                # Add traces for each metric
                for col in metric_cols:
                    x = device_data[device_data.columns[0]]  # Timestamp
                    y = pd.to_numeric(device_data[col])      # Metric values
                    fig.add_trace(
                        go.Scatter(
                            x=x, y=y, mode='lines', 
                            name=col
                        )
                    )
                
                # Apply layout
                layout = self.get_common_plot_layout(
                    title=f'Disk Metrics - {device}',
                    y_title='Value'
                )
                fig.update_layout(**layout)
                
                figures.append(fig)
            
            return figures
            
        except Exception as e:
            raise DataProcessorError(f"Failed to create disk plots: {e}")
    
    def __del__(self):
        """Clean up temporary file if it exists."""
        if hasattr(self, 'temp_file') and self.temp_file and os.path.exists(self.temp_file.name):
            try:
                os.unlink(self.temp_file.name)
            except:
                pass
