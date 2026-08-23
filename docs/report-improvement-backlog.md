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
