"""
IOTop command processor for iotop data.
"""

import os
import logging
from typing import List, Dict, Any, Tuple
import json

from core.base import ProcessInfoProcessor, DataProcessorError



# NOTE: This module only provides legacy function wrappers for backward compatibility.
# The class-based processor is not used in the current implementation.

# Legacy function wrappers for backward compatibility with generate_html.py
def is_legacy_format(first_line):
    """Check if the file is in the legacy format (starts with full date)"""
    return first_line.startswith(
        ('Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun')
    )


def generate_iotop(iotop_input_file):
    """Legacy function wrapper for backward compatibility."""
    timestamps = set()
    chunks = {}

    with open(iotop_input_file, 'r') as f:
        # Read first line to determine format
        first_line = f.readline()
        is_legacy = is_legacy_format(first_line)
        f.seek(0)  # Reset file pointer to start

        current_chunk = ""
        current_timestamp = None
        prev_line = None  # Only needed for legacy format

        for line in f:
            if is_legacy:
                # Legacy format processing
                if "Total DISK READ" in line:
                    if current_timestamp:
                        chunks[current_timestamp] = current_chunk.strip()
                        current_chunk = ""

                    current_timestamp = prev_line.strip()
                    timestamps.add(current_timestamp)
                else:
                    current_chunk += prev_line if prev_line else ""
                prev_line = line

            else:
                # New format processing
                if (len(line.strip()) > 8 and
                        line[0:8].replace(':', '').isdigit()):
                    timestamp = line[0:8]

                    if current_timestamp and current_timestamp != timestamp:
                        chunks[current_timestamp] = current_chunk.strip()
                        current_chunk = ""

                    current_timestamp = timestamp
                    timestamps.add(timestamp)

                current_chunk += line

        # Handle the last chunk
        if current_timestamp and current_chunk:
            if is_legacy:
                current_chunk += prev_line  # Include the last line for legacy
            chunks[current_timestamp] = current_chunk.strip()

    # Escape special characters and construct a JavaScript object
    chunks_js_object = "{\n"
    for timestamp, chunk in chunks.items():
        escaped_chunk = chunk.replace("\\", "\\\\").replace(
            "\"", "\\\"").replace("\n", "\\n").replace("\t", "\\t")
        chunks_js_object += f'    "{timestamp}": "{escaped_chunk}",\n'
    chunks_js_object += "}"

    return timestamps, chunks_js_object

