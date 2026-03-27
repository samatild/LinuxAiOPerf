interface Props {
  label: string;
  content?: string;
}

export default function TextBlock({ label, content }: Props) {
  if (!content) return null;
  return (
    <div className="mb-6">
      <h4
        className="text-xs font-semibold uppercase tracking-widest mb-2"
        style={{ color: 'var(--accent)' }}
      >
        {label}
      </h4>
      <pre
        className="mono rounded-lg p-4 text-sm whitespace-pre-wrap overflow-x-auto leading-relaxed max-h-[500px] overflow-y-auto"
        style={{
          background: 'var(--bg-elevated)',
          border: '1px solid var(--border)',
          color: 'var(--text-primary)',
        }}
      >
        {content}
      </pre>
    </div>
  );
}
