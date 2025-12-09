"""
Top Memory consumers analysis.

Parses pidstat memory data and identifies the top N memory consuming processes
based on their average metric utilization across the entire collection period.

Each metric (%MEM, RSS, VSZ) has its own independent top 10 ranking.
Processes are grouped by Command name (not PID).
"""

from collections import defaultdict


def extract_top_mem_consumers(pidstatmem_input_file, top_n=10):
    """
    Extract top N memory consuming processes for each metric with time-series data.

    Ranking Method:
    ---------------
    For each metric (%MEM, RSS, VSZ), processes are ranked INDEPENDENTLY
    by their AVERAGE value across all timestamps.

    Processes are grouped by Command name (last column), not by PID.

    Parameters:
    -----------
    pidstatmem_input_file : str
        Path to the pidstat-memory.txt file
    top_n : int
        Number of top consumers to return per metric (default: 10)

    Returns:
    --------
    dict with:
        - timestamps: list of timestamps in chronological order
        - top_mem_pct: dict of top N processes ranked by avg %MEM
        - top_rss: dict of top N processes ranked by avg RSS
        - top_vsz: dict of top N processes ranked by avg VSZ

        Each top_* dict maps Command name to:
            - command: process command name
            - pids: list of PIDs seen for this command
            - avg_metric: average value used for ranking
            - values: list of metric values aligned with timestamps
    """
    # Data structures to collect all process data grouped by Command
    process_data = defaultdict(lambda: {
        'mem_pct': {},   # timestamp -> %MEM value
        'rss': {},       # timestamp -> RSS value (KB)
        'vsz': {},       # timestamp -> VSZ value (KB)
        'pids': set()    # all PIDs seen for this command
    })
    all_timestamps = set()

    with open(pidstatmem_input_file, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or "Linux" in line:
                continue

            # Skip header lines
            if "UID" in line:
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
                # Parse fields based on pidstat -r output format:
                # Timestamp [AM/PM] UID PID minflt/s majflt/s VSZ RSS %MEM Command
                # With AM/PM: indices after offset are:
                # 0=UID, 1=PID, 2=minflt/s, 3=majflt/s, 4=VSZ, 5=RSS, 6=%MEM, 7+=Command
                pid = parts[offset + 1]  # PID
                # minflt/s = parts[offset + 2]  # not used
                # majflt/s = parts[offset + 3]  # not used
                vsz = float(parts[offset + 4])  # VSZ (KB)
                rss = float(parts[offset + 5])  # RSS (KB)
                mem_pct = float(parts[offset + 6])  # %MEM
                # Command is the last field (may contain spaces)
                command = ' '.join(parts[offset + 7:])

                all_timestamps.add(timestamp)

                # Group by Command name (not PID)
                process_data[command]['pids'].add(pid)

                # For each timestamp, keep the MAX value if multiple PIDs
                # have the same command (aggregate)
                current_mem = process_data[command]['mem_pct'].get(timestamp, 0)
                current_rss = process_data[command]['rss'].get(timestamp, 0)
                current_vsz = process_data[command]['vsz'].get(timestamp, 0)

                process_data[command]['mem_pct'][timestamp] = max(current_mem, mem_pct)
                process_data[command]['rss'][timestamp] = max(current_rss, rss)
                process_data[command]['vsz'][timestamp] = max(current_vsz, vsz)

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
        'top_mem_pct': calculate_top_n_for_metric('mem_pct'),
        'top_rss': calculate_top_n_for_metric('rss'),
        'top_vsz': calculate_top_n_for_metric('vsz')
    }

