export function adjacentTimestamp(
  timestamps: readonly string[],
  selected: string,
  direction: -1 | 1,
): string {
  const index = timestamps.indexOf(selected);
  if (index < 0) return timestamps[0] ?? '';
  return timestamps[Math.max(0, Math.min(timestamps.length - 1, index + direction))] ?? '';
}
