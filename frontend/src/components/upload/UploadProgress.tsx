import { useEffect, useRef } from 'react';
import type { LogLine } from '../../hooks/useUpload';

interface UploadProgressProps {
  percent: number;
  stage: string;
  log: LogLine[];
}

export default function UploadProgress({ percent, stage, log }: UploadProgressProps) {
  const logRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (logRef.current) {
      logRef.current.scrollTop = logRef.current.scrollHeight;
    }
  }, [log.length]);

  return (
    <div className="flex flex-col gap-4 py-8 px-2">
      <div className="flex items-baseline justify-between">
        <p className="text-sm font-medium" style={{ color: 'var(--text-primary)' }}>{stage || 'Processing archive…'}</p>
        <span className="text-sm mono" style={{ color: 'var(--accent)' }}>{Math.round(percent)}%</span>
      </div>

      <div
        className="w-full h-2 rounded-full overflow-hidden"
        style={{ background: 'var(--bg-subtle, rgba(148,163,184,0.2))' }}
      >
        <div
          className="h-full rounded-full transition-all duration-300 ease-out"
          style={{ width: `${Math.max(2, Math.min(100, percent))}%`, background: 'var(--accent)' }}
        />
      </div>

      <div
        ref={logRef}
        className="mono text-xs rounded-lg p-3 h-40 overflow-y-auto leading-6"
        style={{ background: 'var(--bg-inset, rgba(15,23,42,0.4))', border: '1px solid var(--border)', color: 'var(--text-muted)' }}
      >
        {log.length === 0 ? (
          <span>Starting…</span>
        ) : (
          log.map((line, i) => (
            <div key={i}>
              <span style={{ color: 'var(--text-secondary)' }}>›</span> {line.message}
            </div>
          ))
        )}
      </div>

      <p className="text-xs text-center" style={{ color: 'var(--text-muted)' }}>
        Large archives (hundreds of MB) can take a few minutes — this page will update automatically.
      </p>
    </div>
  );
}
