import { Link } from 'react-router-dom';
import type { ReportMetadata } from '../../types/report';
import { useTheme } from '../../hooks/useTheme';
import logo from '../../assets/logo.png';

interface Props {
  metadata?: ReportMetadata;
  showBack?: boolean;
}

function Chip({ icon, text }: { icon: string; text: string }) {
  return (
    <span
      className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs"
      style={{
        background: 'var(--bg-muted)',
        border: '1px solid var(--border)',
        color: 'var(--text-secondary)',
      }}
    >
      <span>{icon}</span> {text}
    </span>
  );
}

function ThemeToggle() {
  const { theme, toggle } = useTheme();
  return (
    <button
      onClick={toggle}
      title={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
      className="flex items-center justify-center w-8 h-8 rounded-md transition-colors"
      style={{
        background: 'var(--bg-muted)',
        border: '1px solid var(--border)',
        color: 'var(--text-secondary)',
      }}
    >
      {theme === 'dark' ? '☀️' : '🌙'}
    </button>
  );
}

export default function Header({ metadata, showBack }: Props) {
  return (
    <header
      className="sticky top-0 z-50 px-6 py-3"
      style={{
        background: 'var(--bg-surface)',
        borderBottom: '1px solid var(--border)',
        backdropFilter: 'blur(12px)',
      }}
    >
      <div className="max-w-screen-2xl mx-auto flex items-center justify-between gap-4 flex-wrap">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-3">
            <img src={logo} alt="Linux AIO" className="h-9 w-auto" />
            <div>
              <h1 className="text-sm font-semibold leading-none" style={{ color: 'var(--text-primary)' }}>
                Linux AIO Performance
              </h1>
              <p className="text-xs mt-0.5" style={{ color: 'var(--text-muted)' }}>
                Performance Analysis Report
              </p>
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
        <div className="flex items-center gap-2">
          <ThemeToggle />
          {showBack && (
            <Link
              to="/"
              className="flex items-center gap-2 px-3 py-1.5 rounded-md text-sm transition-all"
              style={{
                background: 'var(--bg-muted)',
                border: '1px solid var(--border)',
                color: 'var(--text-secondary)',
              }}
            >
              ← New Report
            </Link>
          )}
        </div>
      </div>
    </header>
  );
}
