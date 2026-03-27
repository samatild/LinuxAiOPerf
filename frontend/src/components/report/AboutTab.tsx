export default function AboutTab() {
  return (
    <div className="max-w-2xl space-y-8">
      <div className="flex items-center gap-5">
        <img src="/logo.png" alt="Linux AIO" className="h-16 w-auto" />
        <div>
          <h2 className="text-2xl font-bold text-slate-100">Linux AIO Performance</h2>
          <p className="text-slate-400 mt-1">All-in-one Linux Performance Collector &amp; Analyser</p>
        </div>
      </div>

      <div className="bg-[#1a1d27] border border-[#2d3149] rounded-xl divide-y divide-[#2d3149]">
        {[
          { label: 'Version', value: '2.2.0' },
          { label: 'License', value: 'MIT' },
          { label: 'Author', value: 'Samuel Matildes' },
        ].map(({ label, value }) => (
          <div key={label} className="flex items-center justify-between px-5 py-3">
            <span className="text-sm text-slate-400">{label}</span>
            <span className="text-sm font-medium text-slate-200">{value}</span>
          </div>
        ))}
      </div>

      <div className="bg-[#1a1d27] border border-[#2d3149] rounded-xl p-5 space-y-3">
        <h3 className="text-sm font-semibold text-indigo-400 uppercase tracking-wider">Links</h3>
        <div className="flex flex-wrap gap-3">
          <a
            href="https://github.com/samatild/LinuxAiOPerf"
            target="_blank"
            rel="noreferrer"
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-[#21263a] border border-[#2d3149] text-sm text-slate-300 hover:border-indigo-500 hover:text-slate-100 transition-all"
          >
            ★ GitHub Repository
          </a>
          <a
            href="https://linuxaioperf.matildes.dev"
            target="_blank"
            rel="noreferrer"
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-[#21263a] border border-[#2d3149] text-sm text-slate-300 hover:border-indigo-500 hover:text-slate-100 transition-all"
          >
            🌐 Hosted App
          </a>
        </div>
      </div>

      <div className="bg-[#1a1d27] border border-[#2d3149] rounded-xl p-5 space-y-2">
        <h3 className="text-sm font-semibold text-indigo-400 uppercase tracking-wider">Privacy</h3>
        <p className="text-sm text-slate-400 leading-relaxed">
          No personal information is collected. Uploaded data is processed in memory and discarded immediately after the report is generated. No data is stored or transmitted to third parties.
        </p>
      </div>

      <div className="bg-[#1a1d27] border border-[#2d3149] rounded-xl p-5">
        <h3 className="text-sm font-semibold text-indigo-400 uppercase tracking-wider mb-3">MIT License</h3>
        <pre className="mono text-xs text-slate-400 whitespace-pre-wrap leading-relaxed">
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
