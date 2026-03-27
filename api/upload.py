"""
POST /api/upload

Accepts a multipart .tar.gz archive, extracts it, runs all existing Python
performance data processors from webapp/domains/*, and returns a single JSON
report object conforming to the ReportData TypeScript interface.
"""

import json
import os
import sys
import tarfile
import secrets
import io
import shutil
import re
import logging
from http.server import BaseHTTPRequestHandler

# ── Path setup ──────────────────────────────────────────────────────────────
WEBAPP_DIR = os.path.join(os.path.dirname(__file__), '..', 'webapp')
sys.path.insert(0, WEBAPP_DIR)

import plotly.io as pio

from domains.factory import ProcessorFactory
from domains.procperf.cpu.top_consumers import extract_top_cpu_consumers
from domains.procperf.io.top_consumers import extract_top_io_consumers
from domains.procperf.memory.top_consumers import extract_top_mem_consumers
from domains.procinfo.pidstat.pidstatcpu import generate_pidstat, pidstat_extract_header_line
from domains.procinfo.pidstat.pidstatio import generate_pidstatio, pidstatio_extract_header_line
from domains.procinfo.pidstat.pidstatmem import generate_pidstatmem, pidstatmem_extract_header_line
from domains.procinfo.top.topcmd import generate_top
from domains.procinfo.iotop.iotopcmd import generate_iotop
from domains.sysconfig.lvm.lvmviz import parse_pvs, parse_vgs, parse_lvs

logging.basicConfig(level=logging.WARNING)
log = logging.getLogger('api.upload')


# ── Helpers ──────────────────────────────────────────────────────────────────

def read_safe(path: str) -> str:
    try:
        if os.path.exists(path) and os.path.getsize(path) > 0:
            with open(path, 'r', encoding='utf-8', errors='replace') as f:
                return f.read()
    except Exception:
        pass
    return ''


def fig_to_dict(fig) -> dict:
    return json.loads(pio.to_json(fig))


def parse_cgi_multipart(handler):
    """Parse multipart/form-data without cgi module (deprecated in 3.13)."""
    import email
    content_type = handler.headers.get('Content-Type', '')
    content_length = int(handler.headers.get('Content-Length', 0))
    body = handler.rfile.read(content_length)

    # Build a message to let email library parse the multipart body
    msg_bytes = f'Content-Type: {content_type}\r\n\r\n'.encode() + body
    msg = email.message_from_bytes(msg_bytes)

    parts = {}
    for part in msg.walk():
        cd = part.get('Content-Disposition', '')
        if not cd:
            continue
        params = dict(p.strip().split('=', 1) for p in cd.split(';')[1:] if '=' in p)
        name = params.get('name', '').strip('"')
        if name:
            parts[name] = part.get_payload(decode=True)
    return parts


# ── Metadata ─────────────────────────────────────────────────────────────────

def extract_metadata(work_dir: str) -> dict:
    meta = {}

    info = read_safe(os.path.join(work_dir, 'info.txt'))
    if info:
        for line in info.splitlines():
            low = line.lower()
            if 'hostname' in low or 'host:' in low:
                parts = line.split(':', 1)
                if len(parts) > 1 and 'hostname' not in meta:
                    meta['hostname'] = parts[1].strip()
            if re.search(r'\d{4}-\d{2}-\d{2}', line) and 'collection_date' not in meta:
                m = re.search(r'\d{4}-\d{2}-\d{2}', line)
                if m:
                    meta['collection_date'] = m.group(0)
            if 'kernel' in low and 'kernel' not in meta:
                parts = line.split(':', 1)
                if len(parts) > 1:
                    meta['kernel'] = parts[1].strip()

    os_rel = read_safe(os.path.join(work_dir, 'os-release'))
    for line in os_rel.splitlines():
        if line.startswith('PRETTY_NAME='):
            meta['os'] = line.split('=', 1)[1].strip().strip('"')

    lscpu = read_safe(os.path.join(work_dir, 'lscpu.txt'))
    for line in lscpu.splitlines():
        if line.startswith('Model name'):
            parts = line.split(':', 1)
            if len(parts) > 1:
                meta['cpu_model'] = parts[1].strip()
                break

    return meta


