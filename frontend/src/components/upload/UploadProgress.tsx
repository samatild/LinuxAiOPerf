import { useEffect, useRef } from 'react';
import type { AnalysisProgress, LogLine, TransferProgress } from '../../hooks/useUpload';

interface UploadProgressProps {
  upload: TransferProgress;
  analysis: AnalysisProgress;
  log: LogLine[];
}

function formatBytes(value: number) {
  if (value < 1024) return `${value} B`;
  const units = ['KB', 'MB', 'GB', 'TB'];
  let size = value;
  let unit = -1;
  do { size /= 1024; unit += 1; } while (size >= 1024 && unit < units.length - 1);
  return `${size.toFixed(size >= 10 ? 0 : 1)} ${units[unit]}`;
}

function formatEta(seconds: number | null) {
  if (seconds === null || !Number.isFinite(seconds)) return 'calculating…';
  if (seconds < 60) return `${Math.ceil(seconds)}s remaining`;
  return `${Math.ceil(seconds / 60)}m remaining`;
}

function ProgressBar({ percent, color }: { percent: number; color: string }) {
  return (
    <div className="w-full h-2 rounded-full overflow-hidden" style={{ background: 'var(--bg-subtle, rgba(148,163,184,0.2))' }}>
      <div className="h-full rounded-full transition-all duration-300 ease-out" style={{ width: `${Math.max(2, Math.min(100, percent))}%`, background: color }} />
    </div>
  );
}

export default function UploadProgress({ upload, analysis, log }: UploadProgressProps) {
  const logRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (logRef.current) logRef.current.scrollTop = logRef.current.scrollHeight;
  }, [log.length]);

  return (
    <div className="flex flex-col gap-6 py-5 px-2">
      <section className="flex flex-col gap-2" aria-label="Upload progress">
        <div className="flex items-baseline justify-between gap-3">
          <p className="text-sm font-medium" style={{ color: 'var(--text-primary)' }}>Uploading archive</p>
          <span className="text-sm mono" style={{ color: 'var(--accent)' }}>{Math.round(upload.percent)}%</span>
        </div>
        <ProgressBar percent={upload.percent} color="var(--accent)" />
        <div className="flex flex-wrap justify-between gap-x-3 text-xs mono" style={{ color: 'var(--text-muted)' }}>
          <span>{formatBytes(upload.loaded)} / {formatBytes(upload.total)}</span>
          <span>{upload.bytesPerSecond > 0 ? `${formatBytes(upload.bytesPerSecond)}/s` : 'starting…'}</span>
          <span>{formatEta(upload.etaSeconds)}</span>
        </div>
      </section>

      <section className="flex flex-col gap-2" aria-label="Analysis progress">
        <div className="flex items-baseline justify-between gap-3">
          <p className="text-sm font-medium" style={{ color: 'var(--text-primary)' }}>{analysis.stage || 'Waiting for analysis…'}</p>
          <span className="text-sm mono" style={{ color: 'var(--accent-purple, var(--accent))' }}>{Math.round(analysis.percent)}%</span>
        </div>
        <ProgressBar percent={analysis.percent} color="var(--accent-purple, var(--accent))" />
      </section>

      <div ref={logRef} className="mono text-xs rounded-lg p-3 h-40 overflow-y-auto leading-6" style={{ background: 'var(--bg-inset, rgba(15,23,42,0.4))', border: '1px solid var(--border)', color: 'var(--text-muted)' }}>
        {log.length === 0 ? <span>Waiting for analysis output…</span> : log.map((line, i) => <div key={i}><span style={{ color: 'var(--text-secondary)' }}>›</span> {line.message}</div>)}
      </div>

      <p className="text-xs text-center" style={{ color: 'var(--text-muted)' }}>
        Upload and analysis run independently. Large archives can take several minutes to analyse.
      </p>
    </div>
  );
}
