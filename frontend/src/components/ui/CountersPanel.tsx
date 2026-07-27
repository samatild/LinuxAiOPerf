import { useState } from 'react';
import { createPortal } from 'react-dom';
import { BookOpen, X } from 'lucide-react';
import countersText from '../../assets/counters.txt?raw';

export default function CountersPanel() {
  const [open, setOpen] = useState(false);

  return (
    <>
      <button
        onClick={() => setOpen(o => !o)}
        title="Counters Reference"
        aria-label="Counters Reference"
        className="flex items-center gap-2 px-3 h-8 rounded-md text-sm transition-colors"
        style={
          open
            ? { background: 'var(--accent)', color: 'var(--accent-fg)' }
            : {
                background: 'var(--bg-elevated)',
                border: '1px solid var(--border)',
                color: 'var(--text-secondary)',
              }
        }
      >
        <BookOpen size={14} />
        <span>Counters</span>
      </button>

      {open && createPortal(
        <>
          <div
            className="fixed top-0 right-0 h-full w-[480px] z-[60] shadow-2xl flex flex-col"
            style={{ background: 'var(--bg-base)', borderLeft: '1px solid var(--border)' }}
          >
            <div
              className="flex items-center justify-between px-5 py-4 shrink-0"
              style={{ borderBottom: '1px solid var(--border)' }}
            >
              <div>
                <h3 className="text-sm font-semibold" style={{ color: 'var(--text-primary)' }}>Counters Reference</h3>
                <p className="text-xs mt-0.5" style={{ color: 'var(--text-muted)' }}>Metric descriptions and units</p>
              </div>
              <button
                onClick={() => setOpen(false)}
                className="flex items-center justify-center w-7 h-7 rounded-md transition-colors"
                style={{ color: 'var(--text-muted)' }}
              >
                <X size={14} />
              </button>
            </div>
            <pre className="mono flex-1 overflow-y-auto px-5 py-4 text-xs leading-relaxed whitespace-pre-wrap" style={{ color: 'var(--text-secondary)' }}>
              {countersText}
            </pre>
          </div>
          <div
            className="fixed inset-0 z-50 bg-black/40 backdrop-blur-sm"
            onClick={() => setOpen(false)}
          />
        </>,
        document.body,
      )}
    </>
  );
}