# ── System Configuration ─────────────────────────────────────────────────────

def extract_sysconfig(work_dir: str) -> dict:
    sc = {}

    runtime = read_safe(os.path.join(work_dir, 'info.txt'))
    os_rel = read_safe(os.path.join(work_dir, 'os-release'))
    if runtime or os_rel:
        sc['information'] = {'runtime_info': runtime, 'os_release': os_rel}

    lshw = read_safe(os.path.join(work_dir, 'lshw.txt'))
    dmidecode = read_safe(os.path.join(work_dir, 'dmidecode.txt'))
    if lshw or dmidecode:
        sc['hardware'] = {'lshw': lshw, 'dmidecode': dmidecode}

    storage = {}
    for key, fname in [('lsscsi', 'lsscsi.txt'), ('lsblk', 'lsblk-f.txt'),
                       ('df', 'df-h.txt'), ('ls_dev_mapper', 'ls-l-dev-mapper.txt')]:
        v = read_safe(os.path.join(work_dir, fname))
        if v:
            storage[key] = v
    if storage:
        sc['storage'] = storage

    # LVM — parse topology + raw text; no graphviz needed (diagram rendered in React)
    lvs_path = os.path.join(work_dir, 'lvs.txt')
    if os.path.exists(lvs_path) and os.path.getsize(lvs_path) > 0:
        lvm_data: dict = {}
        # Raw text files
        for fname, key in [('pvs.txt','pvs_raw'),('vgs.txt','vgs_raw'),('lvs.txt','lvs_raw'),
                           ('pvdisplay.txt','pvdisplay_raw'),('vgdisplay.txt','vgdisplay_raw'),
                           ('lvdisplay.txt','lvdisplay_raw')]:
            p = os.path.join(work_dir, fname)
            if os.path.exists(p):
                with open(p) as f:
                    lvm_data[key] = f.read()
        # Structured topology for React diagram
        try:
            orig = os.getcwd()
            os.chdir(work_dir)
            pvs = parse_pvs()   # [(pv_name, vg_name, pv_size, pv_free), ...]
            vgs = parse_vgs()   # [(vg_name, vg_size, vg_free), ...]
            lvs = parse_lvs()   # [(lv_name, vg_name, lv_size, lv_type, ...), ...]
            os.chdir(orig)
            lvm_data['topology'] = {
                'pvs': [{'name': p[0], 'vg': p[1], 'size': p[2], 'free': p[3]} for p in pvs],
                'vgs': [{'name': v[0], 'size': v[1], 'free': v[2]} for v in vgs],
                'lvs': [{'name': l[0], 'vg': l[1], 'size': l[2], 'type': l[3]} for l in lvs],
            }
        except Exception as e:
            log.warning(f'LVM topology parse failed: {e}')
            try:
                os.chdir(orig)
            except Exception:
                pass
        if lvm_data:
            sc['lvm'] = lvm_data

    for key, fname in [
        ('cpu_info', 'lscpu.txt'),
        ('memory_info', 'meminfo.txt'),
        ('kernel_params', 'sysctl.txt'),
        ('kernel_modules', 'lsmod.txt'),
    ]:
        v = read_safe(os.path.join(work_dir, fname))
        if v:
            sc[key] = v

    # Security — prefer selinux, fall back to apparmor
    selinux = read_safe(os.path.join(work_dir, 'sestatus.txt'))
    apparmor = read_safe(os.path.join(work_dir, 'apparmor_status.txt'))
    security = selinux or apparmor
    if security:
        sc['security'] = security

    return sc


# ── Performance (time-series charts) ─────────────────────────────────────────

