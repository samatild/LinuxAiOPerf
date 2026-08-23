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
import gzip
import threading
import time
import urllib.parse
from functools import wraps
from http.server import BaseHTTPRequestHandler

try:  # package import on Vercel
    from .async_jobs import AnalysisJobs
except ImportError:  # top-level import from scripts/serve.py
    from async_jobs import AnalysisJobs

# ── Path setup ──────────────────────────────────────────────────────────────
# Vercel's Python runtime doesn't guarantee this file's own directory is on
# sys.path (unlike local dev / Docker, where api/ ends up importable via
# other means) — add it explicitly so sibling modules like lazy_details can
# be imported below.
API_DIR = os.path.dirname(os.path.abspath(__file__))
APP_ROOT = os.path.abspath(os.path.join(API_DIR, '..'))
sys.path.insert(0, API_DIR)
WEBAPP_DIR = os.path.join(API_DIR, '..', 'webapp')
sys.path.insert(0, WEBAPP_DIR)

import plotly.io as pio
import orjson

from domains.factory import ProcessorFactory
from domains.procperf.cpu.top_consumers import extract_top_cpu_consumers
from domains.procperf.io.top_consumers import extract_top_io_consumers
from domains.procperf.memory.top_consumers import extract_top_mem_consumers
from domains.procinfo.pidstat.pidstatcpu import pidstat_extract_header_line
from domains.procinfo.pidstat.pidstatio import pidstatio_extract_header_line
from domains.procinfo.pidstat.pidstatmem import pidstatmem_extract_header_line
from domains.sysconfig.lvm.lvmviz import (
    device_mapper_labels,
    parse_pvs,
    parse_vgs,
    parse_lvs,
    parse_dev_mapper,
    relabel_iostat_figures,
)

import lazy_details
from workdir import working_directory

logging.basicConfig(level=logging.WARNING)
log = logging.getLogger('api.upload')


def _in_upload_work_dir(function):
    """Serialize processors that require relative paths inside an upload."""
    @wraps(function)
    def wrapped(work_dir, *args, **kwargs):
        with working_directory(work_dir, restore_to=APP_ROOT):
            return function(work_dir, *args, **kwargs)
    return wrapped


# ── Helpers ──────────────────────────────────────────────────────────────────

def _human_size(path: str) -> str:
    try:
        n = os.path.getsize(path)
    except OSError:
        return 'unknown size'
    for unit in ('B', 'KB', 'MB', 'GB'):
        if n < 1024 or unit == 'GB':
            return f'{n:.1f} {unit}' if unit != 'B' else f'{n} B'
        n /= 1024
    return f'{n:.1f} GB'


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

