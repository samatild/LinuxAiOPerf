import { Activity, Box, Database, Server } from 'lucide-react';
import type { ReportData } from '../../../types/report';
import { summarizeReport } from './reportSummary';

export default function OverviewTab({ data }: { data: ReportData }) {
  const summary = summarizeReport(data);
  const { metadata } = data;
  const systemDetails = [
    ['Host', metadata.hostname],
    ['Operating system', metadata.os],
    ['Kernel', metadata.kernel],
    ['CPU', metadata.cpu_model],
    ['Collected', metadata.collection_date],
  ].filter(([, value]) => Boolean(value));
  const cards = [
    { label: 'Interactive charts', value: summary.figures, icon: Activity },
    { label: 'Process snapshots', value: summary.snapshots, icon: Database },
    { label: 'Volume groups', value: summary.volumeGroups, icon: Server },
    { label: 'Logical volumes', value: summary.logicalVolumes, icon: Box },
  ].filter(card => card.value > 0);

  return (
    <div className="space-y-6">
      <section className="rounded-xl p-6" style={{ background: 'var(--bg-elevated)', border: '1px solid var(--border)' }}>
        <p className="text-xs font-semibold uppercase tracking-widest" style={{ color: 'var(--accent)' }}>Report overview</p>
        <h2 className="text-2xl font-semibold mt-2" style={{ color: 'var(--text-primary)' }}>
          {metadata.hostname ? `Performance report for ${metadata.hostname}` : 'Performance report'}
        </h2>
        <p className="mt-2 text-sm max-w-2xl" style={{ color: 'var(--text-secondary)' }}>
          Use the tabs to explore host configuration, interactive telemetry charts, and time-indexed process details.
        </p>
        {systemDetails.length > 0 && (
          <dl className="grid sm:grid-cols-2 xl:grid-cols-3 gap-x-8 gap-y-4 mt-6">
            {systemDetails.map(([label, value]) => (
              <div key={label}>
                <dt className="text-xs" style={{ color: 'var(--text-muted)' }}>{label}</dt>
                <dd className="text-sm mt-0.5 break-words" style={{ color: 'var(--text-primary)' }}>{value}</dd>
              </div>
            ))}
          </dl>
        )}
      </section>
      {cards.length > 0 && (
        <section className="grid grid-cols-2 xl:grid-cols-4 gap-4">
          {cards.map(({ label, value, icon: Icon }) => (
            <div key={label} className="rounded-xl p-4" style={{ background: 'var(--bg-elevated)', border: '1px solid var(--border)' }}>
              <Icon size={18} style={{ color: 'var(--accent)' }} />
              <div className="text-2xl font-semibold mt-4" style={{ color: 'var(--text-primary)' }}>{value.toLocaleString()}</div>
              <div className="text-xs mt-1" style={{ color: 'var(--text-secondary)' }}>{label}</div>
            </div>
          ))}
        </section>
      )}
    </div>
  );
}
