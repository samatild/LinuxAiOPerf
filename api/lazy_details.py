"""
Lazy (on-demand) reader for large process-detail files (pidstat, top, iotop).

Historically these files were fully parsed into memory and shipped as one
giant JSON blob containing every timestamp's process table. For hosts with
many CPUs/processes, that file can be hundreds of MB to GB in size, making
the eager approach painfully slow and memory hungry.

This module builds a lightweight byte-offset index (single pass, O(n),
no string concatenation) mapping each timestamp to its (offset, length) in
the source file. The full data is never discarded -- it's read and parsed
on demand, one snapshot at a time, when the UI actually needs it (e.g. the
user picks a timestamp in the "Process Details" combobox).
"""

from typing import Callable, Optional


def _index_by_boundary(path: str, is_boundary: Callable[[str], Optional[str]]) -> dict:
    """Single-pass byte-offset index.

    `is_boundary(line)` should return the timestamp string if `line` starts
    a new chunk, or None otherwise. Returns {timestamp: (offset, length)}.
    """
    index: dict[str, tuple[int, int]] = {}
    current_ts = None
    current_start = None
    pos = 0
    with open(path, 'rb') as f:
        for raw_line in f:
            line = raw_line.decode('utf-8', errors='replace')
            ts = is_boundary(line)
            if ts is not None and ts != current_ts:
                if current_ts is not None:
                    index[current_ts] = (current_start, pos - current_start)
                current_ts = ts
                current_start = pos
            pos += len(raw_line)
    if current_ts is not None:
        index[current_ts] = (current_start, pos - current_start)
    return index


def index_pidstat(path: str) -> dict:
    """Index a pidstat-style file (pidstat.txt / pidstat-io.txt / pidstat-memory.txt)."""
    def boundary(line: str) -> Optional[str]:
        s = line.strip()
        if not s or 'Linux' in s or 'UID' in s:
            return None
        parts = s.split()
        first = parts[0] if parts else ''
        return first if len(first.split(':')) == 3 else None
    return _index_by_boundary(path, boundary)


def index_top(path: str) -> dict:
    """Index a top.txt file (chunk boundary = 'top - HH:MM:SS up ...' lines)."""
    def boundary(line: str) -> Optional[str]:
        if 'top - ' in line:
            parts = line.split()
            return parts[2] if len(parts) > 2 else None
        return None
    return _index_by_boundary(path, boundary)


def index_iotop(path: str) -> dict:
    """Index an iotop.txt file (chunk boundary = 'Total DISK READ' summary lines)."""
    def boundary(line: str) -> Optional[str]:
        s = line.strip()
        if 'Total DISK READ' in s:
            parts = s.split()
            return parts[0] if parts else None
        return None
    return _index_by_boundary(path, boundary)


def read_range(path: str, offset: int, length: int) -> str:
    """Read exactly one chunk's raw text via seek (fast regardless of file size)."""
    with open(path, 'rb') as f:
        f.seek(offset)
        return f.read(length).decode('utf-8', errors='replace')


def strip_pidstat_noise(text: str) -> str:
    """Drop the interleaved 'Linux ...' / blank / repeated 'UID' header lines
    that pidstat re-prints before every timestamp sample -- mirrors the
    `continue` skips in the original generate_pidstat()/etc. loops so the
    remaining text can be parsed the same way (via _parse_chunk_text)."""
    return '\n'.join(
        line for line in text.splitlines()
        if line.strip() and 'Linux' not in line and 'UID' not in line
    )


def parse_top_chunk(text: str) -> dict:
    """Parse a single top.txt chunk's raw text into {headers, rows}.

    Mirrors _parse_top_file()'s per-line filtering/slicing exactly (including
    its pre-existing quirk of keeping only the first word of multi-word
    COMMAND values) so results are identical to the previous eager parse.
    """
    headers = ['Timestamp', 'PID', 'USER', 'PR', 'NI', 'VIRT', 'RES', 'SHR',
               'S', '%CPU', '%MEM', 'TIME+', 'COMMAND']
    current_ts = None
    rows = []
    for line in text.splitlines():
        if 'top - ' in line:
            parts = line.split()
            current_ts = parts[2] if len(parts) > 2 else None
            continue
        if not (line.strip() and current_ts
                and not any(line.startswith(p) for p in
                            ('top', '%', 'Tasks', 'Cpu', 'MiB', 'KiB', 'Mem', 'Swap', 'PID'))):
            continue
        parts = line.strip().split(None, 12)
        if len(parts) >= 12 and parts[0].isdigit():
            rows.append([current_ts] + parts[:12])
    return {'headers': headers, 'rows': rows}


def parse_iotop_chunk(text: str) -> dict:
    """Parse a single iotop.txt chunk's raw text into {headers, rows}.

    Mirrors _parse_iotop_file()'s per-line handling exactly, including using
    each row's own embedded timestamp (not the chunk-boundary timestamp) for
    the Timestamp column, for both the legacy "b'...'" and plain formats.
    """
    headers = ['Timestamp', 'TID', 'PRIO', 'USER', 'DISK_READ', 'DISK_WRITE',
               'SWAPIN', 'IO%', 'COMMAND']
    rows = []
    for line in text.splitlines():
        s = line.strip()
        if not s:
            continue

        if 'Total DISK READ' in s:
            continue
        if 'Actual DISK' in s or 'Current DISK' in s or s.startswith('TIME') or s.startswith('TID'):
            continue

        if s.startswith("b'") or s.startswith('b"'):
            inner = s[2:].rstrip("'\"")
            parts = inner.split(None, 8)
            if len(parts) >= 7 and parts[1].isdigit():
                rows.append([parts[0]] + parts[1:])
            continue

        parts = s.split(None, 8)
        if len(parts) >= 7 and parts[1].isdigit() and ':' in parts[0]:
            rows.append([parts[0]] + parts[1:])

    return {'headers': headers, 'rows': rows}