@_in_upload_work_dir
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
            dev_mapper = parse_dev_mapper(os.path.join(work_dir, 'ls-l-dev-mapper.txt'))
            lvm_data['topology'] = {
                'pvs': [{'name': p[0], 'vg': p[1], 'size': p[2], 'free': p[3]} for p in pvs],
                'vgs': [{'name': v[0], 'size': v[1], 'free': v[2]} for v in vgs],
                'lvs': [
                    {
                        'name': l[0], 'vg': l[1], 'size': l[2], 'type': l[3],
                        'device_mapper': dev_mapper.get(f'{l[1]}-{l[0]}'),
                    }
                    for l in lvs
                ],
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

@_in_upload_work_dir
def extract_performance(work_dir: str, progress: 'ProgressReporter | None' = None) -> dict:
    orig = os.getcwd()
    os.chdir(work_dir)
    perf = {}
    iostat_device_labels = {}
    if os.path.exists('lvs.txt') and os.path.exists('ls-l-dev-mapper.txt'):
        try:
            iostat_device_labels = device_mapper_labels(parse_lvs(), parse_dev_mapper())
        except Exception as e:
            log.warning(f'Could not map device-mapper labels for iostat: {e}')

    def run_processor(ptype: str, fname: str, stage_key: str = '', label: str = '', device_labels: dict | None = None) -> list:
        if not os.path.exists(fname):
            return []
        if progress and stage_key:
            progress.begin(stage_key, f'{label} ({fname}, {_human_size(fname)})')
        try:
            proc = ProcessorFactory.create_processor(ptype, fname)
            _, figs = proc.process()
            result = [fig_to_dict(f) for f in figs]
            if device_labels:
                result = relabel_iostat_figures(result, device_labels)
        except Exception as e:
            log.warning(f'{ptype} processor failed: {e}')
            result = []
        if progress and stage_key:
            progress.finish(stage_key)
        return result

    cpu_figs = run_processor('cpu', 'mpstat.txt', 'perf_cpu', 'Processing CPU load distribution')
    if cpu_figs:
        perf['cpu'] = {'figures': cpu_figs}

    mem_figs = run_processor('memory', 'vmstat-data.out', 'perf_mem', 'Processing memory usage')
    if mem_figs:
        perf['memory'] = {'figures': mem_figs}

    disk = {}
    pd_figs = run_processor(
        'diskiostat', 'iostat-data.out', 'perf_disk_iostat',
        'Processing disk I/O per-device', iostat_device_labels)
    pm_figs = run_processor(
        'diskmetrics', 'iostat-data.out', 'perf_disk_metrics',
        'Processing disk I/O per-metric', iostat_device_labels)
    hr_figs = run_processor('diskhighres', 'diskstats_log.txt', 'perf_disk_highres', 'Processing high-resolution disk stats')
    if pd_figs:
        disk['per_device'] = {'figures': pd_figs}
    if pm_figs:
        disk['per_metric'] = {'figures': pm_figs}
    if hr_figs:
        disk['highres'] = {'figures': hr_figs}
    if disk:
        perf['disk'] = disk

    net_figs = run_processor('network', 'sarnetwork.txt', 'perf_network', 'Processing network performance')
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


@_in_upload_work_dir
def extract_process_activity(work_dir: str, progress: 'ProgressReporter | None' = None) -> dict:
    orig = os.getcwd()
    os.chdir(work_dir)
    activity = {}

    if os.path.exists('pidstat.txt'):
        if progress:
            progress.begin('activity_cpu', f'Ranking top CPU consumers (pidstat.txt, {_human_size("pidstat.txt")})')
        try:
            cpu_data = extract_top_cpu_consumers('pidstat.txt')
            figs = _top_consumers_to_figs(cpu_data, [
                ('top_usr', '%usr'), ('top_system', '%system'), ('top_wait', '%wait'),
            ])
            if figs:
                activity['cpu'] = {'figures': figs}
        except Exception as e:
            log.warning(f'process activity CPU failed: {e}')
        if progress:
            progress.finish('activity_cpu')

    if os.path.exists('pidstat-io.txt'):
        if progress:
            progress.begin('activity_io', f'Ranking top IO consumers (pidstat-io.txt, {_human_size("pidstat-io.txt")})')
        try:
            io_data = extract_top_io_consumers('pidstat-io.txt')
            figs = _top_consumers_to_figs(io_data, [
                ('top_read', 'kB_rd/s'), ('top_write', 'kB_wr/s'), ('top_iodelay', 'iodelay'),
            ])
            if figs:
                activity['io'] = {'figures': figs}
        except Exception as e:
            log.warning(f'process activity IO failed: {e}')
        if progress:
            progress.finish('activity_io')

    if os.path.exists('pidstat-memory.txt'):
        if progress:
            progress.begin('activity_mem', f'Ranking top memory consumers (pidstat-memory.txt, {_human_size("pidstat-memory.txt")})')
        try:
            mem_data = extract_top_mem_consumers('pidstat-memory.txt')
            figs = _top_consumers_to_figs(mem_data, [
                ('top_mem_pct', '%MEM'), ('top_rss', 'RSS (MB)'), ('top_vsz', 'VSZ (MB)'),
            ])
            if figs:
                activity['memory'] = {'figures': figs}
        except Exception as e:
            log.warning(f'process activity Memory failed: {e}')
        if progress:
            progress.finish('activity_mem')

    os.chdir(orig)
    return activity


# ── Process Details (timestamp-chunked snapshots, lazily loaded) ────────────
#
# Full data for every timestamp is NEVER discarded -- it stays on disk. We
# only build a byte-offset index here (cheap: no string copies) so the
# initial /api/upload response stays small (just timestamps + headers), and
# the frontend fetches one timestamp's full process table on demand via
# GET /api/chunk when the user picks it in the "Process Details" combobox.

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


def extract_process_details(work_dir: str, progress: 'ProgressReporter | None' = None) -> tuple[dict, dict]:
    """Returns (details_for_response, sections_for_registry).

    `details_for_response` only carries timestamps + header + thresholds
    (small, safe to JSON-serialize eagerly). `sections_for_registry` carries
    everything needed to serve a single timestamp's chunk later: absolute
    file path, parser kind, byte-offset index and header.
    """
    details: dict = {}
    sections: dict = {}

    def register(name, fname, kind, header, index, thresholds=None):
        if not index:
            return
        details[name] = {
            'timestamps': sorted(index.keys()),
            'header': header.split(),
        }
        if thresholds:
            details[name]['thresholds'] = thresholds
        sections[name] = {
            'path': os.path.join(work_dir, fname),
            'kind': kind,
            'header': header,
            'index': index,
            'thresholds': thresholds,
        }

    # pidstat CPU
    path = os.path.join(work_dir, 'pidstat.txt')
    if os.path.exists(path):
        if progress:
            progress.begin('details_cpu', f'Indexing process CPU snapshots (pidstat.txt, {_human_size(path)})')
        try:
            header = pidstat_extract_header_line(path)
            index = lazy_details.index_pidstat(path)
            register('pidstat_cpu', 'pidstat.txt', 'pidstat', header, index, {
                '%usr': {'warn': 50, 'crit': 80},
                '%system': {'warn': 20, 'crit': 40},
                '%wait': {'warn': 10, 'crit': 25},
            })
        except Exception as e:
            log.warning(f'pidstat CPU details failed: {e}')
        if progress:
            progress.finish('details_cpu')

    # pidstat IO
    path = os.path.join(work_dir, 'pidstat-io.txt')
    if os.path.exists(path):
        if progress:
            progress.begin('details_io', f'Indexing process IO snapshots (pidstat-io.txt, {_human_size(path)})')
        try:
            header = pidstatio_extract_header_line(path)
            index = lazy_details.index_pidstat(path)
            register('pidstat_io', 'pidstat-io.txt', 'pidstat', header, index)
        except Exception as e:
            log.warning(f'pidstat IO details failed: {e}')
        if progress:
            progress.finish('details_io')

    # pidstat Memory
    path = os.path.join(work_dir, 'pidstat-memory.txt')
    if os.path.exists(path):
        if progress:
            progress.begin('details_mem', f'Indexing process memory snapshots (pidstat-memory.txt, {_human_size(path)})')
        try:
            header = pidstatmem_extract_header_line(path)
            index = lazy_details.index_pidstat(path)
            register('pidstat_memory', 'pidstat-memory.txt', 'pidstat', header, index, {
                '%MEM': {'warn': 20, 'crit': 50},
            })
        except Exception as e:
            log.warning(f'pidstat Memory details failed: {e}')
        if progress:
            progress.finish('details_mem')

    # top
    path = os.path.join(work_dir, 'top.txt')
    if os.path.exists(path):
        if progress:
            progress.begin('details_top', f'Indexing top snapshots (top.txt, {_human_size(path)})')
        try:
            index = lazy_details.index_top(path)
            header = 'Timestamp PID USER PR NI VIRT RES SHR S %CPU %MEM TIME+ COMMAND'
            register('top', 'top.txt', 'top', header, index, {
                '%CPU': {'warn': 50, 'crit': 80},
                '%MEM': {'warn': 20, 'crit': 50},
            })
        except Exception as e:
            log.warning(f'top details failed: {e}')
        if progress:
            progress.finish('details_top')

    # iotop
    path = os.path.join(work_dir, 'iotop.txt')
    if os.path.exists(path):
        if progress:
            progress.begin('details_iotop', f'Indexing iotop snapshots (iotop.txt, {_human_size(path)})')
        try:
            index = lazy_details.index_iotop(path)
            header = 'Timestamp TID PRIO USER DISK_READ DISK_WRITE SWAPIN IO% COMMAND'
            register('iotop', 'iotop.txt', 'iotop', header, index)
        except Exception as e:
            log.warning(f'iotop details failed: {e}')
        if progress:
            progress.finish('details_iotop')

    return details, sections


def read_process_detail_chunk(section: dict, timestamp: str) -> dict:
    """Read + parse a single timestamp's process table on demand (lazy)."""
    offset, length = section['index'][timestamp]
    text = lazy_details.read_range(section['path'], offset, length)
    kind = section['kind']
    if kind == 'pidstat':
        return _parse_chunk_text(section['header'], lazy_details.strip_pidstat_noise(text))
    if kind == 'top':
        return lazy_details.parse_top_chunk(text)
    return lazy_details.parse_iotop_chunk(text)


# ── Progress reporting ────────────────────────────────────────────────────────
#
# Large archives can take minutes to process (pure-Python parsing of
# multi-hundred-MB pidstat/top files scales with file size). Rather than
# leaving the user staring at a blind spinner, each processing stage is
# weighted by its input file's size (parse time is roughly proportional to
# bytes read) and reports percent/verbose log messages into REPORTS so the
# frontend can poll GET /api/progress.

_WEIGHTED_STAGES = [
    'perf_cpu', 'perf_mem', 'perf_disk_iostat', 'perf_disk_metrics', 'perf_disk_highres',
    'perf_network', 'activity_cpu', 'activity_io', 'activity_mem',
    'details_cpu', 'details_io', 'details_mem', 'details_top', 'details_iotop',
]

_STAGE_FILES = {
    'perf_cpu': 'mpstat.txt',
    'perf_mem': 'vmstat-data.out',
    'perf_disk_iostat': 'iostat-data.out',
    'perf_disk_metrics': 'iostat-data.out',
    'perf_disk_highres': 'diskstats_log.txt',
    'perf_network': 'sarnetwork.txt',
    'activity_cpu': 'pidstat.txt',
    'activity_io': 'pidstat-io.txt',
    'activity_mem': 'pidstat-memory.txt',
    'details_cpu': 'pidstat.txt',
    'details_io': 'pidstat-io.txt',
    'details_mem': 'pidstat-memory.txt',
    'details_top': 'top.txt',
    'details_iotop': 'iotop.txt',
}

# Percent budget: [0, FLAT_START_PCT) covers extraction/metadata/sysconfig
# (fast, fixed steps); [FLAT_START_PCT, WEIGHTED_END_PCT) is shared across the
# size-weighted stages that are actually present in this archive;
# [WEIGHTED_END_PCT, 100] covers finalizing the response.
FLAT_START_PCT = 6
WEIGHTED_END_PCT = 98


def _compute_stage_weights(work_dir: str) -> dict:
    """Byte size of each stage's input file (0 if the file is missing)."""
    weights = {}
    for stage in _WEIGHTED_STAGES:
        path = os.path.join(work_dir, _STAGE_FILES[stage])
        weights[stage] = os.path.getsize(path) if os.path.exists(path) else 0
    return weights


class ProgressReporter:
    """Streams stage progress + verbose log lines directly onto the HTTP
    response as NDJSON lines (one JSON object per line), instead of writing
    into a shared in-memory registry that a *separate* later request would
    poll.

    This matters because the previous design (background thread + poll via
    GET /api/progress) relied on server state surviving across two distinct
    HTTP requests. That's true on a persistent process (local dev, Docker),
    but not guaranteed on classic serverless platforms like Vercel, where a
    background thread can be frozen/killed as soon as the initiating request
    ends, and a later poll request has no guarantee of landing on the same
    warm instance. Streaming progress within a single request/response
    removes that dependency entirely (see issue #88).

    Stages are weighted by input file size so the percent bar advances
    proportionally to how much data actually needs to be parsed. A background
    ticker nudges percent forward *during* a long stage (asymptotically,
    never reaching the stage's full share until finish() is called) so the
    bar doesn't freeze while a huge file is being parsed.
    """

    def __init__(self, emit, weights: dict):
        self.emit = emit  # emit(percent: float|None, message: str|None, log_it: bool)
        self.weights = weights
        self.total_weight = sum(weights.values()) or 1
        self.done_weight = 0.0
        self._ticker_stop: 'threading.Event | None' = None

    def _percent_for(self, weight: float) -> float:
        span = WEIGHTED_END_PCT - FLAT_START_PCT
        return FLAT_START_PCT + (weight / self.total_weight) * span

    def flat(self, percent: float, message: str):
        """Set an absolute percent for a fast, unweighted early/late step."""
        self.emit(percent, message, True)

    def begin(self, stage_key: str, message: str):
        weight = self.weights.get(stage_key, 0)
        self.emit(self._percent_for(self.done_weight), message, True)

        self._ticker_stop = threading.Event()
        stop_event = self._ticker_stop

        def tick():
            simulated = 0.0
            while not stop_event.wait(0.6):
                simulated += (weight - simulated) * 0.15
                self.emit(self._percent_for(self.done_weight + simulated), None, False)

        threading.Thread(target=tick, daemon=True).start()

    def finish(self, stage_key: str):
        if self._ticker_stop:
            self._ticker_stop.set()
            self._ticker_stop = None
        self.done_weight += self.weights.get(stage_key, 0)
        self.emit(self._percent_for(self.done_weight), None, False)


# ── Lazy report registry ──────────────────────────────────────────────────────
#
# The main POST /api/upload request now does all the work (extraction,
# processing, progress streaming) itself, in a single request/response — see
# issue #88: relying on a background thread plus a *second*, later request
# (GET /api/progress) to observe its result depended on server state
# surviving across two separate HTTP requests, which classic serverless
# platforms like Vercel don't guarantee (a background thread can be
# frozen/killed once the initiating request ends, and a later request has no
# guarantee of landing on the same warm instance).
#
# REPORTS is now only used to serve on-demand GET /api/chunk requests for
# large Process Details tables (pidstat/top/iotop), which are genuinely
# needed *after* the main response has already been sent (the user may click
# a different timestamp minutes later). Only the handful of files actually
# needed for that are kept on disk (instead of the whole extracted archive);
# a background sweep removes anything older than REPORT_TTL_SECONDS as a
# backstop. This still has the same small residual cross-request risk on
# serverless, but is a deliberate, bounded trade-off (see README/issue #88
# discussion) rather than the thing that was actually crashing.

REPORT_TTL_SECONDS = int(os.environ.get('REPORT_TTL_SECONDS', 15 * 60))
LOCAL_ASYNC_ANALYSIS = os.environ.get('LOCAL_ASYNC_ANALYSIS') == '1'
REPORTS: dict = {}
_REPORTS_LOCK = threading.Lock()
_cleanup_started = False
ASYNC_JOBS = AnalysisJobs()


def _prune_work_dir(work_dir: str, sections: dict):
    """Delete every extracted file that isn't referenced by `sections` (i.e.
    not needed later for on-demand /api/chunk reads). Frees the bulk of a
    report's disk/RAM footprint (mpstat.txt, ps.txt, iostat, etc. are only
    needed transiently during the initial pipeline run)."""
    keep = {os.path.abspath(s['path']) for s in sections.values()}
    try:
        for name in os.listdir(work_dir):
            path = os.path.join(work_dir, name)
            if os.path.abspath(path) in keep:
                continue
            try:
                if os.path.isfile(path) or os.path.islink(path):
                    os.remove(path)
                elif os.path.isdir(path):
                    shutil.rmtree(path, ignore_errors=True)
            except OSError as e:
                log.warning(f'failed to prune {path}: {e}')
    except OSError as e:
        log.warning(f'failed to list {work_dir} for pruning: {e}')


def _cleanup_expired_reports():
    while True:
        time.sleep(60)
        cutoff = time.time() - REPORT_TTL_SECONDS
        with _REPORTS_LOCK:
            expired = [rid for rid, entry in REPORTS.items() if entry['created'] < cutoff]
            for rid in expired:
                entry = REPORTS.pop(rid)
                shutil.rmtree(entry['work_dir'], ignore_errors=True)


def _ensure_cleanup_thread():
    global _cleanup_started
    if not _cleanup_started:
        _cleanup_started = True
        t = threading.Thread(target=_cleanup_expired_reports, daemon=True)
        t.start()


def _run_local_analysis(job_id: str, report_id: str, work_dir: str, weights: dict) -> None:
    """Run the long pipeline after Azure has returned the upload response.

    This is used only by the persistent container image.  Vercel keeps the
    synchronous NDJSON route because a serverless invocation cannot own a
    background thread once its HTTP response has ended.
    """
    registered = False
    try:
        def emit(percent, message, log_it):
            ASYNC_JOBS.progress(job_id, percent, message if log_it else None)

        reporter = ProgressReporter(emit, weights)
        report: dict = {'report_id': report_id}
        report['metadata'] = extract_metadata(work_dir)
        reporter.flat(1, 'Reading archive metadata')

        sc = extract_sysconfig(work_dir)
        if sc:
            report['sysconfig'] = sc
        reporter.flat(3, 'Reading system configuration')

        reporter.flat(FLAT_START_PCT, 'Processing performance metrics')
        perf = extract_performance(work_dir, reporter)
        if perf:
            report['performance'] = perf

        activity = extract_process_activity(work_dir, reporter)
        if activity:
            report['process_activity'] = activity

        details, sections = extract_process_details(work_dir, reporter)
        if details:
            report['process_details'] = details
        reporter.flat(99, 'Finalizing report')

        _prune_work_dir(work_dir, sections)
        _ensure_cleanup_thread()
        with _REPORTS_LOCK:
            REPORTS[report_id] = {
                'created': time.time(),
                'work_dir': work_dir,
                'sections': sections,
            }
        registered = True
        ASYNC_JOBS.complete(job_id, report)
    except Exception as exc:
        log.exception('local async analysis failed')
        ASYNC_JOBS.fail(job_id, f'Processing failed: {exc}')
    finally:
        if not registered:
            shutil.rmtree(work_dir, ignore_errors=True)


# ── Vercel handler ────────────────────────────────────────────────────────────

class handler(BaseHTTPRequestHandler):
    # Chunked transfer-encoding (used to stream progress in do_POST) requires
    # HTTP/1.1; BaseHTTPRequestHandler defaults to HTTP/1.0.
    protocol_version = 'HTTP/1.1'

    def log_message(self, format, *args):
        pass

    def _send_json(self, data, status=200):
        # The complete large report is several hundred MB.  orjson serializes
        # it faster than the stdlib and directly supports NumPy values emitted
        # by Plotly, while preserving the JSON HTTP contract.
        body = orjson.dumps(data, option=orjson.OPT_SERIALIZE_NUMPY)
        headers = {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}

        accepts_gzip = 'gzip' in self.headers.get('Accept-Encoding', '')
        if accepts_gzip and len(body) > 1024:
            body = gzip.compress(body)
            headers['Content-Encoding'] = 'gzip'

        self.send_response(status)
        for k, v in headers.items():
            self.send_header(k, v)
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Content-Length', '0')
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == '/api/job':
            self._handle_job_request(parsed)
            return
        if parsed.path == '/api/chunk':
            self._handle_chunk_request(parsed)
            return
        self._send_json({'error': 'not found'}, 404)

    def _handle_job_request(self, parsed):
        job_id = urllib.parse.parse_qs(parsed.query).get('job_id', [''])[0]
        job = ASYNC_JOBS.get(job_id)
        if not job:
            self._send_json({'error': 'job not found or lost after a container restart'}, 404)
            return
        self._send_json(job)

    def _handle_chunk_request(self, parsed):
        qs = urllib.parse.parse_qs(parsed.query)
        report_id = qs.get('report_id', [''])[0]
        section_name = qs.get('section', [''])[0]
        timestamp = qs.get('ts', [''])[0]

        with _REPORTS_LOCK:
            entry = REPORTS.get(report_id)

        if not entry:
            self._send_json({'error': 'report not found or expired, please re-upload'}, 404)
            return

        section = entry.get('sections', {}).get(section_name)
        if not section or timestamp not in section['index']:
            self._send_json({'error': 'timestamp not found'}, 404)
            return

        try:
            chunk = read_process_detail_chunk(section, timestamp)
        except Exception as e:
            log.warning(f'chunk read failed ({section_name}@{timestamp}): {e}')
            self._send_json({'error': f'failed to read chunk: {e}'}, 500)
            return

        self._send_json(chunk)

    def do_POST(self):
        work_dir = None
        register_job = False
        hex_id = None
        streaming = False
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

            weights = _compute_stage_weights(work_dir)

            if LOCAL_ASYNC_ANALYSIS:
                job_id = ASYNC_JOBS.start()
                worker = threading.Thread(
                    target=_run_local_analysis,
                    args=(job_id, hex_id, work_dir, weights),
                    daemon=True,
                )
                worker.start()
                register_job = True
                self._send_json({'job_id': job_id, 'status': 'processing'}, 202)
                return

            # Stream progress + the final result as newline-delimited JSON
            # (NDJSON) within this single request/response, instead of
            # returning immediately and handing the work off to a background
            # thread that a *separate* later request would poll (see #88 —
            # that design relied on server state surviving across two HTTP
            # requests, which isn't guaranteed on serverless platforms).
            self.send_response(200)
            self.send_header('Content-Type', 'application/x-ndjson')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Cache-Control', 'no-cache')
            self.send_header('X-Accel-Buffering', 'no')
            self.send_header('Transfer-Encoding', 'chunked')
            self.end_headers()
            streaming = True

            def emit(percent, message, log_it):
                line = {}
                if percent is not None:
                    line['percent'] = round(percent, 1)
                if message:
                    line['stage'] = message
                    if log_it:
                        line['log'] = message
                if not line:
                    return
                self._write_chunk(json.dumps(line).encode('utf-8') + b'\n')

            emit(0, 'Archive extracted, starting analysis', True)
            reporter = ProgressReporter(emit, weights)

            report: dict = {'report_id': hex_id}
            report['metadata'] = extract_metadata(work_dir)

            reporter.flat(1, 'Reading archive metadata')

            sc = extract_sysconfig(work_dir)
            if sc:
                report['sysconfig'] = sc
            reporter.flat(3, 'Reading system configuration')

            reporter.flat(FLAT_START_PCT, 'Processing performance metrics')
            perf = extract_performance(work_dir, reporter)
            if perf:
                report['performance'] = perf

            activity = extract_process_activity(work_dir, reporter)
            if activity:
                report['process_activity'] = activity

            details, sections = extract_process_details(work_dir, reporter)
            if details:
                report['process_details'] = details

            reporter.flat(99, 'Finalizing report')

            # Only files referenced by `sections` are needed later, for
            # on-demand GET /api/chunk reads (Process Details drill-down);
            # everything else can be freed from disk (and, on tmpfs, RAM)
            # right away.
            _prune_work_dir(work_dir, sections)
            _ensure_cleanup_thread()
            with _REPORTS_LOCK:
                REPORTS[hex_id] = {
                    'created': time.time(),
                    'work_dir': work_dir,
                    'sections': sections,
                }
            register_job = True

            self._write_chunk(json.dumps({'percent': 100, 'stage': 'Done', 'result': report}).encode('utf-8') + b'\n')
            self._write_chunk(b'')

        except Exception as e:
            import traceback
            log.error(traceback.format_exc())
            if streaming:
                try:
                    self._write_chunk(json.dumps({'error': f'Processing failed: {e}'}).encode('utf-8') + b'\n')
                    self._write_chunk(b'')
                except Exception:
                    pass
            else:
                self._send_json({'error': f'Processing failed: {e}'}, 500)
        finally:
            # If the job was never registered (e.g. failed before it could be
            # pruned/handed off for /api/chunk), this request still owns
            # work_dir and must clean it up itself.
            if not register_job and work_dir and os.path.exists(work_dir):
                shutil.rmtree(work_dir, ignore_errors=True)

    def _write_chunk(self, data: bytes):
        """Write one HTTP chunked-transfer-encoding frame and flush it
        immediately so the client sees progress as it happens."""
        self.wfile.write(b'%x\r\n' % len(data))
        self.wfile.write(data)
        self.wfile.write(b'\r\n')
        self.wfile.flush()
