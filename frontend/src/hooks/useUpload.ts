import { useState } from 'react';
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

// The full response body is a single request that streams newline-delimited
// JSON (NDJSON) progress lines, ending with a final line containing the full
// report (or an error). This avoids depending on server-side state surviving
// across two separate HTTP requests (upload + poll), which isn't guaranteed
// on serverless platforms like Vercel — see issue #88.
export function useUpload() {
  const [state, setState] = useState<UploadState>({ status: 'idle' });

  async function waitForLocalJob(jobId: string, log: LogLine[]) {
    while (true) {
      await new Promise((resolve) => window.setTimeout(resolve, 1000));
      const res = await fetch(`/api/job?job_id=${encodeURIComponent(jobId)}`);
      const job = await res.json();
      if (!res.ok || job.error) {
        setState({ status: 'error', message: job.error ?? `HTTP ${res.status}` });
        return;
      }
      if (job.stage && log.at(-1)?.message !== job.stage) {
        log = [...log, { ts: Date.now(), message: job.stage }];
      }
      setState({
        status: 'uploading',
        percent: job.percent ?? 0,
        stage: job.stage ?? 'Processing archive…',
        log,
      });
      if (job.status === 'done') {
        setState({ status: 'done', data: job.result });
        return;
      }
    }
  }

  async function upload(file: File) {
    setState({ status: 'uploading', percent: 0, stage: 'Uploading archive…', log: [] });
    const form = new FormData();
    form.append('file', file);

    let log: LogLine[] = [];

    try {
      const res = await fetch('/api/upload', { method: 'POST', body: form });
      if (!res.ok || !res.body) {
        let message = `HTTP ${res.status}`;
        try {
          const json = await res.json();
          message = json.error ?? message;
        } catch {
          // response wasn't JSON (e.g. platform error page) — keep the HTTP status message
        }
        setState({ status: 'error', message });
        return;
      }

      if (res.status === 202) {
        const job = await res.json();
        await waitForLocalJob(job.job_id, log);
        return;
      }

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });

        let newlineIdx: number;
        while ((newlineIdx = buffer.indexOf('\n')) !== -1) {
          const line = buffer.slice(0, newlineIdx).trim();
          buffer = buffer.slice(newlineIdx + 1);
          if (!line) continue;

          let json: any;
          try {
            json = JSON.parse(line);
          } catch {
            continue; // ignore malformed/partial line, shouldn't normally happen
          }

          if (json.error) {
            setState({ status: 'error', message: json.error });
            return;
          }
          if (json.result) {
            setState({ status: 'done', data: json.result });
            return;
          }
          if (json.log) {
            log = [...log, { ts: Date.now(), message: json.log }];
          }
          setState((prev) => ({
            status: 'uploading',
            percent: json.percent ?? (prev.status === 'uploading' ? prev.percent : 0),
            stage: json.stage ?? (prev.status === 'uploading' ? prev.stage : ''),
            log,
          }));
        }
      }
    } catch (e) {
      setState({ status: 'error', message: (e as Error).message });
    }
  }

  function reset() {
    setState({ status: 'idle' });
  }

  return { state, upload, reset };
}
