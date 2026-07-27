import { useState, useRef } from 'react';
import { Archive } from 'lucide-react';
import type { DragEvent, ChangeEvent, KeyboardEvent } from 'react';

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

  function handleKeyDown(e: KeyboardEvent<HTMLDivElement>) {
    if (!disabled && (e.key === 'Enter' || e.key === ' ')) {
      e.preventDefault();
      inputRef.current?.click();
    }
  }

  return (
    <div
      onClick={() => !disabled && inputRef.current?.click()}
      onDragOver={e => { e.preventDefault(); setDragging(true); }}
      onDragLeave={() => setDragging(false)}
      onDrop={handleDrop}
      onKeyDown={handleKeyDown}
      role="button"
      tabIndex={disabled ? -1 : 0}
      aria-label="Upload a Linux AIO Performance Collector archive"
      aria-disabled={disabled}
      className="upload-dropzone relative flex flex-col items-center justify-center gap-4 p-12 rounded-xl border-2 border-dashed cursor-pointer transition-all duration-200"
      style={
        dragging
          ? { borderColor: 'var(--accent)', background: 'var(--accent-subtle)' }
          : disabled
          ? { borderColor: 'var(--border)', opacity: 0.5, cursor: 'not-allowed' }
          : { borderColor: 'var(--border)' }
      }
    >
      <div
        className="upload-dropzone-icon w-14 h-14 rounded-xl flex items-center justify-center"
        style={{
          background: 'var(--accent-subtle)',
          border: '1px solid var(--accent)',
        }}
      >
        <Archive size={26} style={{ color: 'var(--accent)' }} />
      </div>
      <div className="text-center">
        <p className="font-semibold text-lg" style={{ color: 'var(--text-primary)' }}>Drop collector archive</p>
        <p className="text-sm mt-1" style={{ color: 'var(--text-muted)' }}>Drag and drop, or browse for a .tar.gz file</p>
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
