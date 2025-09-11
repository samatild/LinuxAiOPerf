"""
Process IO statistics processor for pidstat-io data.
"""

import os
import logging
from typing import List, Dict, Any, Tuple
import json

from core.base import ProcessInfoProcessor, DataProcessorError



# NOTE: This module only provides legacy function wrappers for backward compatibility.
# The class-based processor is not used in the current implementation.

# Legacy function wrappers for backward compatibility with generate_html.py
def pidstatio_extract_header_line(file_path):
    """Legacy function wrapper for backward compatibility."""
    # Read the input file and extract the header line containing "UID"
    with open(file_path, "r") as file:
        for line in file:
            if "UID" in line:
                columns = line.split()
                # Replace the text in the first column
                columns[0] = "Timestamp"
                header_line = " ".join(columns)
                return header_line.strip()


def generate_pidstatio(pidstat_input_file, pidstat_header):
    """Legacy function wrapper for backward compatibility."""
    timestamps = set()  # To hold unique timestamps
    chunks = {}  # To hold chunks of data for each timestamp

    with open(pidstat_input_file, 'r') as f:
        current_chunk = ""
        current_timestamp = None
        for line in f:
            if "Linux" in line or line.strip() == '' or "UID" in line:
                continue
            first_column = line.split()[0]
            # Checking if it's a timestamp with HH:MM:SS format
            if len(first_column.split(':')) == 3:
                new_timestamp = first_column.strip()
                if new_timestamp != current_timestamp:
                    if current_timestamp:
                        # Save the previous chunk
                        chunks[current_timestamp] = current_chunk.strip()
                    current_timestamp = new_timestamp
                    timestamps.add(current_timestamp)
                    current_chunk = line  # Start the new chunk with this line
                else:
                    # If the timestamp is the same, append
                    current_chunk += line
            else:
                current_chunk += line  # Append non-timestamp

        if current_timestamp:  # For the last chunk
            chunks[current_timestamp] = current_chunk.strip()

    # Generate JavaScript object for chunks
    chunks_js_object = "{\n"
    for timestamp, chunk in chunks.items():
        # Escape quotes and backslashes within the chunk of text
        escaped_chunk = chunk.replace("\\", "\\\\").replace(
            "\"", "\\\"").replace("\n", "\\n").replace("\t", "\\t")
        chunks_js_object += f'    "{timestamp}": "{escaped_chunk}",\n'
    chunks_js_object += "}"

    return chunks, timestamps, chunks_js_object

