export interface UploadMetrics {
  percent: number;
  bytesPerSecond: number;
  etaSeconds: number | null;
}

export function uploadMetrics(
  loaded: number,
  total: number,
  startedAt: number,
  now: number,
): UploadMetrics {
  const percent = total > 0 ? Math.min(100, (loaded / total) * 100) : 0;
  const elapsedSeconds = Math.max(0, (now - startedAt) / 1000);
  const bytesPerSecond = elapsedSeconds > 0 ? loaded / elapsedSeconds : 0;
  const etaSeconds = bytesPerSecond > 0 ? Math.max(0, (total - loaded) / bytesPerSecond) : null;
  return { percent, bytesPerSecond, etaSeconds };
}
