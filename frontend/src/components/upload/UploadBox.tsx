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
      className="relative flex flex-col items-center justify-center gap-4 p-12 rounded-2xl border-2 border-dashed cursor-pointer transition-all duration-200"
      style={
        dragging
          ? { borderColor: 'var(--accent)', background: 'var(--accent-subtle)' }
          : disabled
          ? { borderColor: 'var(--border)', opacity: 0.5, cursor: 'not-allowed' }
          : { borderColor: 'var(--border)' }
      }
      onMouseEnter={e => {
        if (!dragging && !disabled) {
          (e.currentTarget as HTMLDivElement).style.borderColor = 'var(--accent-hover)';
          (e.currentTarget as HTMLDivElement).style.background = 'var(--bg-elevated)';
        }
      }}
      onMouseLeave={e => {
        if (!dragging && !disabled) {
          (e.currentTarget as HTMLDivElement).style.borderColor = 'var(--border)';
          (e.currentTarget as HTMLDivElement).style.background = '';
        }
      }}
    >
      <div
        className="w-16 h-16 rounded-2xl flex items-center justify-center text-3xl"
        style={{
          background: 'var(--accent-subtle)',
          border: '1px solid var(--accent)',
          opacity: 0.8,
        }}
      >
        📦
      </div>
      <div className="text-center">
        <p className="font-semibold text-lg" style={{ color: 'var(--text-primary)' }}>Drop your archive here</p>
        <p className="text-sm mt-1" style={{ color: 'var(--text-muted)' }}>or click to browse — .tar.gz files only</p>
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