def extract_performance(work_dir: str) -> dict:
    orig = os.getcwd()
    os.chdir(work_dir)
    perf = {}

    def run_processor(ptype: str, fname: str) -> list:
        if not os.path.exists(fname):
            return []
        try:
            proc = ProcessorFactory.create_processor(ptype, fname)
            _, figs = proc.process()
            return [fig_to_dict(f) for f in figs]
        except Exception as e:
            log.warning(f'{ptype} processor failed: {e}')
            return []

    cpu_figs = run_processor('cpu', 'mpstat.txt')
    if cpu_figs:
        perf['cpu'] = {'figures': cpu_figs}

    mem_figs = run_processor('memory', 'vmstat-data.out')
    if mem_figs:
        perf['memory'] = {'figures': mem_figs}

    disk = {}
    pd_figs = run_processor('diskiostat', 'iostat-data.out')
    pm_figs = run_processor('diskmetrics', 'iostat-data.out')
    hr_figs = run_processor('diskhighres', 'diskstats_log.txt')
    if pd_figs:
        disk['per_device'] = {'figures': pd_figs}
    if pm_figs:
        disk['per_metric'] = {'figures': pm_figs}
    if hr_figs:
        disk['highres'] = {'figures': hr_figs}
    if disk:
        perf['disk'] = disk

    net_figs = run_processor('network', 'sarnetwork.txt')
    if net_figs:
        perf['network'] = {'figures': net_figs}

    os.chdir(orig)
    return perf


# ── Process Activity (top-N consumer charts) ──────────────────────────────────

def _top_consumers_to_figs(data: dict, metric_keys: list[tuple[str, str]]) -> list:
    """Convert top-consumer dicts to Plotly figures."""
    import plotly.graph_objects as go
    figs = []
    timestamps = data.get('timestamps', [])
    for data_key, metric_label in metric_keys:
        consumers = data.get(data_key, {})
        if not consumers:
            continue
        fig = go.Figure()
        for cmd, info in consumers.items():
            fig.add_trace(go.Scatter(
                x=timestamps,
                y=info.get('values', []),
                mode='lines',
                name=cmd,
                hovertemplate=f'<b>{cmd}</b><br>{metric_label}: %{{y:.1f}}<br>%{{x}}<extra></extra>',
            ))
        fig.update_layout(
            title=f'Top 10 Processes — {metric_label}',
            xaxis_title='Timestamp',
            yaxis_title=metric_label,
            height=420,
            template='seaborn',
        )
        figs.append(fig_to_dict(fig))
    return figs


def extract_process_activity(work_dir: str) -> dict:
    orig = os.getcwd()
    os.chdir(work_dir)
    activity = {}

    try:
        cpu_data = extract_top_cpu_consumers('pidstat.txt')
        figs = _top_consumers_to_figs(cpu_data, [
            ('top_usr', '%usr'), ('top_system', '%system'), ('top_wait', '%wait'),
        ])
        if figs:
            activity['cpu'] = {'figures': figs}
    except Exception as e:
        log.warning(f'process activity CPU failed: {e}')

    try:
        io_data = extract_top_io_consumers('pidstat-io.txt')
        figs = _top_consumers_to_figs(io_data, [
            ('top_read', 'kB_rd/s'), ('top_write', 'kB_wr/s'), ('top_iodelay', 'iodelay'),
        ])
        if figs:
            activity['io'] = {'figures': figs}
    except Exception as e:
        log.warning(f'process activity IO failed: {e}')

    try:
        mem_data = extract_top_mem_consumers('pidstat-memory.txt')
        figs = _top_consumers_to_figs(mem_data, [
            ('top_mem_pct', '%MEM'), ('top_rss', 'RSS (MB)'), ('top_vsz', 'VSZ (MB)'),
        ])
        if figs:
            activity['memory'] = {'figures': figs}
    except Exception as e:
        log.warning(f'process activity Memory failed: {e}')

    os.chdir(orig)
    return activity


# ── Process Details (timestamp-chunked snapshots) ─────────────────────────────

def _parse_chunk_text(header_line: str, chunk_text: str) -> dict:
    """Convert raw pidstat chunk text to {headers, rows}."""
    headers = header_line.split()
    rows = []
    for line in chunk_text.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) >= len(headers) - 1:
            # Pad or trim to header length; last field may contain spaces (command)
            row = parts[:len(headers)]
            while len(row) < len(headers):
                row.append('')
            rows.append(row)
    return {'headers': headers, 'rows': rows}


