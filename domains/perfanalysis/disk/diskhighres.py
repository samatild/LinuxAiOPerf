"""
High-resolution disk statistics processor.
"""

from typing import List
import pandas as pd
import plotly.graph_objects as go
import numpy as np

from core.base import BaseDataProcessor, DataProcessorError


class DiskHighResProcessor(BaseDataProcessor):
    """
    Processor for high-resolution disk statistics.
    """
    def extract_header(self) -> str:
        """High-resolution disk stats don't have a traditional header."""
        return ("Timestamp Major Minor Device Reads_Completed Reads_Merged "
                "Sectors_Read Time_Reading Writes_Completed Writes_Merged "
                "Sectors_Written Time_Writing IO_Currently IO_Time "
                "Weighted_IO_Time Discards_Completed Discards_Merged "
                "Sectors_Discarded Time_Discarding Flush_Requests "
                "Time_Flushing")

    def filter_data_lines(self) -> List[str]:
        """Return all lines as they are already filtered."""
        try:
            with open(self.input_file, 'r') as f:
                return [line.strip() for line in f if line.strip()]
        except IOError as e:
            raise DataProcessorError(f"Failed to read disk stats file: {e}")

    def process_data(self) -> pd.DataFrame:
        """Process high-resolution disk statistics."""
        try:
            columns = [
                'Timestamp', 'Major', 'Minor', 'Device',
                'Reads_Completed', 'Reads_Merged', 'Sectors_Read',
                'Time_Reading',
                'Writes_Completed', 'Writes_Merged', 'Sectors_Written',
                'Time_Writing', 'IO_Currently', 'IO_Time', 'Weighted_IO_Time',
                'Discards_Completed', 'Discards_Merged', 'Sectors_Discarded',
                'Time_Discarding', 'Flush_Requests', 'Time_Flushing'
            ]

            df = pd.read_csv(self.input_file, sep=r'\s+', names=columns,
                             skiprows=1)
            df['Timestamp'] = pd.to_datetime(
                df['Timestamp'], format='%Y-%m-%d-%H:%M:%S.%f'
            )
            df.set_index('Timestamp', inplace=True)

            return df
        except Exception as e:
            raise DataProcessorError(f"Failed to process disk stats data: {e}")

    def _calculate_rates(self, device_data: pd.DataFrame,
                         device_name: str) -> pd.DataFrame:
        """
        Calculate IOPS, throughput, and latency from cumulative counters.

        Args:
            device_data: Raw device statistics
            device_name: Name of the device being processed

        Returns:
            Device data with calculated rates
        """
        # Calculate IOPS
        reads_delta = device_data['Reads_Completed'].diff()
        writes_delta = device_data['Writes_Completed'].diff()
        device_data['IOPS'] = reads_delta + writes_delta

        # Calculate throughput (MB/s)
        sectors_read_delta = device_data['Sectors_Read'].diff()
        sectors_write_delta = device_data['Sectors_Written'].diff()
        device_data['MB_per_sec'] = (
            (sectors_read_delta + sectors_write_delta) * 512 / 1024 / 1024
        )

        # Calculate latency (in milliseconds)
        read_time_delta = device_data['Time_Reading'].diff()
        write_time_delta = device_data['Time_Writing'].diff()

        # Avoid division by zero
        read_latency = np.where(
            reads_delta > 0,
            read_time_delta / reads_delta,
            0
        )
        write_latency = np.where(
            writes_delta > 0,
            write_time_delta / writes_delta,
            0
        )

        device_data['Read_Latency'] = read_latency
        device_data['Write_Latency'] = write_latency

        return device_data

    def _resample_device_data(self, device_data: pd.DataFrame,
                              resample_period: str = '1s') -> pd.DataFrame:
        """
        Resample device data to a specified time period.

        Args:
            device_data: Device statistics
            resample_period: Time period for resampling

        Returns:
            Resampled device statistics
        """
        # Resample the raw counters
        resampled = device_data[[
            'Reads_Completed', 'Writes_Completed',
            'Sectors_Read', 'Sectors_Written',
            'Time_Reading', 'Time_Writing'
        ]].resample(resample_period).mean()

        # Calculate rates from resampled data
        reads_delta = resampled['Reads_Completed'].diff()
        writes_delta = resampled['Writes_Completed'].diff()
        resampled['IOPS'] = reads_delta + writes_delta

        sectors_read_delta = resampled['Sectors_Read'].diff()
        sectors_write_delta = resampled['Sectors_Written'].diff()
        resampled['MB_per_sec'] = (
            (sectors_read_delta + sectors_write_delta) * 512 / 1024 / 1024
        )

        read_time_delta = resampled['Time_Reading'].diff()
        write_time_delta = resampled['Time_Writing'].diff()

        # Avoid division by zero
        resampled['Read_Latency'] = np.where(
            reads_delta > 0,
            read_time_delta / reads_delta,
            0
        )
        resampled['Write_Latency'] = np.where(
            writes_delta > 0,
            write_time_delta / writes_delta,
            0
        )

        return resampled

    def create_plots(self, df: pd.DataFrame) -> List[go.Figure]:
        """Create high-resolution disk performance plots."""
        try:
            if df.empty:
                self.logger.warning(
                    "No data available for high-resolution disk plots")
                return []

            devices = df['Device'].unique()
            figures = []

            # Common button menu for resolution switching
            updatemenus = [dict(
                type="buttons",
                direction="right",
                x=0.1,
                y=1.15,
                showactive=True,
                buttons=[
                    dict(
                        label="1s avg",
                        method="update",
                        args=[{"visible": [False, True] * len(devices)}]
                    ),
                    dict(
                        label="50ms",
                        method="update",
                        args=[{"visible": [True, False] * len(devices)}]
                    )
                ]
            )]

            # Create IOPS plot
            fig_iops = go.Figure()
            for device in devices:
                device_data = df[df['Device'] == device].copy()
                device_data = self._calculate_rates(device_data, device)
                resample_1s = self._resample_device_data(device_data, '1s')

                fig_iops.add_trace(go.Scatter(
                    x=device_data.index,
                    y=device_data['IOPS'],
                    mode='lines',
                    name=f'{device} IOPS (50ms)',
                    visible=False
                ))
                fig_iops.add_trace(go.Scatter(
                    x=resample_1s.index,
                    y=resample_1s['IOPS'],
                    mode='lines',
                    name=f'{device} IOPS (1s avg)',
                    visible=True
                ))

            fig_iops.update_layout(
                title='Disk IOPS Over Time',
                xaxis_title='Time',
                yaxis_title='IOPS',
                height=500,
                updatemenus=updatemenus,
                xaxis=dict(
                    type="date",
                    tickformat="%H:%M:%S.%3f"
                )
            )
            fig_iops.update_traces(line={'shape': 'linear'}, mode='lines')
            figures.append(fig_iops)

            # Create Throughput plot
            fig_throughput = go.Figure()
            for device in devices:
                device_data = df[df['Device'] == device].copy()
                device_data = self._calculate_rates(device_data, device)
                resample_1s = self._resample_device_data(device_data, '1s')

                fig_throughput.add_trace(go.Scatter(
                    x=device_data.index,
                    y=device_data['MB_per_sec'],
                    mode='lines',
                    name=f'{device} MB/s (50ms)',
                    visible=False
                ))
                fig_throughput.add_trace(go.Scatter(
                    x=resample_1s.index,
                    y=resample_1s['MB_per_sec'],
                    mode='lines',
                    name=f'{device} MB/s (1s avg)',
                    visible=True
                ))

            fig_throughput.update_layout(
                title='Disk Throughput Over Time',
                xaxis_title='Time',
                yaxis_title='MB/s',
                height=500,
                updatemenus=updatemenus,
                xaxis=dict(
                    type="date",
                    tickformat="%H:%M:%S.%3f"
                )
            )
            fig_throughput.update_traces(line={'shape': 'linear'},
                                         mode='lines')
            figures.append(fig_throughput)

            # Create Latency plot
            fig_latency = go.Figure()
            for device in devices:
                device_data = df[df['Device'] == device].copy()
                device_data = self._calculate_rates(device_data, device)
                resample_1s = self._resample_device_data(device_data, '1s')

                # Add read latency traces
                fig_latency.add_trace(go.Scatter(
                    x=device_data.index,
                    y=device_data['Read_Latency'],
                    mode='lines',
                    name=f'{device} Read Latency (50ms)',
                    visible=False
                ))
                fig_latency.add_trace(go.Scatter(
                    x=resample_1s.index,
                    y=resample_1s['Read_Latency'],
                    mode='lines',
                    name=f'{device} Read Latency (1s avg)',
                    visible=True
                ))

                # Add write latency traces
                fig_latency.add_trace(go.Scatter(
                    x=device_data.index,
                    y=device_data['Write_Latency'],
                    mode='lines',
                    name=f'{device} Write Latency (50ms)',
                    visible=False,
                    line=dict(dash='dash')
                ))
                fig_latency.add_trace(go.Scatter(
                    x=resample_1s.index,
                    y=resample_1s['Write_Latency'],
                    mode='lines',
                    name=f'{device} Write Latency (1s avg)',
                    visible=True,
                    line=dict(dash='dash')
                ))

            fig_latency.update_layout(
                title='Disk Latency Over Time',
                xaxis_title='Time',
                yaxis_title='Latency (ms)',
                height=500,
                updatemenus=[dict(
                    type="buttons",
                    direction="right",
                    x=0.1,
                    y=1.15,
                    showactive=True,
                    buttons=[
                        dict(
                            label="1s avg",
                            method="update",
                            args=[{
                                "visible": [False, True, False, True] *
                                len(devices)
                            }]
                        ),
                        dict(
                            label="50ms",
                            method="update",
                            args=[{
                                "visible": [True, False, True, False] *
                                len(devices)
                            }]
                        )
                    ]
                )],
                xaxis=dict(
                    type="date",
                    tickformat="%H:%M:%S.%3f"
                )
            )
            fig_latency.update_traces(line={'shape': 'linear'}, mode='lines')
            figures.append(fig_latency)

            # Create Latency Boxplot
            fig_latency_box = go.Figure()
            for device in devices:
                device_data = df[df['Device'] == device].copy()
                device_data = self._calculate_rates(device_data, device)
                resample_1s = self._resample_device_data(device_data, '1s')

                # Add 50ms read latency boxplot
                fig_latency_box.add_trace(go.Box(
                    y=device_data['Read_Latency'],
                    name=f'{device} Read (50ms)',
                    boxpoints=False,
                    visible=True
                ))

                # Add 50ms write latency boxplot
                fig_latency_box.add_trace(go.Box(
                    y=device_data['Write_Latency'],
                    name=f'{device} Write (50ms)',
                    boxpoints=False,
                    visible=True
                ))

                # Add 1s read latency boxplot
                fig_latency_box.add_trace(go.Box(
                    y=resample_1s['Read_Latency'],
                    name=f'{device} Read (1s)',
                    boxpoints=False,
                    visible=False
                ))

                # Add 1s write latency boxplot
                fig_latency_box.add_trace(go.Box(
                    y=resample_1s['Write_Latency'],
                    name=f'{device} Write (1s)',
                    boxpoints=False,
                    visible=False
                ))

            fig_latency_box.update_layout(
                title='Disk Latency Distribution',
                yaxis_title='Latency (ms)',
                height=500,
                showlegend=True,
                boxmode='group',  # Group boxes by device
                updatemenus=[dict(
                    type="buttons",
                    direction="right",
                    x=0.1,
                    y=1.15,
                    showactive=True,
                    buttons=[
                        dict(
                            label="50ms",
                            method="update",
                            args=[{
                                "visible": [True, True, False, False] *
                                len(devices)
                            }]
                        ),
                        dict(
                            label="1s avg",
                            method="update",
                            args=[{
                                "visible": [False, False, True, True] *
                                len(devices)
                            }]
                        )
                    ]
                )]
            )
            figures.append(fig_latency_box)

            return figures

        except Exception as e:
            raise DataProcessorError(
                f"Failed to create high-resolution disk plots: {e}")
