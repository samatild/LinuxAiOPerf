import { useRef, useState } from 'react';
import type { ReportData } from '../types/report';

export interface LogLine {
  ts: number;
  message: string;
}

type UploadState =
  | { status: 'idle' }
  | { status: 'uploading'; percent: number; stage: string; log: LogLine[] }
  | { status: 'done'; data: ReportData }
  | { status: 'error'; message: string };

const POLL_INTERVAL_MS = 800;

export function useUpload() {
  const [state, setState] = useState<UploadState>({ status: 'idle' });
  const pollTimer = useRef<number | null>(null);

  function stopPolling() {
    if (pollTimer.current !== null) {
      window.clearTimeout(pollTimer.current);
      pollTimer.current = null;
    }
  }

  function pollProgress(reportId: string) {
    pollTimer.current = window.setTimeout(async () => {
      try {
        const res = await fetch(`/api/progress?report_id=${encodeURIComponent(reportId)}`);
        const json = await res.json();
        if (!res.ok || json.error) {
          setState({ status: 'error', message: json.error ?? `HTTP ${res.status}` });
          return;
        }
        if (json.status === 'done') {
          setState({ status: 'done', data: json.result });
          return;
        }
        if (json.status === 'error') {
          setState({ status: 'error', message: json.error ?? 'Processing failed' });
          return;
        }
        setState({
          status: 'uploading',
          percent: json.percent ?? 0,
          stage: json.stage ?? '',
          log: json.log ?? [],
        });
        pollProgress(reportId);
      } catch (e) {
        setState({ status: 'error', message: (e as Error).message });
      }
    }, POLL_INTERVAL_MS);
  }

  async function upload(file: File) {
    stopPolling();
    setState({ status: 'uploading', percent: 0, stage: 'Uploading archive…', log: [] });
    const form = new FormData();
    form.append('file', file);

    try {
      const res = await fetch('/api/upload', { method: 'POST', body: form });
      const json = await res.json();
      if (!res.ok || json.error) {
        setState({ status: 'error', message: json.error ?? `HTTP ${res.status}` });
        return;
      }
      pollProgress(json.report_id);
    } catch (e) {
      setState({ status: 'error', message: (e as Error).message });
    }
  }

  function reset() {
    stopPolling();
    setState({ status: 'idle' });
  }

  return { state, upload, reset };
}
