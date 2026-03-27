import { useState } from 'react';
import countersText from '../../assets/counters.txt?raw';

export default function CountersPanel() {
  const [open, setOpen] = useState(false);

  return (
    <>
      {/* Floating button — always visible */}
      <button
        onClick={() => setOpen(o => !o)}
        title="Counters Reference"
        className={`fixed bottom-6 right-6 z-50 flex items-center gap-2 px-4 py-2.5 rounded-full text-sm font-medium shadow-lg transition-all duration-200 ${
          open
            ? 'bg-indigo-600 text-white shadow-indigo-900/50'
            : 'bg-[#21263a] border border-[#2d3149] text-slate-300 hover:border-indigo-500 hover:text-slate-100 shadow-black/40'
        }`}
      >
        <span>📊</span>
        <span>Counters</span>
      </button>

      {/* Sliding panel */}
      <div
        className={`fixed top-0 right-0 h-full z-40 bg-[#0f1117] border-l border-[#2d3149] shadow-2xl transition-all duration-300 flex flex-col ${
          open ? 'w-[480px]' : 'w-0 overflow-hidden'
        }`}
      >
        {open && (
          <>
            <div className="flex items-center justify-between px-5 py-4 border-b border-[#2d3149] shrink-0">
              <div>
                <h3 className="text-sm font-semibold text-slate-100">Counters Reference</h3>
                <p className="text-xs text-slate-500 mt-0.5">Metric descriptions and units</p>
              </div>
              <button
                onClick={() => setOpen(false)}
                className="text-slate-400 hover:text-slate-200 text-xl leading-none p-1"
              >
                ×
              </button>
            </div>
            <pre className="mono flex-1 overflow-y-auto px-5 py-4 text-xs text-slate-300 leading-relaxed whitespace-pre-wrap">
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
