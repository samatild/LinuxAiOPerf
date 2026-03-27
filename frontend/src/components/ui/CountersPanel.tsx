import { useState } from 'react';
import { BookOpen, X } from 'lucide-react';
import countersText from '../../assets/counters.txt?raw';

export default function CountersPanel() {
  const [open, setOpen] = useState(false);

  return (
    <>
      {/* Floating button — always visible */}
      <button
        onClick={() => setOpen(o => !o)}
        title="Counters Reference"
        className="fixed bottom-6 right-6 z-50 flex items-center gap-2 px-3 py-2 rounded-md text-sm font-medium shadow-lg transition-all duration-200"
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

      {/* Sliding panel */}
      <div
        className={`fixed top-0 right-0 h-full z-40 shadow-2xl transition-all duration-300 flex flex-col ${
          open ? 'w-[480px]' : 'w-0 overflow-hidden'
        }`}
        style={{ background: 'var(--bg-base)', borderLeft: '1px solid var(--border)' }}
      >
        {open && (
          <>
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
          </>
        )}
      </div>

      {/* Backdrop */}
      {open && (
        <div
          className="fixed inset-0 z-30 bg-black/40 backdrop-blur-sm"
          onClick={() => setOpen(false)}
        />
      )}
    </>
  );
}
