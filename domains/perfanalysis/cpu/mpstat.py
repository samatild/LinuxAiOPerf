"""
CPU domain processor for mpstat data.
"""

import os
import tempfile
import logging
from typing import List, Dict, Any, Tuple
import pandas as pd
import plotly.graph_objects as go

from core.base import BaseDataProcessor, DataProcessorError


class CPUProcessor(BaseDataProcessor):
    """
    Processor for CPU performance data from mpstat.
    """
    
    def __init__(self, input_file: str, output_dir: str = ".", logger: logging.Logger = None):
        super().__init__(input_file, output_dir, logger)
        self.temp_file = None
    
    def extract_header(self) -> str:
        """Extract header from mpstat data."""
        try:
            with open(self.input_file, 'r') as f:
                for line in f:
                    if "Linux" not in line and "Average" not in line and line.strip():
                        # First non-header line contains the column structure
                        return line.strip()
            raise DataProcessorError("No valid header found in mpstat file")
        except IOError as e:
            raise DataProcessorError(f"Failed to read mpstat file: {e}")
    
    def filter_data_lines(self) -> List[str]:
        """Filter and clean mpstat data lines."""
        filtered_lines = []
        try:
            with open(self.input_file, 'r') as f:
                for line in f:
                    if "Linux" not in line and "Average" not in line and line.strip():
                        # Remove AM/PM indicators
                        cleaned_line = line.replace("AM", "").replace("PM", "").strip()
                        filtered_lines.append(cleaned_line)
            return filtered_lines
        except IOError as e:
            raise DataProcessorError(f"Failed to filter mpstat data: {e}")
    
    def process_data(self) -> pd.DataFrame:
        """Process mpstat data into DataFrame."""
        try:
            # Create temporary file for cleaned data
            self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt')
            
            # Write filtered data to temp file
            data_lines = self.filter_data_lines()
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
            raise DataProcessorError(f"Failed to process mpstat data: {e}")
    
    def create_plots(self, df: pd.DataFrame) -> List[go.Figure]:
        """Create CPU performance plots."""
        try:
            if df.empty:
                self.logger.warning("No data available for CPU plots")
                return []
            
            y_cols = df.columns[2:]  # Skip timestamp and CPU columns
            df_all = df[df[df.columns[1]] == 'all']
            
            figures = []
            
            # Create "All CPU Usage" plot
            if not df_all.empty:
                fig_all = go.Figure()
                for col in y_cols:
                    fig_all.add_trace(
                        go.Scatter(
                            x=df_all[df_all.columns[0]],
                            y=pd.to_numeric(df_all[col]),
                            mode='lines',
                            name=f"{col}"
                        )
                    )
                
                fig_all.update_layout(
                    title='All CPU Usage Data',
                    xaxis_title='Timestamp',
                    height=800,
                    template="seaborn"
                )
                figures.append(fig_all)
            
            # Create individual metric plots
            df_numeric = df[df[df.columns[1]].str.contains(r'^\d+$|^all$', regex=True)]
            
            for col in y_cols:
                fig = go.Figure()
                
                # Group by CPU and create traces
                for cpu, data in sorted(
                    df_numeric.groupby(df_numeric.columns[1]),
                    key=lambda x: int(x[0]) if x[0] != 'all' else -1
                ):
                    x = data[data.columns[0]]
                    y = pd.to_numeric(data[col])
                    fig.add_trace(
                        go.Scatter(
                            x=x, y=y, mode='lines', 
                            name=f"CPU - {cpu}"
                        )
                    )
                
                # Apply common layout
                layout = self.get_common_plot_layout(
                    title=f'{col} - CPU Usage Data',
                    y_title=col
                )
                layout['height'] = 800
                fig.update_layout(**layout)
                
                # Add range selector
                fig.update_xaxes(rangeselector=dict(buttons=list([
                    dict(count=5, label="5m", step="minute", stepmode="backward"),
                    dict(count=1, label="1m", step="minute", stepmode="backward"),
                    dict(count=30, label="30s", step="second", stepmode="backward"),
                    dict(count=1, label="1s", step="second", stepmode="backward"),
                    dict(step="all")
                ])))
                
                figures.append(fig)
            
            return figures
            
        except Exception as e:
            raise DataProcessorError(f"Failed to create CPU plots: {e}")
    
    def __del__(self):
        """Clean up temporary file if it exists."""
        if hasattr(self, 'temp_file') and self.temp_file and os.path.exists(self.temp_file.name):
            try:
                os.unlink(self.temp_file.name)
            except:
                pass
