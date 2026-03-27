import { GitBranch } from 'lucide-react';
import { APP_VERSION, GITHUB_URL } from '../../version';

export default function Footer() {
  return (
    <footer
      className="mt-auto px-6 py-4 text-xs flex items-center justify-center gap-3"
      style={{ borderTop: '1px solid var(--border)', color: 'var(--text-muted)' }}
    >
      <span>Linux AIO Performance</span>
      <span style={{ color: 'var(--border)' }}>·</span>
      <span>v{APP_VERSION}</span>
      <span style={{ color: 'var(--border)' }}>·</span>
      <a
        href={GITHUB_URL}
        target="_blank"
        rel="noopener noreferrer"
        className="inline-flex items-center gap-1.5 transition-colors"
        style={{ color: 'var(--text-muted)' }}
        onMouseEnter={e => (e.currentTarget.style.color = 'var(--accent)')}
        onMouseLeave={e => (e.currentTarget.style.color = 'var(--text-muted)')}
      >
        <GitBranch size={13} />
        Source
      </a>
    </footer>
  );
}