def _chunks_to_response(chunks: dict, header: str, thresholds: dict | None = None) -> dict:
    timestamps = sorted(chunks.keys())
    parsed_chunks = {ts: _parse_chunk_text(header, text) for ts, text in chunks.items()}
    result: dict = {'timestamps': timestamps, 'chunks': parsed_chunks}
    if thresholds:
        result['thresholds'] = thresholds
    return result


def extract_process_details(work_dir: str) -> dict:
    orig = os.getcwd()
    os.chdir(work_dir)
    details = {}

    # pidstat CPU
    if os.path.exists('pidstat.txt'):
        try:
            header = pidstat_extract_header_line('pidstat.txt')
            chunks, _, _ = generate_pidstat('pidstat.txt', header)
            if chunks:
                details['pidstat_cpu'] = _chunks_to_response(chunks, header, {
                    '%usr': {'warn': 50, 'crit': 80},
                    '%system': {'warn': 20, 'crit': 40},
                    '%wait': {'warn': 10, 'crit': 25},
                })
        except Exception as e:
            log.warning(f'pidstat CPU details failed: {e}')

    # pidstat IO
    if os.path.exists('pidstat-io.txt'):
        try:
            header = pidstatio_extract_header_line('pidstat-io.txt')
            chunks, _, _ = generate_pidstatio('pidstat-io.txt', header)
            if chunks:
                details['pidstat_io'] = _chunks_to_response(chunks, header)
        except Exception as e:
            log.warning(f'pidstat IO details failed: {e}')

    # pidstat Memory
    if os.path.exists('pidstat-memory.txt'):
        try:
            header = pidstatmem_extract_header_line('pidstat-memory.txt')
            chunks, _, _ = generate_pidstatmem('pidstat-memory.txt', header)
            if chunks:
                details['pidstat_memory'] = _chunks_to_response(chunks, header, {
                    '%MEM': {'warn': 20, 'crit': 50},
                })
        except Exception as e:
            log.warning(f'pidstat Memory details failed: {e}')

    # top
    if os.path.exists('top.txt'):
        try:
            chunks_js, timestamps = generate_top('top.txt')
            # generate_top returns a JS object string; re-parse the raw file instead
            chunks = _parse_top_file('top.txt')
            if chunks:
                header = 'Timestamp PID USER PR NI VIRT RES SHR S %CPU %MEM TIME+ COMMAND'
                details['top'] = _chunks_to_response(chunks, header, {
                    '%CPU': {'warn': 50, 'crit': 80},
                    '%MEM': {'warn': 20, 'crit': 50},
                })
        except Exception as e:
            log.warning(f'top details failed: {e}')

    # iotop
    if os.path.exists('iotop.txt'):
        try:
            chunks = _parse_iotop_file('iotop.txt')
            if chunks:
                header = 'Timestamp TID PRIO USER DISK_READ DISK_WRITE SWAPIN IO% COMMAND'
                details['iotop'] = _chunks_to_response(chunks, header)
        except Exception as e:
            log.warning(f'iotop details failed: {e}')

    os.chdir(orig)
    return details


def _parse_top_file(path: str) -> dict:
    chunks: dict[str, str] = {}
    current_ts = None
    lines_buf: list[str] = []

    def flush():
        if current_ts and lines_buf:
            chunks[current_ts] = '\n'.join(lines_buf)

    with open(path, 'r', errors='replace') as f:
        for line in f:
            if 'top - ' in line:
                flush()
                parts = line.split()
                current_ts = parts[2] if len(parts) > 2 else None
                lines_buf = []
            elif (line.strip() and current_ts
                  and not any(line.startswith(p) for p in
                              ('top', '%', 'Tasks', 'Cpu', 'MiB', 'KiB', 'Mem', 'Swap', 'PID'))):
                parts = line.strip().split(None, 12)
                if len(parts) >= 12 and parts[0].isdigit():
                    lines_buf.append(f"{current_ts} " + ' '.join(parts[:12]))
    flush()
    return chunks


