import { useState, useMemo } from 'react';
import type { TimestampChunks } from '../../types/report';

interface Props {
  data: TimestampChunks;
}

type SortDir = 'asc' | 'desc';

export default function DataTable({ data }: Props) {
  const { timestamps, chunks, thresholds } = data;
  const [selectedTs, setSelectedTs] = useState<string>(timestamps[0] ?? '');
  const [search, setSearch] = useState('');
  const [topN, setTopN] = useState<number | 'all'>(25);
  const [sortCol, setSortCol] = useState<number | null>(null);
  const [sortDir, setSortDir] = useState<SortDir>('desc');

  const snapshot = chunks[selectedTs];
  const headers = snapshot?.headers ?? [];
  const cmdIdx = headers.findIndex(h => /command|cmd/i.test(h));

  const filteredRows = useMemo(() => {
    if (!snapshot) return [];
    let rows = snapshot.rows;
    if (search && cmdIdx >= 0) {
      const q = search.toLowerCase();
      rows = rows.filter(r => String(r[cmdIdx] ?? '').toLowerCase().includes(q));
    }
    if (sortCol !== null) {
      rows = [...rows].sort((a, b) => {
        const va = a[sortCol], vb = b[sortCol];
        const na = parseFloat(String(va)), nb = parseFloat(String(vb));
        const cmp = !isNaN(na) && !isNaN(nb) ? na - nb : String(va).localeCompare(String(vb));
        return sortDir === 'asc' ? cmp : -cmp;
      });
    }
    return topN === 'all' ? rows : rows.slice(0, topN);
  }, [snapshot, search, sortCol, sortDir, topN, cmdIdx]);

  function handleSort(idx: number) {
    if (sortCol === idx) setSortDir(d => d === 'asc' ? 'desc' : 'asc');
    else { setSortCol(idx); setSortDir('desc'); }
  }

  function cellClass(header: string, value: string | number) {
    if (!thresholds) return '';
    const t = thresholds[header];
    if (!t) return '';
    const n = parseFloat(String(value));
    if (isNaN(n)) return '';
    if (n >= t.crit) return 'bg-red-900/50 text-red-200';
    if (n >= t.warn) return 'bg-yellow-900/50 text-yellow-200';
    return '';
  }

  const controlStyle = {
    background: 'var(--bg-elevated)',
    border: '1px solid var(--border)',
    color: 'var(--text-primary)',
  };

  return (
    <div>
      {/* Controls */}
      <div className="flex flex-wrap gap-3 mb-4">
        <div className="flex flex-col gap-1">
          <label className="text-xs" style={{ color: 'var(--text-secondary)' }}>Timestamp</label>
          <select
            value={selectedTs}
            onChange={e => setSelectedTs(e.target.value)}
            className="text-sm px-3 py-1.5 rounded-md w-56 focus:outline-none"
            style={{ ...controlStyle, outlineColor: 'var(--accent)' }}
          >
            {timestamps.map(ts => (
              <option key={ts} value={ts}>{ts}</option>
            ))}
          </select>
        </div>
        {cmdIdx >= 0 && (
          <div className="flex flex-col gap-1">
            <label className="text-xs" style={{ color: 'var(--text-secondary)' }}>Filter command</label>
            <input
              type="text"
              placeholder="regex / name..."
              value={search}
              onChange={e => setSearch(e.target.value)}
              className="text-sm px-3 py-1.5 rounded-md w-48 focus:outline-none"
              style={controlStyle}
            />
          </div>
        )}
        <div className="flex flex-col gap-1">
          <label className="text-xs" style={{ color: 'var(--text-secondary)' }}>Show</label>
          <select
            value={topN === 'all' ? 'all' : String(topN)}
            onChange={e => setTopN(e.target.value === 'all' ? 'all' : parseInt(e.target.value))}
            className="text-sm px-3 py-1.5 rounded-md focus:outline-none"
            style={controlStyle}
          >
            {[10, 25, 50, 100].map(n => <option key={n} value={n}>Top {n}</option>)}
            <option value="all">All</option>
          </select>
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto rounded-lg" style={{ border: '1px solid var(--border)' }}>
        <div className="max-h-[560px] overflow-y-auto">
          <table className="w-full text-sm text-left border-collapse">
            <thead className="sticky top-0 z-10" style={{ background: 'var(--bg-muted)' }}>
              <tr>
                {headers.map((h, i) => (
                  <th
                    key={i}
                    onClick={() => handleSort(i)}
                    className="px-3 py-2.5 text-xs font-semibold uppercase tracking-wider cursor-pointer select-none whitespace-nowrap"
                    style={{
                      color: sortCol === i ? 'var(--accent)' : 'var(--text-secondary)',
                      borderBottom: '1px solid var(--border)',
                    }}
                  >
                    {h}
                    {sortCol === i && <span className="ml-1">{sortDir === 'asc' ? '↑' : '↓'}</span>}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {filteredRows.map((row, ri) => (
                <tr
                  key={ri}
                  className="transition-colors"
                  style={{ borderBottom: '1px solid var(--border-subtle)' }}
                  onMouseEnter={e => (e.currentTarget as HTMLTableRowElement).style.background = 'var(--bg-hover)'}
                  onMouseLeave={e => (e.currentTarget as HTMLTableRowElement).style.background = ''}
                >
                  {row.map((cell, ci) => (
                    <td key={ci} className={`px-3 py-1.5 mono text-xs whitespace-nowrap ${cellClass(headers[ci], cell)}`}>
                      {String(cell)}
                    </td>
                  ))}
                </tr>
              ))}
              {filteredRows.length === 0 && (
                <tr>
                  <td colSpan={headers.length} className="px-3 py-8 text-center" style={{ color: 'var(--text-muted)' }}>
                    No data
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
