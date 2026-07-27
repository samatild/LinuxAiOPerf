export default function AboutTab() {
  return (
    <div className="max-w-2xl space-y-8">
      <div className="flex items-center gap-5">
        <img src="/logo.png" alt="Linux AIO" className="h-16 w-auto" />
        <div>
          <h2 className="text-2xl font-bold" style={{ color: 'var(--text-primary)' }}>Linux AIO Performance</h2>
          <p className="mt-1" style={{ color: 'var(--text-secondary)' }}>All-in-one Linux Performance Collector &amp; Analyser</p>
        </div>
      </div>

      <div
        className="rounded-xl overflow-hidden"
        style={{ background: 'var(--bg-surface)', border: '1px solid var(--border)' }}
      >
        {[
          { label: 'Version', value: '2.2.0' },
          { label: 'License', value: 'MIT' },
          { label: 'Author', value: 'Samuel Matildes' },
        ].map(({ label, value }, i, arr) => (
          <div
            key={label}
            className="flex items-center justify-between px-5 py-3"
            style={i < arr.length - 1 ? { borderBottom: '1px solid var(--border)' } : undefined}
          >
            <span className="text-sm" style={{ color: 'var(--text-secondary)' }}>{label}</span>
            <span className="text-sm font-medium" style={{ color: 'var(--text-primary)' }}>{value}</span>
          </div>
        ))}
      </div>

      <div
        className="rounded-xl p-5 space-y-3"
        style={{ background: 'var(--bg-surface)', border: '1px solid var(--border)' }}
      >
        <h3 className="text-sm font-semibold uppercase tracking-wider" style={{ color: 'var(--accent)' }}>Links</h3>
        <div className="flex flex-wrap gap-3">
          <a
            href="https://github.com/samatild/LinuxAiOPerf"
            target="_blank"
            rel="noreferrer"
            className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm transition-all"
            style={{
              background: 'var(--bg-elevated)',
              border: '1px solid var(--border)',
              color: 'var(--text-secondary)',
            }}
          >
            ★ GitHub Repository
          </a>
          <a
            href="https://linuxaioperf.matildes.dev"
            target="_blank"
            rel="noreferrer"
            className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm transition-all"
            style={{
              background: 'var(--bg-elevated)',
              border: '1px solid var(--border)',
              color: 'var(--text-secondary)',
            }}
          >
            🌐 Hosted App
          </a>
        </div>
      </div>

      <div
        className="rounded-xl p-5 space-y-2"
        style={{ background: 'var(--bg-surface)', border: '1px solid var(--border)' }}
      >
        <h3 className="text-sm font-semibold uppercase tracking-wider" style={{ color: 'var(--accent)' }}>Privacy</h3>
        <p className="text-sm leading-relaxed" style={{ color: 'var(--text-secondary)' }}>
          No personal information is collected. Uploaded data is processed in memory and discarded immediately after the report is generated. No data is stored or transmitted to third parties.
        </p>
      </div>

      <div
        className="rounded-xl p-5"
        style={{ background: 'var(--bg-surface)', border: '1px solid var(--border)' }}
      >
        <h3 className="text-sm font-semibold uppercase tracking-wider mb-3" style={{ color: 'var(--accent)' }}>MIT License</h3>
        <pre className="mono text-xs whitespace-pre-wrap leading-relaxed" style={{ color: 'var(--text-muted)' }}>
{`Copyright (c) 2023 Samuel Matildes

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.`}
        </pre>
      </div>
    </div>
  );
}

