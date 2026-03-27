import { useState, useRef } from 'react';
import type { DragEvent, ChangeEvent } from 'react';

interface Props {
  onFile: (file: File) => void;
  disabled?: boolean;
}

export default function UploadBox({ onFile, disabled }: Props) {
  const [dragging, setDragging] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  function handleDrop(e: DragEvent) {
    e.preventDefault();
    setDragging(false);
    const file = e.dataTransfer.files[0];
    if (file) onFile(file);
  }

  function handleChange(e: ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (file) onFile(file);
  }

  return (
    <div
      onClick={() => !disabled && inputRef.current?.click()}
      onDragOver={e => { e.preventDefault(); setDragging(true); }}
      onDragLeave={() => setDragging(false)}
      onDrop={handleDrop}
      className={`relative flex flex-col items-center justify-center gap-4 p-12 rounded-2xl border-2 border-dashed cursor-pointer transition-all duration-200 ${
        dragging
          ? 'border-indigo-400 bg-indigo-950/30'
          : disabled
          ? 'border-[#2d3149] opacity-50 cursor-not-allowed'
          : 'border-[#2d3149] hover:border-indigo-500 hover:bg-[#21263a]/50'
      }`}
    >
      <div className="w-16 h-16 rounded-2xl bg-indigo-600/20 border border-indigo-500/30 flex items-center justify-center text-3xl">
        📦
      </div>
      <div className="text-center">
        <p className="text-slate-200 font-semibold text-lg">Drop your archive here</p>
        <p className="text-slate-500 text-sm mt-1">or click to browse — .tar.gz files only</p>
      </div>
      <input
        ref={inputRef}
        type="file"
        accept=".tar.gz,.tgz"
        className="hidden"
        onChange={handleChange}
        disabled={disabled}
      />
    </div>
  );
}
