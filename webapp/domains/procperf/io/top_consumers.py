"""
Top I/O consumers analysis.

Parses pidstat IO data and identifies the top N I/O consuming processes
based on their average metric utilization across the entire collection period.

Each metric (kB_rd/s, kB_wr/s, iodelay) has its own independent top 10 ranking.
Processes are grouped by Command name (not PID).
"""

from collections import defaultdict


def extract_top_io_consumers(pidstatio_input_file, top_n=10):
    """
    Extract top N I/O consuming processes for each metric with time-series data.

    Ranking Method:
    ---------------
    For each metric (kB_rd/s, kB_wr/s, iodelay), processes are ranked
    INDEPENDENTLY by their AVERAGE value across all timestamps.

    Processes are grouped by Command name (last column), not by PID.

    Parameters:
    -----------
    pidstatio_input_file : str
        Path to the pidstat-io.txt file
    top_n : int
        Number of top consumers to return per metric (default: 10)

    Returns:
    --------
    dict with:
        - timestamps: list of timestamps in chronological order
        - top_read: dict of top N processes ranked by avg kB_rd/s
        - top_write: dict of top N processes ranked by avg kB_wr/s
        - top_iodelay: dict of top N processes ranked by avg iodelay

        Each top_* dict maps Command name to:
            - command: process command name
            - pids: list of PIDs seen for this command
            - avg_metric: average value used for ranking
            - values: list of metric values aligned with timestamps
    """
    # Data structures to collect all process data grouped by Command
    process_data = defaultdict(lambda: {
        'read': {},      # timestamp -> kB_rd/s value
        'write': {},     # timestamp -> kB_wr/s value
        'iodelay': {},   # timestamp -> iodelay value
        'pids': set()    # all PIDs seen for this command
    })
    all_timestamps = set()

    with open(pidstatio_input_file, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or "Linux" in line:
                continue

            # Skip header lines
            if "UID" in line:
                continue

            parts = line.split()
            if len(parts) < 8:
                continue

            # Check if first column is a timestamp (HH:MM:SS format)
            first_col = parts[0]
            if len(first_col.split(':')) != 3:
                continue

            # Handle AM/PM format (e.g., "12:51:43 PM")
            timestamp = first_col
            offset = 1
            if len(parts) > 1 and parts[1] in ('AM', 'PM'):
                timestamp = f"{first_col} {parts[1]}"
                offset = 2

            try:
                # Parse fields based on pidstat -d output format:
                # Timestamp [AM/PM] UID PID kB_rd/s kB_wr/s kB_ccwr/s iodelay Command
                # With AM/PM: indices are 0=time, 1=AM/PM, 2=UID, 3=PID, 4=rd, 5=wr, 6=ccwr, 7=iodelay, 8+=Command
                pid = parts[offset + 1]  # PID
                read_val = float(parts[offset + 2])  # kB_rd/s
                write_val = float(parts[offset + 3])  # kB_wr/s
                # parts[offset + 4] is kB_ccwr/s, skip it
                iodelay_val = float(parts[offset + 5])  # iodelay
                # Command is the last field (may contain spaces)
                command = ' '.join(parts[offset + 6:])

                all_timestamps.add(timestamp)

                # Group by Command name (not PID)
                process_data[command]['pids'].add(pid)

                # For each timestamp, keep the MAX value if multiple PIDs
                # have the same command (aggregate)
                current_read = process_data[command]['read'].get(timestamp, 0)
                current_write = process_data[command]['write'].get(timestamp, 0)
                current_iodelay = process_data[command]['iodelay'].get(timestamp, 0)

                process_data[command]['read'][timestamp] = max(current_read, read_val)
                process_data[command]['write'][timestamp] = max(current_write, write_val)
                process_data[command]['iodelay'][timestamp] = max(
                    current_iodelay, iodelay_val)

            except (ValueError, IndexError):
                # Skip malformed lines
                continue

    # Sort timestamps chronologically
    sorted_timestamps = sorted(list(all_timestamps))

    def calculate_top_n_for_metric(metric_name):
        """Calculate top N processes for a specific metric."""
        # Calculate average for each process
        process_avg = {}
        for command, data in process_data.items():
            values = list(data[metric_name].values())
            if values:
                process_avg[command] = sum(values) / len(values)
            else:
                process_avg[command] = 0

        # Get top N by average
        top_commands = sorted(
            process_avg.keys(),
            key=lambda x: process_avg[x],
            reverse=True
        )[:top_n]

        # Build result
        result = {}
        for command in top_commands:
            data = process_data[command]
            result[command] = {
                'command': command,
                'pids': list(data['pids']),
                'avg_metric': round(process_avg[command], 2),
                'values': [data[metric_name].get(ts, 0) for ts in sorted_timestamps]
            }
        return result

    return {
        'timestamps': sorted_timestamps,
        'top_read': calculate_top_n_for_metric('read'),
        'top_write': calculate_top_n_for_metric('write'),
        'top_iodelay': calculate_top_n_for_metric('iodelay')
    }
