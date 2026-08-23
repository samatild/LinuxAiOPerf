import { useState } from 'react';
import type { ReportData } from '../types/report';
import { uploadMetrics } from '../components/upload/uploadMetrics';

export interface LogLine {
  ts: number;
  message: string;
}

export interface TransferProgress {
  percent: number;
  loaded: number;
  total: number;
  bytesPerSecond: number;
  etaSeconds: number | null;
}

export interface AnalysisProgress {
  percent: number;
  stage: string;
}

type UploadState =
  | { status: 'idle' }
  | { status: 'uploading'; upload: TransferProgress; analysis: AnalysisProgress; log: LogLine[] }
  | { status: 'done'; data: ReportData }
  | { status: 'error'; message: string };

const initialTransfer: TransferProgress = {
  percent: 0, loaded: 0, total: 0, bytesPerSecond: 0, etaSeconds: null,
};

export function useUpload() {
  const [state, setState] = useState<UploadState>({ status: 'idle' });

  function updateAnalysis(percent: number | undefined, stage: string | undefined, log: LogLine[]) {
    setState((previous) => {
      if (previous.status !== 'uploading') return previous;
      const nextLog = stage && log.at(-1)?.message !== stage
        ? [...log, { ts: Date.now(), message: stage }]
        : log;
      return {
        ...previous,
        analysis: {
          percent: percent ?? previous.analysis.percent,
          stage: stage ?? previous.analysis.stage,
        },
        log: nextLog,
      };
    });
  }

  async function waitForLocalJob(jobId: string, log: LogLine[]) {
    while (true) {
      await new Promise((resolve) => window.setTimeout(resolve, 1000));
      const response = await fetch(`/api/job?job_id=${encodeURIComponent(jobId)}`);
      const job = await response.json();
      if (!response.ok || job.error) {
        setState({ status: 'error', message: job.error ?? `HTTP ${response.status}` });
        return;
      }
      if (job.stage && log.at(-1)?.message !== job.stage) {
        log = [...log, { ts: Date.now(), message: job.stage }];
      }
      updateAnalysis(job.percent, job.stage, log);
      if (job.status === 'done') {
        setState({ status: 'done', data: job.result });
        return;
      }
    }
  }

  function upload(file: File) {
    let log: LogLine[] = [];
    let responseOffset = 0;
    let responseBuffer = '';
    let finalResult: ReportData | null = null;
    const startedAt = performance.now();

    setState({
      status: 'uploading',
      upload: { ...initialTransfer, total: file.size },
      analysis: { percent: 0, stage: 'Waiting for upload to finish…' },
      log,
    });

    const xhr = new XMLHttpRequest();
    xhr.open('POST', '/api/upload');

    xhr.upload.onprogress = (event) => {
      if (!event.lengthComputable) return;
      const metrics = uploadMetrics(event.loaded, event.total, startedAt, performance.now());
      setState((previous) => previous.status === 'uploading' ? {
        ...previous,
        upload: { loaded: event.loaded, total: event.total, ...metrics },
      } : previous);
    };

    const consumeLines = (flush = false) => {
      responseBuffer += xhr.responseText.slice(responseOffset);
      responseOffset = xhr.responseText.length;
      const lines = responseBuffer.split('\n');
      responseBuffer = flush ? '' : (lines.pop() ?? '');
      for (const line of lines) {
        if (!line.trim()) continue;
        try {
          const data = JSON.parse(line);
          if (data.error) {
            setState({ status: 'error', message: data.error });
            return;
          }
          if (data.result) {
            finalResult = data.result;
            return;
          }
          if (data.log) log = [...log, { ts: Date.now(), message: data.log }];
          updateAnalysis(data.percent, data.stage, log);
        } catch {
          // A chunk can end in the middle of one NDJSON object; keep parsing.
        }
      }
    };

    xhr.onprogress = () => consumeLines();
    xhr.onerror = () => setState({ status: 'error', message: 'Network error while uploading archive' });
    xhr.onload = async () => {
      if (xhr.status === 202) {
        try {
          const job = JSON.parse(xhr.responseText);
          setState((previous) => previous.status === 'uploading' ? {
            ...previous,
            upload: { ...previous.upload, percent: 100, loaded: file.size },
            analysis: { percent: 0, stage: 'Archive uploaded, starting analysis…' },
          } : previous);
          await waitForLocalJob(job.job_id, log);
        } catch {
          setState({ status: 'error', message: 'Invalid asynchronous job response' });
        }
        return;
      }
      if (xhr.status < 200 || xhr.status >= 300) {
        setState({ status: 'error', message: `HTTP ${xhr.status}` });
        return;
      }
      consumeLines(true);
      if (finalResult) setState({ status: 'done', data: finalResult });
    };

    const form = new FormData();
    form.append('file', file);
    xhr.send(form);
  }

  function reset() {
    setState({ status: 'idle' });
  }

  return { state, upload, reset };
}
