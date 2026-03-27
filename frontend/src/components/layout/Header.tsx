import { Link } from 'react-router-dom';
import type { ReportMetadata } from '../../types/report';

interface Props {
  metadata?: ReportMetadata;
  showBack?: boolean;
}

function Chip({ icon, text }: { icon: string; text: string }) {
  return (
    <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-[#21263a] border border-[#2d3149] text-xs text-slate-300">
      <span>{icon}</span> {text}
    </span>
  );
}

export default function Header({ metadata, showBack }: Props) {
  return (
    <header className="sticky top-0 z-50 bg-[#0f1117]/95 backdrop-blur border-b border-[#2d3149] px-6 py-3">
      <div className="max-w-screen-2xl mx-auto flex items-center justify-between gap-4 flex-wrap">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-indigo-600 rounded-lg flex items-center justify-center text-white font-bold text-sm">
              L
            </div>
            <div>
              <h1 className="text-sm font-semibold text-slate-100 leading-none">
                Linux AIO Performance
              </h1>
              <p className="text-xs text-slate-500 mt-0.5">Performance Analysis Report</p>
            </div>
          </div>
          {metadata && (
            <div className="flex flex-wrap gap-2 ml-4">
              {metadata.hostname && <Chip icon="🖥" text={metadata.hostname} />}
              {metadata.os && <Chip icon="🐧" text={metadata.os} />}
              {metadata.kernel && <Chip icon="⚙" text={metadata.kernel} />}
              {metadata.cpu_model && <Chip icon="🔲" text={metadata.cpu_model} />}
              {metadata.collection_date && <Chip icon="📅" text={metadata.collection_date} />}
            </div>
          )}
        </div>
        {showBack && (
          <Link
            to="/"
            className="flex items-center gap-2 px-3 py-1.5 rounded-md bg-[#21263a] border border-[#2d3149] text-sm text-slate-300 hover:text-slate-100 hover:border-indigo-500 transition-all"
          >
            ← New Report
          </Link>
        )}
      </div>
    </header>
  );
}
