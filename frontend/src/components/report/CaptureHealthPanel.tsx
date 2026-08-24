import type { CaptureHealth } from '../../types/report';

function formatBytes(value?: number) {
  if (value === undefined) return '—';
  return `${(value / 1024 ** 3).toFixed(2)} GiB`;
}

export default function CaptureHealthPanel({ data }: { data: CaptureHealth }) {
  const cards = [
    ['Peak load / CPU', data.peak_normalized_load_1m?.toFixed(2) ?? '—', '1-minute load, normalized by logical CPUs'],
    ['Available memory', formatBytes(data.min_available_memory_bytes), 'Snapshot recorded at collection'],
    ['Swap in use', formatBytes(data.peak_swap_used_bytes), 'Snapshot recorded at collection'],
    ['Logical CPUs', data.cpu_count?.toLocaleString() ?? '—', 'Reported by lscpu'],
  ];
  return (
    <section className="grid grid-cols-2 xl:grid-cols-4 gap-4 mb-6" aria-label="Capture health summary">
      {cards.map(([label, value, description]) => (
        <div key={label} className="rounded-xl p-4" style={{ background: 'var(--bg-elevated)', border: '1px solid var(--border)' }}>
          <p className="text-xs" style={{ color: 'var(--text-secondary)' }}>{label}</p>
          <p className="text-2xl font-semibold mt-2" style={{ color: 'var(--text-primary)' }}>{value}</p>
          <p className="text-xs mt-2" style={{ color: 'var(--text-muted)' }}>{description}</p>
        </div>
      ))}
    </section>
  );
}
