# Report improvement backlog

Ideas identified during the report UX audit on 2026-08-24. They are deliberately separate from the currently implemented improvements, so each can be validated independently against real archives.

## 1. Full-screen chart inspector

Add an expand control to each Plotly card. The overlay should preserve Plotly's native zoom/pan/download tools, present the chart title and close with `Escape`, and use the full available viewport for wide I/O and CPU timelines.

**Why:** the normal grid is excellent for comparison, but dense time series and long device legends are hard to inspect without enlarging a chart.

**Validation:** exercise with the large archive and verify no chart trace/data is changed; only the presentation container changes.

## 2. Cross-report comparison workspace

Allow a user to load two already-downloaded report JSON files locally and compare summary counts plus selected series (for example CPU utilisation, disk throughput and top consumers). This must remain browser-local: no uploaded report data, storage service or backend persistence.

**Why:** provides a natural before/after workflow for tuning and regression validation.

**Validation:** compare a baseline and a known-equivalent report; then compare an intentionally different archive and ensure differences are explicit rather than inferred.

## 3. Report export bundle

Offer an optional client-side export containing the response JSON and a small human-readable summary/metadata file. Because reports can be very large, the implementation must use a streaming-friendly approach where supported and disclose the approximate export size before starting.

**Why:** lets users retain an ephemeral analysis after the server TTL expires.

**Validation:** test with both small and large reports, ensuring the original API response remains unchanged and that export failure does not affect viewing the report.

## 4. Performance finding annotations

Add a deterministic findings panel that highlights already-known threshold breaches from current parsed data, with links to the corresponding tab/chart. It should state the source metric and threshold rather than make opaque diagnoses.

**Why:** helps users navigate large reports without removing any raw metric or chart.

**Validation:** build fixtures with normal, warning and critical values; ensure each finding links to an existing visualisation and never fabricates a conclusion.

## 5. Capture health / resource-pressure summary

Parse the already-collected `sar-load-avg.txt`, `free.txt`, `uptime.txt`, and CPU count from `lscpu.txt` into a compact capture-health panel: peak normalised 1-minute load, maximum runnable/blocked tasks, minimum available memory, and peak swap use. Old archives must simply show no panel when those sources are absent.

**Why:** lets an operator quickly distinguish CPU, scheduler, or memory pressure without manually correlating raw files.

**Validation:** fixtures for normal, warning, missing, and malformed data; confirm that the example archive's low normalised load is not reported as pressure.

## 6. Storage-capacity risk summary

Build a structured capacity table from `df-h.txt`, enriched with `lsblk-f.txt` and existing LVM labels. Show real mounted filesystems, used percentage, free space, backing device and explicit warning/critical thresholds, while retaining the raw source blocks below.

**Why:** pseudo-filesystems currently bury the mounts that matter, and the raw `df`/`lsblk` blocks make capacity risk slower to spot.

**Validation:** fixtures must cover pseudo-filesystems, malformed rows, unavailable percentages and mount points with spaces; the existing sample must expose the real root mount but not present `proc`/`sysfs` as risks.

## 7. Accessible, robust Process Details table

Replace render-time ref caching with React state and make table sorting keyboard and screen-reader accessible. Sort headers should be native buttons with `aria-sort`; control labels should be associated with inputs; the filter must say it performs a substring match (or implement real regex support).

**Why:** it removes a known fragile render-state pattern and makes a core troubleshooting table usable without a mouse.

**Validation:** component tests for fetch/cache, keyboard sorting, `aria-sort`, timestamp changes, filtering and loading/error states; `npm run lint` should no longer report DataTable render-time-ref errors.
