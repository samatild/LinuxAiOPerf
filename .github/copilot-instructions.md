# LinuxAiOPerf — Copilot Instructions

## Project Overview

Flask web application that accepts a `.tar.gz` archive of Linux performance data collected by `build/linux_aio_perfcheck.sh` and generates a single self-contained interactive HTML report. The report embeds Plotly charts and uses tab/subtab navigation driven by vanilla JS.

Example data archives live in `examples/` (RHEL 9 and Ubuntu 20.04).

**Active goal:** Migrate to a modern serverless stack (Node.js/Go backend + React frontend, Vercel-compatible, Docker fallback) while replicating all current report functionality with improved UI/UX.

---

## Running Locally

```bash
# With Docker (recommended)
docker compose up --build
# App available at http://localhost:8000

# Direct (development)
cd webapp
pip install -r requirements.txt
UPLOAD_FOLDER=./uploads flask run --host=0.0.0.0 --port=8000
```

There is no automated test suite. Validate changes by uploading one of the `examples/` archives and inspecting the generated report.

---

## Architecture

```
webapp/
├── app.py                          # Flask entry point — upload, view_report routes
├── core/
│   ├── base.py                     # Abstract base classes for all processors
│   └── datetime_utils.py           # Shared timestamp parsing/enrichment
└── domains/
    ├── factory.py                  # ProcessorFactory — registry of processor types
    ├── perfanalysis/               # Time-series processors (CPU, disk, memory, network)
    ├── procinfo/                   # pidstat / top / iotop table data
    ├── procperf/                   # Top-N process activity charts
    ├── sysconfig/                  # Static system info + LVM diagram
    ├── htmlgeneration/             # Report assembly (template.html + html_generator.py)
    └── webapp/                     # FileManager (upload/extract) + ScriptExecutor
```

### Request lifecycle

1. `POST /upload` → `FileManager.process_upload()` extracts the tar.gz into a unique hex directory under `UPLOAD_FOLDER` (`/linuxaio/digest/` in prod).
2. `ScriptExecutor` runs `linuxaioperf.py` **with the unique dir as CWD** — all processors open data files by bare filename (e.g. `mpstat.txt`), so CWD must be the extracted archive directory.
3. `PerformanceReportGenerator` calls `ProcessorFactory` → each processor's `.process()` pipeline → Plotly figures → `generate_report()`.
4. `generate_report()` loads `domains/htmlgeneration/template.html` and does string replacement on `<!-- placeholder -->` comments to inject charts, tables, and config sections.
5. The resulting `linuxaioperf_report.html` is served via `GET /view_report?dir=<path>`.
6. A background thread deletes directories older than 10 minutes every 600 s.

---

## Key Conventions

### Adding a new processor

All time-series processors must subclass `core.base.BaseDataProcessor` and implement:
- `extract_header()` → `str`
- `filter_data_lines()` → `List[str]`
- `process_data()` → `pd.DataFrame`
- `create_plots(df)` → `List[go.Figure]`

Use `self.get_common_plot_layout(title, x_title, y_title)` for consistent Plotly layout (seaborn template, range selector buttons, date x-axis).

Register the new processor in `domains/factory.py`'s `_processors` dict.

For non-time-series system info, subclass `SystemInfoProcessor` and implement `extract_system_info()`.
For process snapshot data (pidstat/top/iotop), subclass `ProcessInfoProcessor` and implement `extract_process_data()`.

### Timestamp handling

Raw data files often have time-only timestamps (`HH:MM:SS`). Use `core.datetime_utils` helpers:
- `parse_collection_date(input_file)` — reads the co-located `info.txt` to get the collection date.
- `enrich_timestamps(series, date)` — prepends date to produce full `datetime` values.
- `normalize_ampm_timestamps(line)` — normalises 12-hour AM/PM strings (RHEL) to 24-hour.

### HTML report injection

`template.html` contains `<!-- section.name_placeholder -->` comments. `html_generator.py` replaces them with generated HTML fragments. Follow the existing naming pattern when adding new sections.

LVM Layout tab is only injected when `lvs.txt` is non-empty (detected via `os.stat("lvs.txt").st_size != 0`). Apply the same conditional pattern for any optional features.

