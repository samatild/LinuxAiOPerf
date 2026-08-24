import { useMemo, useState } from 'react';
import { Check, Copy, Search } from 'lucide-react';
import { filterRawText } from './rawTextFilter';

interface Props {
  label: string;
  content?: string;
}

export default function TextBlock({ label, content }: Props) {
  const [query, setQuery] = useState('');
  const [copied, setCopied] = useState(false);
  const filtered = useMemo(() => filterRawText(content ?? '', query), [content, query]);

  if (!content) return null;

  async function copyContent() {
    await navigator.clipboard.writeText(content ?? '');
    setCopied(true);
    window.setTimeout(() => setCopied(false), 1600);
  }

  return (
    <div className="mb-6">
      <div className="flex flex-wrap items-center justify-between gap-2 mb-2">
        <h4
          className="text-xs font-semibold uppercase tracking-widest"
          style={{ color: 'var(--accent)' }}
        >
          {label}
        </h4>
        <div className="flex items-center gap-2">
          <label className="relative">
            <Search size={14} className="absolute left-2 top-1/2 -translate-y-1/2" style={{ color: 'var(--text-muted)' }} />
            <input
              type="search"
              value={query}
              onChange={event => setQuery(event.target.value)}
              placeholder="Filter lines…"
              aria-label={`Filter ${label}`}
              className="pl-7 pr-2 py-1.5 rounded-md text-xs w-44"
              style={{ background: 'var(--bg-elevated)', border: '1px solid var(--border)', color: 'var(--text-primary)' }}
            />
          </label>
          <button
            type="button"
            onClick={copyContent}
            className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-md text-xs"
            style={{ background: 'var(--bg-elevated)', border: '1px solid var(--border)', color: 'var(--text-secondary)' }}
          >
            {copied ? <Check size={14} /> : <Copy size={14} />}
            {copied ? 'Copied' : 'Copy'}
          </button>
        </div>
      </div>
      {query && (
        <p className="text-xs mb-2" style={{ color: 'var(--text-muted)' }}>
          {filtered ? 'Showing matching lines' : 'No matching lines'}
        </p>
      )}
      <pre
        className="mono rounded-lg p-4 text-sm whitespace-pre-wrap overflow-x-auto leading-relaxed max-h-[500px] overflow-y-auto"
        style={{
          background: 'var(--bg-elevated)',
          border: '1px solid var(--border)',
          color: 'var(--text-primary)',
        }}
      >
        {filtered || (query ? 'No matching lines.' : content)}
      </pre>
    </div>
  );
}
