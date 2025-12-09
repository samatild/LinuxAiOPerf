"""
Top CPU consumers analysis.

Parses pidstat data and identifies the top N CPU consuming processes
based on their average metric utilization across the entire collection period.

Each metric (%usr, %system, %wait) has its own independent top 10 ranking.
Processes are grouped by Command name (not PID).
"""

from collections import defaultdict


def extract_top_cpu_consumers(pidstat_input_file, top_n=10):
    """
    Extract top N CPU consumers for each metric with time-series data.

    Ranking Method:
    ---------------
    For each metric (%usr, %system, %wait), processes are ranked INDEPENDENTLY
    by their AVERAGE value of that specific metric across all timestamps.

    Processes are grouped by Command name (last column), not by PID,
    since the same process may have different PIDs across samples.

    Parameters:
    -----------
    pidstat_input_file : str
        Path to the pidstat.txt file
    top_n : int
        Number of top consumers to return per metric (default: 10)

    Returns:
    --------
    dict with:
        - timestamps: list of timestamps in chronological order
        - top_usr: dict of top N processes ranked by avg %usr
        - top_system: dict of top N processes ranked by avg %system
        - top_wait: dict of top N processes ranked by avg %wait

        Each top_* dict maps Command name to:
            - command: process command name
            - pids: set of PIDs seen for this command
            - avg_metric: average value used for ranking
            - values: list of metric values aligned with timestamps
    """
    # Data structures to collect all process data grouped by Command
    process_data = defaultdict(lambda: {
        'usr': {},       # timestamp -> value
        'system': {},    # timestamp -> value
        'wait': {},      # timestamp -> value
        'pids': set()    # all PIDs seen for this command
    })
    all_timestamps = set()
    header_cols = None

    with open(pidstat_input_file, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or "Linux" in line:
                continue

            # Extract header to understand column structure
            if "UID" in line:
                header_cols = line.split()
                continue

            if header_cols is None:
                continue

            parts = line.split()
            if len(parts) < 9:
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
                # Parse fields based on pidstat output format:
                # Time [AM/PM] UID PID %usr %system %guest %wait %CPU CPU Cmd
                pid = parts[offset + 1]
                usr = float(parts[offset + 2])
                system = float(parts[offset + 3])
                # guest = float(parts[offset + 4])  # not used
                wait = float(parts[offset + 5])
                # Command is the last field (may contain spaces)
                command = ' '.join(parts[offset + 8:])

                all_timestamps.add(timestamp)

                # Group by Command name (not PID)
                process_data[command]['pids'].add(pid)

                # For each timestamp, keep the MAX value if multiple PIDs
                # have the same command (aggregate)
                current_usr = process_data[command]['usr'].get(timestamp, 0)
                current_sys = process_data[command]['system'].get(timestamp, 0)
                current_wait = process_data[command]['wait'].get(timestamp, 0)

                proc = process_data[command]
                proc['usr'][timestamp] = max(current_usr, usr)
                proc['system'][timestamp] = max(current_sys, system)
                proc['wait'][timestamp] = max(current_wait, wait)

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
            values = [data[metric_name].get(ts, 0) for ts in sorted_timestamps]
            result[command] = {
                'command': command,
                'pids': list(data['pids']),
                'avg_metric': round(process_avg[command], 2),
                'values': values
            }
        return result

    return {
        'timestamps': sorted_timestamps,
        'top_usr': calculate_top_n_for_metric('usr'),
        'top_system': calculate_top_n_for_metric('system'),
        'top_wait': calculate_top_n_for_metric('wait')
    }
