"""
Shared datetime utilities for Linux AIO Performance data processors.

Provides helpers for enriching time-only timestamps (HH:MM:SS) with the
actual collection date read from the co-located info.txt metadata file.
"""

import os
import datetime
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Formats used by the collection script across distros:
# Ubuntu/24h: "Wed Sep 10 14:54:17 UTC 2025"
# RHEL/12h:   "Thu Mar 26 12:31:27 PM UTC 2026"
_INFO_START_TIME_PREFIX = "Start Time:"
_INFO_START_TIME_FMTS = [
    "%a %b %d %H:%M:%S UTC %Y",     # 24-hour (Ubuntu, Debian, …)
    "%a %b %d %I:%M:%S %p UTC %Y",  # 12-hour AM/PM (RHEL, CentOS, …)
]


def parse_info_txt_content(content: str) -> Optional[datetime.date]:
    """
    Parse the collection date from the raw text content of info.txt.

    Args:
        content: Full text content of info.txt

    Returns:
        datetime.date of the collection, or None if not parseable
    """
    for line in content.splitlines():
        line = line.strip()
        if line.startswith(_INFO_START_TIME_PREFIX):
            value = line[len(_INFO_START_TIME_PREFIX):].strip()
            for fmt in _INFO_START_TIME_FMTS:
                try:
                    dt = datetime.datetime.strptime(value, fmt)
                    return dt.date()
                except ValueError:
                    continue
            logger.debug(
                "Could not parse Start Time value: %r", value)
            return None
    return None


def parse_collection_date(data_file_path: str) -> Optional[datetime.date]:
    """
    Derive the collection date from the info.txt file that lives in the
    same directory as the given data file.

    Args:
        data_file_path: Path to any data file in the collection directory
                        (e.g. 'mpstat.txt' or '/data/run1/mpstat.txt')

    Returns:
        datetime.date of the collection, or None if info.txt is absent
        or its Start Time line cannot be parsed.
    """
    data_dir = os.path.dirname(os.path.abspath(data_file_path))
    info_path = os.path.join(data_dir, "info.txt")

    if not os.path.exists(info_path):
        logger.debug("info.txt not found at %s — skipping date enrichment",
                     info_path)
        return None

    try:
        with open(info_path, "r") as f:
            content = f.read()
        result = parse_info_txt_content(content)
        if result is None:
            logger.debug(
                "No parseable Start Time found in %s", info_path)
        return result
    except OSError as e:
        logger.debug("Could not read %s: %s", info_path, e)
        return None


def enrich_timestamps(
    time_series,
    collection_date: datetime.date,
    time_fmt: str = "%H:%M:%S"
):
    """
    Combine a Series of time-only strings with a known date to produce
    proper datetime strings that pandas can parse unambiguously.

    Args:
        time_series: pandas Series of time strings (e.g. "14:54:20")
        collection_date: The date to prepend
        time_fmt: strptime format of the time strings (default "%H:%M:%S")

    Returns:
        pandas Series of combined datetime strings: "YYYY-MM-DD HH:MM:SS"
    """
    date_str = collection_date.strftime("%Y-%m-%d")
    return time_series.astype(str).apply(lambda t: f"{date_str} {t}")


import re as _re
_AMPM_RE = _re.compile(r'\b(\d{1,2}:\d{2}:\d{2})\s+(AM|PM)\b', _re.IGNORECASE)


def normalize_ampm_timestamps(line: str) -> str:
    """
    Convert any HH:MM:SS AM/PM occurrences in *line* to 24-hour HH:MM:SS.

    E.g. "12:31:30 PM  all  56.78" → "12:31:30  all  56.78"
         "01:30:00 PM  all  56.78" → "13:30:00  all  56.78"
         "12:00:00 AM  all  56.78" → "00:00:00  all  56.78"

    Lines without AM/PM tokens are returned unchanged.
    """
    def _convert(m):
        h, mn, s = m.group(1).split(':')
        hour = int(h)
        ampm = m.group(2).upper()
        if ampm == 'PM' and hour != 12:
            hour += 12
        elif ampm == 'AM' and hour == 12:
            hour = 0
        return f"{hour:02d}:{mn}:{s}"

    return _AMPM_RE.sub(_convert, line)
