import re


def _bytes_from_kib(value: str) -> int | None:
    try:
        return int(value) * 1024
    except (TypeError, ValueError):
        return None


def summarize_capture_health(lscpu: str, sar_load: str, meminfo: str) -> dict:
    """Return a small, source-derived capture health summary; omit absent inputs."""
    summary: dict = {}
    cpu_match = re.search(r'^CPU\(s\):\s*(\d+)', lscpu, re.MULTILINE)
    cpu_count = int(cpu_match.group(1)) if cpu_match else 0
    if cpu_count:
        summary['cpu_count'] = cpu_count

    peak_load: float | None = None
    for line in sar_load.splitlines():
        values = re.findall(r'\d+(?:\.\d+)?', line)
        if len(values) >= 5 and not line.lower().startswith(('average', 'runq')):
            try:
                load_1m = float(values[-4])
            except ValueError:
                continue
            peak_load = max(peak_load or load_1m, load_1m)
    if peak_load is not None and cpu_count:
        summary['peak_normalized_load_1m'] = round(peak_load / cpu_count, 3)

    fields = {}
    for line in meminfo.splitlines():
        match = re.match(r'^(MemTotal|MemAvailable|SwapTotal|SwapFree):\s*(\d+)', line)
        if match:
            fields[match.group(1)] = _bytes_from_kib(match.group(2))
    if fields.get('MemAvailable') is not None:
        summary['min_available_memory_bytes'] = fields['MemAvailable']
    if fields.get('SwapTotal') is not None and fields.get('SwapFree') is not None:
        summary['peak_swap_used_bytes'] = max(0, fields['SwapTotal'] - fields['SwapFree'])

    return summary
