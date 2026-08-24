export function filterRawText(content: string, query: string): string {
  const needle = query.trim().toLowerCase();
  if (!needle) return content;
  return content
    .split('\n')
    .filter(line => line.toLowerCase().includes(needle))
    .join('\n');
}
