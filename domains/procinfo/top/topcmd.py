"""
Top command processor for top data.
"""
# Legacy function wrappers for backward compatibility with generate_html.py
# NOTE: This module only provides legacy function wrappers for backward
# compatibility. The class-based processor is not used in the current
# implementation.


def generate_top(top_input_file):
    """Legacy function wrapper for backward compatibility."""
    timestamps = set()  # To hold unique timestamps
    chunks = {}  # To hold chunks of data for each timestamp
    with open(top_input_file, 'r') as f:
        current_chunk = ""
        current_timestamp = None
        for line in f:
            if "top - " in line:  # Timestamp is in a line
                # that starts with 'top - '
                # Assuming 'top - 13:36:32 up' format
                new_timestamp = line.split(' ')[2]
                if new_timestamp != current_timestamp:
                    if current_timestamp:
                        chunks[current_timestamp] = current_chunk.strip()
                    current_timestamp = new_timestamp
                    timestamps.add(current_timestamp)
                    current_chunk = line
                else:
                    current_chunk += line
            else:
                current_chunk += line
        if current_timestamp:  # For the last chunk
            chunks[current_timestamp] = current_chunk.strip()
    # Escape special characters and construct a JavaScript object
    chunks_js_object = "{\n"
    for timestamp, chunk in chunks.items():
        escaped_chunk = chunk.replace("\\", "\\\\").replace(
            "\"", "\\\"").replace("\n", "\\n").replace("\t", "\\t")
        chunks_js_object += f'    "{timestamp}": "{escaped_chunk}",\n'
    chunks_js_object += "}"
    return chunks_js_object, timestamps
