import os
import re


def extract_metadata(work_dir: str) -> dict:
    meta: dict = {}
    try:
        with open(os.path.join(work_dir, 'info.txt'), encoding='utf-8', errors='replace') as file:
            info = file.read()
    except OSError:
        info = ''
    labels = {
        'hostname': 'hostname',
        'start time': 'capture_start',
        'end time': 'capture_end',
        'runtime info': 'runtime',
    }
    for line in info.splitlines():
        if ':' not in line:
            continue
        label, value = line.split(':', 1)
        target = labels.get(label.strip().lower())
        if target and value.strip():
            meta[target] = value.strip()
        if label.strip().lower() == 'kernel' and value.strip():
            meta['kernel'] = value.strip()
        if 'collection_date' not in meta:
            match = re.search(r'\d{4}-\d{2}-\d{2}', line)
            if match:
                meta['collection_date'] = match.group(0)
    try:
        with open(os.path.join(work_dir, 'os-release'), encoding='utf-8', errors='replace') as file:
            os_release = file.read()
    except OSError:
        os_release = ''
    for line in os_release.splitlines():
        if line.startswith('PRETTY_NAME='):
            meta['os'] = line.split('=', 1)[1].strip().strip('"')
    try:
        with open(os.path.join(work_dir, 'lscpu.txt'), encoding='utf-8', errors='replace') as file:
            lscpu = file.read()
    except OSError:
        lscpu = ''
    for line in lscpu.splitlines():
        if line.startswith('Model name') and ':' in line:
            meta['cpu_model'] = line.split(':', 1)[1].strip()
            break
    return meta
