interface Props {
  label: string;
  content?: string;
}

export default function TextBlock({ label, content }: Props) {
  if (!content) return null;
  return (
    <div className="mb-6">
      <h4 className="text-xs font-semibold uppercase tracking-widest text-indigo-400 mb-2">
        {label}
      </h4>
      <pre className="mono bg-[#0f1117] border border-[#2d3149] rounded-lg p-4 text-sm text-slate-300 whitespace-pre-wrap overflow-x-auto leading-relaxed max-h-[500px] overflow-y-auto">
        {content}
      </pre>
    </div>
  );
}