def _parse_iotop_file(path: str) -> dict:
    """Parse iotop.txt into {timestamp: text_block} chunks.

    Supports two formats:
    - New: lines like "12:31:30 Total DISK READ..." mark timestamp boundaries;
      process rows look like: b'12:31:31    8365 be/4 root  ...'
    - Legacy: starts with weekday names (Mon/Tue/...), timestamp on prev line.
    """
    chunks: dict[str, str] = {}
    current_ts = None
    lines_buf: list[str] = []

    def flush():
        if current_ts and lines_buf:
            chunks[current_ts] = '\n'.join(lines_buf)

    with open(path, 'r', errors='replace') as f:
        for line in f:
            s = line.strip()
            if not s:
                continue

            # "12:31:30 Total DISK READ ..." — timestamp boundary
            if 'Total DISK READ' in s:
                flush()
                current_ts = s.split()[0]  # "12:31:30"
                lines_buf = []
                continue

            # Skip "Actual DISK READ" / "Current DISK READ" summary lines and column headers
            if 'Actual DISK' in s or 'Current DISK' in s or s.startswith('TIME') or s.startswith('TID'):
                continue

            # Process data rows: b'12:31:31    8365 be/4 root ...'  (RHEL/older iotop)
            if s.startswith("b'") or s.startswith('b"'):
                inner = s[2:].rstrip("'\"")
                parts = inner.split(None, 8)
                if len(parts) >= 7 and parts[1].isdigit():
                    row = f"{parts[0]} " + ' '.join(parts[1:])
                    lines_buf.append(row)
                continue

            # Plain format: "HH:MM:SS   TID  PRIO  USER ..."  (Ubuntu / newer iotop)
            if current_ts:
                parts = s.split(None, 8)
                if len(parts) >= 7 and parts[1].isdigit() and ':' in parts[0]:
                    lines_buf.append(f"{parts[0]} " + ' '.join(parts[1:]))

    flush()
    return chunks


# ── Vercel handler ────────────────────────────────────────────────────────────

class handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def _send_json(self, data, status=200):
        body = json.dumps(data).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Content-Length', '0')
        self.end_headers()

    def do_POST(self):
        work_dir = None
        try:
            parts = parse_cgi_multipart(self)
            file_data = parts.get('file')
            if not file_data:
                self._send_json({'error': 'No file field in form data'}, 400)
                return

            hex_id = secrets.token_hex(8)
            work_dir = os.path.join('/tmp', hex_id)
            os.makedirs(work_dir, exist_ok=True)

            try:
                with tarfile.open(fileobj=io.BytesIO(file_data), mode='r:gz') as tar:
                    safe_members = []
                    for m in tar.getmembers():
                        m.name = re.sub(r'^(/|\.\./?)+', '', m.name)
                        if m.name:
                            safe_members.append(m)
                    tar.extractall(path=work_dir, members=safe_members, filter='data')
            except tarfile.TarError as e:
                self._send_json({'error': f'Invalid tar.gz file: {e}'}, 400)
                return

            # Flatten single-subdir archives
            entries = os.listdir(work_dir)
            if len(entries) == 1 and os.path.isdir(sub := os.path.join(work_dir, entries[0])):
                for item in os.listdir(sub):
                    src = os.path.join(sub, item)
                    dst = os.path.join(work_dir, item)
                    if not os.path.exists(dst):
                        shutil.move(src, dst)
                shutil.rmtree(sub, ignore_errors=True)

            report: dict = {'report_id': hex_id}
            report['metadata'] = extract_metadata(work_dir)

            sc = extract_sysconfig(work_dir)
            if sc:
                report['sysconfig'] = sc

            perf = extract_performance(work_dir)
            if perf:
                report['performance'] = perf

            activity = extract_process_activity(work_dir)
            if activity:
                report['process_activity'] = activity

            details = extract_process_details(work_dir)
            if details:
                report['process_details'] = details

            self._send_json(report)

        except Exception as e:
            import traceback
            log.error(traceback.format_exc())
            self._send_json({'error': f'Processing failed: {e}'}, 500)
        finally:
            if work_dir and os.path.exists(work_dir):
                shutil.rmtree(work_dir, ignore_errors=True)
