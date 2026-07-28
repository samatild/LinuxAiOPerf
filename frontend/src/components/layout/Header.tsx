import { Link } from 'react-router-dom';
import { Sun, Moon, Monitor } from 'lucide-react';
import type { ReportMetadata } from '../../types/report';
import { useTheme } from '../../hooks/useTheme';
import logo from '../../assets/logo.png';
import CountersPanel from '../ui/CountersPanel';
import KofiButton from '../ui/KofiButton';

interface Props {
  metadata?: ReportMetadata;
  showBack?: boolean;
  showCounters?: boolean;
}

function SystemIdentity({ metadata }: { metadata: ReportMetadata }) {
  const identity = [metadata.hostname, metadata.os].filter(
    (value): value is string => Boolean(value),
  );

  if (identity.length === 0) return null;

  return (
    <div
      className="flex items-center gap-2 ml-4 pl-4 text-xs min-w-0"
      style={{ borderLeft: '1px solid var(--border)', color: 'var(--text-secondary)' }}
      aria-label="Report system"
    >
      <Monitor size={14} className="shrink-0" aria-hidden="true" />
      <span className="truncate">
        {identity.map((value, index) => (
          <span key={value}>
            {index > 0 && (
              <span className="mx-2" style={{ color: 'var(--text-dim)' }} aria-hidden="true">
                ·
              </span>
            )}
            {value}
          </span>
        ))}
      </span>
    </div>
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
      {theme === 'dark' ? <Sun size={15} /> : <Moon size={15} />}
    </button>
  );
}

export default function Header({ metadata, showBack, showCounters }: Props) {
  return (
    <header
      className="sticky top-0 z-50 px-6 py-3"
      style={{
        background: 'var(--bg-surface)',
        borderBottom: '1px solid var(--border)',
        backdropFilter: 'blur(12px)',
      }}
    >
      <div className="w-[80%] max-w-[1600px] mx-auto flex items-center justify-between gap-4 flex-wrap">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-3">
            {/* Logo — clickable back to home when on report page */}
            {showBack ? (
              <Link to="/" title="New Report">
                <img src={logo} alt="Linux AIO" className="h-9 w-auto" />
              </Link>
            ) : (
              <img src={logo} alt="Linux AIO" className="h-9 w-auto" />
            )}
            <div>
              <h1 className="text-sm font-semibold leading-none" style={{ color: 'var(--text-primary)' }}>
                Linux AIO Performance
              </h1>
              <p className="text-xs mt-0.5" style={{ color: 'var(--text-muted)' }}>
                Performance Analysis Report
              </p>
            </div>
          </div>
          {metadata && <SystemIdentity metadata={metadata} />}
        </div>
        <div className="flex items-center gap-2">
          {showCounters && <CountersPanel />}
          {showBack && (
            <KofiButton compact />
          )}
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
