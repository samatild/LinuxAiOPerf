import { useState } from 'react';
import Plotly from 'plotly.js-dist-min';
import type { ReportData } from '../../types/report';
import { selectAuditFigures } from './auditExport';

type Notes = Record<string, string>;
type ChartImage = { section: string; title: string; source: string };

const NOTE_SECTIONS = ['Host context', 'Storage configuration', 'CPU', 'Memory', 'Disk', 'Network', 'Process activity'];

function escapeHtml(value: unknown) {
  return String(value ?? '—').replace(/[&<>'"]/g, char => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[char]!));
}
function gib(value?: number) { return value === undefined ? '—' : `${(value / 1024 ** 3).toFixed(2)} GiB`; }
function noteHtml(notes: Notes, section: string) { return notes[section]?.trim() ? `<p class="note"><b>Note</b>${escapeHtml(notes[section].trim())}</p>` : ''; }
function rows(rows: string[][]) { return rows.map(row => `<tr>${row.map(value => `<td>${escapeHtml(value)}</td>`).join('')}</tr>`).join(''); }
function table(headers: string[], body: string[][]) { return `<table><thead><tr>${headers.map(value => `<th>${escapeHtml(value)}</th>`).join('')}</tr></thead><tbody>${rows(body)}</tbody></table>`; }

function storageHtml(data: ReportData, notes: Notes) {
  const storage = data.sysconfig?.storage;
  const topology = data.sysconfig?.lvm?.topology;
  const filesystemRows = (storage?.capacity ?? []).map(item => [item.filesystem, item.mount, item.size, item.used, item.available, `${item.use_percent}%`, item.severity]);
  const lvm = topology ? `<h3>LVM layout</h3>${table(['Logical volume', 'Volume group', 'Size', 'Type', 'Device'], topology.lvs.map(item => [item.name, item.vg, item.size, item.type, item.device_mapper ?? '—']))}` : '<p>No LVM topology was collected.</p>';
  const filesystems = filesystemRows.length ? `<h3>Filesystems</h3>${table(['Filesystem', 'Mount', 'Size', 'Used', 'Available', 'Use', 'Risk'], filesystemRows)}` : '';
  return `<section><h2>Storage configuration</h2>${noteHtml(notes, 'Storage configuration')}${lvm}${filesystems}</section>`;
}

function chartHtml(charts: ChartImage[], notes: Notes) {
  const groups = new Map<string, ChartImage[]>();
  charts.forEach(chart => groups.set(chart.section, [...(groups.get(chart.section) ?? []), chart]));
  return [...groups.entries()].map(([section, figures]) => `<section class="chart-section"><h2>${escapeHtml(section)}</h2>${noteHtml(notes, section)}${figures.map(chart => `<article class="chart"><h3>${escapeHtml(chart.title)}</h3><img src="${chart.source}" alt="${escapeHtml(chart.title)}" /></article>`).join('')}</section>`).join('');
}

function printDocument(data: ReportData, charts: ChartImage[], notes: Notes) {
  const popup = window.open('', '_blank');
  if (!popup) throw new Error('Popup blocked. Allow popups to export the audit PDF.');
  popup.opener = null;
  const meta = data.metadata;
  const health = data.capture_health;
  const logo = (document.querySelector('header img[alt="Linux AIO"]') as HTMLImageElement | null)?.src ?? '';
  const webappUrl = window.location.origin;
  const healthHtml = health ? `<section><h2>Capture health</h2><div class="metrics"><div><b>Peak load / CPU</b><span>${escapeHtml(health.peak_normalized_load_1m?.toFixed(2))}</span></div><div><b>Available memory</b><span>${escapeHtml(gib(health.min_available_memory_bytes))}</span></div><div><b>Swap in use</b><span>${escapeHtml(gib(health.peak_swap_used_bytes))}</span></div><div><b>Logical CPUs</b><span>${escapeHtml(health.cpu_count)}</span></div></div></section>` : '';
  popup.document.write(`<!doctype html><html><head><title>Linux AiO – Performance Report</title><style>
    @page{size:A4;margin:14mm}*{box-sizing:border-box}body{color:#17212b;font:10pt Inter,Arial,sans-serif;margin:0}header{display:flex;align-items:center;gap:5mm;border-bottom:2px solid #1c75bc;padding-bottom:4mm}header img{height:14mm;max-width:42mm;object-fit:contain}h1{font-size:22pt;margin:0}h2{font-size:14pt;margin:8mm 0 3mm;border-bottom:1px solid #d5dce5;padding-bottom:2mm}h3{font-size:10pt;margin:4mm 0 2mm}.subtitle,.footer{color:#52616f}.context,.metrics{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:3mm 8mm}.context b,.metrics b{display:block;color:#52616f;font-size:8pt;text-transform:uppercase;letter-spacing:.04em}.context span,.metrics span{display:block;margin-top:1mm;font-size:11pt}.metrics div{border:1px solid #d5dce5;border-radius:3mm;padding:3mm}table{border-collapse:collapse;width:100%}th,td{padding:2mm;border-bottom:1px solid #d5dce5;text-align:left;vertical-align:top}th{color:#52616f;font-size:8pt;text-transform:uppercase}.note{white-space:pre-wrap;background:#fff8dc;border-left:3px solid #d89b00;padding:3mm;margin:3mm 0}.note b{display:block;font-size:8pt;text-transform:uppercase;color:#725300;margin-bottom:1mm}.chart-section,.chart{break-inside:avoid;page-break-inside:avoid}.chart{margin-top:5mm}.chart img{width:100%;max-height:165mm;object-fit:contain}.footer{margin-top:8mm;font-size:8pt}.footer a{color:#1c75bc}@media print{.no-print{display:none}}
  </style></head><body><button class="no-print" onclick="window.print()">Print / Save as PDF</button><header>${logo ? `<img src="${logo}" alt="Linux AiO" />` : ''}<div><h1>Linux AiO – Performance Report</h1><p class="subtitle">Local audit export — raw output and process details are intentionally excluded.</p></div></header><section><h2>Host context</h2>${noteHtml(notes, 'Host context')}<div class="context"><div><b>Hostname</b><span>${escapeHtml(meta.hostname)}</span></div><div><b>Report started</b><span>${escapeHtml(meta.capture_start)}</span></div><div><b>Report finished</b><span>${escapeHtml(meta.capture_end)}</span></div><div><b>Collection runtime</b><span>${escapeHtml(meta.runtime)}</span></div><div><b>Operating system</b><span>${escapeHtml(meta.os)}</span></div><div><b>Kernel</b><span>${escapeHtml(meta.kernel)}</span></div><div><b>CPU model</b><span>${escapeHtml(meta.cpu_model)}</span></div><div><b>Report ID</b><span>${escapeHtml(data.report_id)}</span></div></div></section>${healthHtml}${storageHtml(data, notes)}${chartHtml(charts, notes)}<p class="footer">Generated locally from this report · <a href="${escapeHtml(webappUrl)}">${escapeHtml(webappUrl)}</a></p></body></html>`);
  popup.document.close(); popup.focus();
}

export default function AuditExportButton({ data }: { data: ReportData }) {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string>();
  const [notesOpen, setNotesOpen] = useState(false);
  const [notes, setNotes] = useState<Notes>({});
  const exportAudit = async () => {
    setBusy(true); setError(undefined);
    const selected = selectAuditFigures(data.performance, data.process_activity);
    const root = document.createElement('div'); root.style.cssText = 'position:fixed;left:-10000px;top:0;width:1200px;height:650px;'; document.body.appendChild(root);
    try {
      const charts: ChartImage[] = [];
      for (const item of selected) {
        const node = document.createElement('div'); node.style.cssText = 'width:1200px;height:650px;'; root.appendChild(node);
        await Plotly.newPlot(node, item.figure.data as Plotly.Data[], item.figure.layout as Plotly.Layout, { displayModeBar: false, staticPlot: true });
        let source: string; try { source = await Plotly.toImage(node, { format: 'svg', width: 1200, height: 650 }); } catch { source = await Plotly.toImage(node, { format: 'png', width: 1200, height: 650 }); }
        charts.push({ section: item.section, title: item.title, source }); Plotly.purge(node); node.remove();
      }
      printDocument(data, charts, notes);
    } catch (cause) { setError(cause instanceof Error ? cause.message : 'Could not prepare audit export.'); }
    finally { root.remove(); setBusy(false); }
  };
  return <>
    <button onClick={exportAudit} disabled={busy} className="px-3 py-1.5 rounded-md text-sm font-medium disabled:opacity-60" style={{ background:'var(--accent)', color:'var(--bg-base)' }}>{busy ? 'Preparing…' : 'Export'}</button>
    <button onClick={() => setNotesOpen(true)} aria-label="Open notes" className="fixed right-0 top-1/2 z-40 rounded-l-lg px-2 py-3 text-sm font-medium" style={{ background:'var(--bg-elevated)', border:'1px solid var(--border)', color:'var(--text-primary)', writingMode:'vertical-rl', transform:'rotate(180deg)' }}>Add notes</button>
    {notesOpen && <div className="fixed inset-0 z-50" role="dialog" aria-modal="true" aria-label="Report notes"><button className="absolute inset-0 w-full h-full" aria-label="Close notes" onClick={() => setNotesOpen(false)} style={{ background:'rgba(0,0,0,.45)' }} /><aside className="absolute right-0 top-0 h-full w-full max-w-md overflow-y-auto p-5" style={{ background:'var(--bg-surface)', borderLeft:'1px solid var(--border)' }}><div className="flex items-center justify-between mb-4"><h2 className="text-lg font-semibold">Notes</h2><button onClick={() => setNotesOpen(false)} className="px-2 py-1 rounded" style={{ color:'var(--text-secondary)' }}>Close</button></div><p className="text-sm mb-4" style={{ color:'var(--text-secondary)' }}>Optional notes are included only in their matching PDF section.</p><div className="grid gap-3">{NOTE_SECTIONS.map(section => <label key={section} className="text-sm" style={{ color:'var(--text-secondary)' }}>{section}<textarea value={notes[section] ?? ''} onChange={event => setNotes({ ...notes, [section]: event.target.value })} rows={3} className="mt-1 w-full rounded p-2 text-sm" style={{ background:'var(--bg-elevated)', border:'1px solid var(--border)', color:'var(--text-primary)' }} placeholder="Optional note for this section…" /></label>)}</div></aside></div>}
    {error && <span className="fixed bottom-4 right-4 z-50 rounded px-3 py-2 text-xs text-red-200" style={{ background:'var(--bg-elevated)', border:'1px solid #ef4444' }}>{error}</span>}
  </>;
}