Static assets (CSS/JS) are referenced via Flask `/static/` URLs hardcoded in `html_generator.py` — do not use relative paths.

### File layout expectations

When `linuxaioperf.py` runs, the CWD contains the flat list of collected `.txt` files (e.g. `mpstat.txt`, `iostat-data.out`, `vmstat-data.out`, `diskstats_log.txt`, etc.). Processors open files by name only — no directory prefix.

### LVM visualisation

`domains/sysconfig/lvm/lvmviz.py` uses **Graphviz** (system package + Python `graphviz` binding) to render the PV→VG→LV diagram. The `graphviz` apt package must be present (see `Dockerfile`).

---

## Data Source → Tab Mapping

| Source file | Report tab / subtab | Notes |
|---|---|---|
| `info.txt`, `os-release` | System Configuration → Information | Runtime info + OS release |
| `lshw.txt`, `dmidecode.txt` | System Configuration → Hardware | |
| `lsscsi.txt`, `lsblk-f.txt`, `df-h.txt`, `ls-l-dev-mapper.txt` | System Configuration → Storage | |
| `pvs.txt`, `vgs.txt`, `lvs.txt`, `pvdisplay.txt`, `vgdisplay.txt`, `lvdisplay.txt` | System Configuration → LVM Layout | Only shown when `lvs.txt` is non-empty; rendered via Graphviz |
| `lscpu.txt` | System Configuration → CPU Info | |
| `meminfo.txt` | System Configuration → Memory Info | |
| `sysctl.txt` | System Configuration → Kernel Parameters | |
| `lsmod.txt` | System Configuration → Kernel Modules | |
| `sestatus.txt`, `apparmor_status.txt` | System Configuration → Security | |
| `mpstat.txt` | System Performance → CPU Load Distribution | One plot per metric; filterable per CPU core |
| `vmstat-data.out` | System Performance → Memory Usage | |
| `iostat-data.out` | System Performance → Disk Metrics/Device | One plot per drive; filter by metric |
| `iostat-data.out` | System Performance → Disk Device/Metrics | One plot per metric; filter by device |
| `diskstats_log.txt` | System Performance → High Resolution Disk Metrics | Optional (50 ms sampling); latency boxplot; variable time granularity |
| `sarnetwork.txt` | System Performance → Network Performance | |
| `pidstat.txt` | Process Activity → Top Processes by CPU | Top 10 over time |
| `pidstat-io.txt` | Process Activity → Top 10 IO Processes | Top 10 over time |
| `pidstat-memory.txt` | Process Activity → Top 10 Memory Processes | Top 10 over time |
| `pidstat.txt` | Process Details → Process Stats (CPU) | Searchable timestamp combobox → full process table |
| `pidstat-io.txt` | Process Details → Process Stats (IO) | Searchable timestamp combobox → full process table |
| `pidstat-memory.txt` | Process Details → Process Stats (Memory) | Searchable timestamp combobox → full process table |
| `top.txt` | Process Details → top | Searchable timestamp combobox → full process table |
| `iotop.txt` | Process Details → iotop | Searchable timestamp combobox → full process table |

---

## Migration Plan (Serverless Rewrite)

The migration targets a modern, serverless architecture deployed on Vercel (or locally via Docker):

- **Backend:** Node.js or Go — serverless functions that accept the tar.gz upload, parse/transform raw data files, and return JSON
- **Frontend:** React — renders interactive charts and tables; must remain fast (current Flask app is fast because report is pre-built server-side)
- **Charts:** Choose a library capable of handling large time-series datasets (e.g. uPlot, ECharts, or Recharts)
- **Hosting:** Vercel-compatible preferred; Docker compose fallback for local/self-hosted

### Migration phases
1. Analyse current codebase — understand every data file format and parsing logic before writing new parsers
2. Design API contract — define JSON schemas returned by each serverless function, one per data domain
3. Create a new branch and scaffold the frontend/backend skeleton
4. Migrate tab by tab, subtab by subtab — replicate functionality first, then improve UX
5. No regressions: validate each subtab against the `examples/` archives
