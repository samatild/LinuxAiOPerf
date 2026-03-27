import { useState } from 'react';
import type { ReportData } from '../types/report';

type UploadState =
  | { status: 'idle' }
  | { status: 'uploading'; progress: number }
  | { status: 'done'; data: ReportData }
  | { status: 'error'; message: string };

export function useUpload() {
  const [state, setState] = useState<UploadState>({ status: 'idle' });

  async function upload(file: File) {
    setState({ status: 'uploading', progress: 0 });
    const form = new FormData();
    form.append('file', file);

    try {
      const res = await fetch('/api/upload', { method: 'POST', body: form });
      const json = await res.json();
      if (!res.ok || json.error) {
        setState({ status: 'error', message: json.error ?? `HTTP ${res.status}` });
        return;
      }
      setState({ status: 'done', data: json });
    } catch (e) {
      setState({ status: 'error', message: (e as Error).message });
    }
  }

  function reset() { setState({ status: 'idle' }); }

  return { state, upload, reset };
}
