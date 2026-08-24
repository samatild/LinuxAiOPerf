import { useState } from 'react';
import Plotly from 'plotly.js-dist-min';
import type { ReportData } from '../../types/report';
import { selectAuditFigures } from './auditExport';

function escapeHtml(value: unknown) {
  return String(value ?? '—').replace(/[&<>'"]/g, char => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[char]!));
}

function gib(value?: number) {
  return value === undefined ? '—' : `${(value / 1024 ** 3).toFixed(2)} GiB`;
}

function printDocument(data: ReportData, charts: { section: string; source: string }[]) {
  const popup = window.open('', '_blank');
  if (!popup) throw new Error('Popup blocked. Allow popups to export the audit PDF.');
  popup.opener = null;
  const meta = data.metadata;
  const health = data.capture_health;
  const capacity = data.sysconfig?.storage?.capacity ?? [];
  const healthHtml = health ? `<section><h2>Capture health</h2><div class="metrics">
    <div><b>Peak load / CPU</b><span>${escapeHtml(health.peak_normalized_load_1m?.toFixed(2))}</span></div>
    <div><b>Available memory</b><span>${escapeHtml(gib(health.min_available_memory_bytes))}</span></div>
    <div><b>Swap in use</b><span>${escapeHtml(gib(health.peak_swap_used_bytes))}</span></div>
    <div><b>Logical CPUs</b><span>${escapeHtml(health.cpu_count)}</span></div>
  </div></section>` : '';
  const capacityHtml = capacity.length ? `<section><h2>Filesystem capacity</h2><table><thead><tr><th>Filesystem</th><th>Mount</th><th>Used</th><th>Available</th><th>Use</th><th>Risk</th></tr></thead><tbody>${capacity.map(item => `<tr><td>${escapeHtml(item.filesystem)}</td><td>${escapeHtml(item.mount)}</td><td>${escapeHtml(item.used)}</td><td>${escapeHtml(item.available)}</td><td>${escapeHtml(item.use_percent)}%</td><td>${escapeHtml(item.severity)}</td></tr>`).join('')}</tbody></table></section>` : '';
  const chartHtml = charts.map(chart => `<section class="chart"><h2>${escapeHtml(chart.section)}</h2><img src="${chart.source}" alt="${escapeHtml(chart.section)} chart" /></section>`).join('');
  popup.document.write(`<!doctype html><html><head><title>Performance audit — ${escapeHtml(meta.hostname)}</title><style>
    @page { size: A4; margin: 14mm; } * { box-sizing: border-box; } body { color:#17212b; font: 10pt Inter,Arial,sans-serif; margin:0; } h1 { font-size:24pt; margin:0 0 5mm; } h2 { font-size:14pt; margin:8mm 0 3mm; border-bottom:1px solid #d5dce5; padding-bottom:2mm; } .subtitle { color:#52616f; margin-bottom:7mm; } .context, .metrics { display:grid; grid-template-columns:repeat(2,1fr); gap:3mm 8mm; } .context b, .metrics b { display:block; color:#52616f; font-size:8pt; text-transform:uppercase; letter-spacing:.04em; } .context span, .metrics span { display:block; margin-top:1mm; font-size:11pt; } .metrics div { border:1px solid #d5dce5; border-radius:3mm; padding:3mm; } table { border-collapse:collapse; width:100%; } th,td { padding:2mm; border-bottom:1px solid #d5dce5; text-align:left; } th { color:#52616f; font-size:8pt; text-transform:uppercase; } .chart { break-inside:avoid; page-break-inside:avoid; } img { width:100%; max-height:165mm; object-fit:contain; } .footer { margin-top:8mm; color:#52616f; font-size:8pt; } @media print { .no-print { display:none; } }
  </style></head><body><button class="no-print" onclick="window.print()">Print / Save as PDF</button><h1>Performance Audit</h1><p class="subtitle">Selective local export — raw output and process details are intentionally excluded.</p><section><h2>Host context</h2><div class="context"><div><b>Hostname</b><span>${escapeHtml(meta.hostname)}</span></div><div><b>Collection date</b><span>${escapeHtml(meta.collection_date)}</span></div><div><b>Operating system</b><span>${escapeHtml(meta.os)}</span></div><div><b>Kernel</b><span>${escapeHtml(meta.kernel)}</span></div><div><b>CPU model</b><span>${escapeHtml(meta.cpu_model)}</span></div><div><b>Report ID</b><span>${escapeHtml(data.report_id)}</span></div></div></section>${healthHtml}${capacityHtml}${chartHtml}<p class="footer">Generated locally from this report. Charts are snapshots selected for audit presentation.</p></body></html>`);
  popup.document.close();
  popup.focus();
}

export default function AuditExportButton({ data }: { data: ReportData }) {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string>();

  const exportAudit = async () => {
    setBusy(true); setError(undefined);
    const selected = selectAuditFigures(data.performance);
    const root = document.createElement('div');
    root.style.cssText = 'position:fixed;left:-10000px;top:0;width:1200px;height:650px;';
    document.body.appendChild(root);
    try {
      const charts: { section: string; source: string }[] = [];
      for (const item of selected) {
        const node = document.createElement('div'); node.style.cssText = 'width:1200px;height:650px;'; root.appendChild(node);
        await Plotly.newPlot(node, item.figure.data as Plotly.Data[], item.figure.layout as Plotly.Layout, { displayModeBar: false, staticPlot: true });
        let source: string;
        try { source = await Plotly.toImage(node, { format: 'svg', width: 1200, height: 650 }); }
        catch { source = await Plotly.toImage(node, { format: 'png', width: 1200, height: 650 }); }
        charts.push({ section: item.section, source }); Plotly.purge(node); node.remove();
      }
      printDocument(data, charts);
    } catch (cause) { setError(cause instanceof Error ? cause.message : 'Could not prepare audit export.'); }
    finally { root.remove(); setBusy(false); }
  };

  return <div className="flex flex-col items-end gap-1"><button onClick={exportAudit} disabled={busy} className="px-3 py-2 rounded-lg text-sm font-medium disabled:opacity-60" style={{ background:'var(--accent)', color:'var(--bg-base)' }}>{busy ? 'Preparing audit…' : 'Export audit PDF'}</button>{error && <span className="text-xs text-red-400">{error}</span>}</div>;
}
