import type { SysConfigData } from '../../../types/report';

type Topology = NonNullable<NonNullable<SysConfigData['lvm']>['topology']>;

interface Props { topology: Topology; }

// ── Small card components ────────────────────────────────────────────────────

function PvCard({ name, size, free }: { name: string; size: string; free: string }) {
  return (
    <div className="rounded-lg px-3 py-2 text-xs" style={{
      background: 'rgba(248, 81, 73, 0.12)',
      border: '1px solid rgba(248, 81, 73, 0.4)',
    }}>
      <div className="font-semibold truncate" style={{ color: '#f85149' }}>{name}</div>
      <div style={{ color: 'var(--text-secondary)' }}>Size: {size}</div>
      <div style={{ color: 'var(--text-muted)' }}>Free: {free}</div>
    </div>
  );
}

function VgCard({ name, size, free, pvCount, lvCount }: {
  name: string; size: string; free: string; pvCount: number; lvCount: number;
}) {
  return (
    <div className="rounded-lg px-4 py-3 text-xs text-center" style={{
      background: 'rgba(63, 185, 80, 0.12)',
      border: '1px solid rgba(63, 185, 80, 0.4)',
      minWidth: '120px',
    }}>
      <div className="font-bold text-sm mb-1" style={{ color: '#3fb950' }}>{name}</div>
      <div style={{ color: 'var(--text-secondary)' }}>Size: {size}</div>
      <div style={{ color: 'var(--text-muted)' }}>Free: {free}</div>
      <div className="mt-1.5 flex justify-center gap-2">
        <span className="px-1.5 py-0.5 rounded text-[10px]" style={{ background: 'rgba(248,81,73,0.15)', color: '#f85149' }}>
          {pvCount} PV{pvCount !== 1 ? 's' : ''}
        </span>
        <span className="px-1.5 py-0.5 rounded text-[10px]" style={{ background: 'rgba(88,166,255,0.15)', color: '#58a6ff' }}>
          {lvCount} LV{lvCount !== 1 ? 's' : ''}
        </span>
      </div>
    </div>
  );
}

function LvCard({ name, size, type }: { name: string; size: string; type: string }) {
  return (
    <div className="rounded-lg px-3 py-2 text-xs" style={{
      background: 'rgba(88, 166, 255, 0.12)',
      border: '1px solid rgba(88, 166, 255, 0.4)',
    }}>
      <div className="font-semibold truncate" style={{ color: '#58a6ff' }}>{name}</div>
      <div style={{ color: 'var(--text-secondary)' }}>Size: {size}</div>
      <div style={{ color: 'var(--text-muted)' }}>{type}</div>
    </div>
  );
}

function Arrow() {
  return (
    <div className="flex items-center self-center px-2" style={{ color: 'var(--text-muted)' }}>
      <svg width="32" height="16" viewBox="0 0 32 16" fill="none">
        <line x1="0" y1="8" x2="26" y2="8" stroke="currentColor" strokeWidth="1.5" />
        <polyline points="20,3 28,8 20,13" stroke="currentColor" strokeWidth="1.5" fill="none" strokeLinejoin="round" />
      </svg>
    </div>
  );
}

// ── Column header ────────────────────────────────────────────────────────────

function ColHeader({ label, color }: { label: string; color: string }) {
  return (
    <div className="text-[10px] font-bold uppercase tracking-widest mb-2 text-center" style={{ color }}>
      {label}
    </div>
  );
}

// ── Main diagram ─────────────────────────────────────────────────────────────

export default function LvmDiagram({ topology }: Props) {
  const { pvs, vgs, lvs } = topology;

  return (
    <div className="rounded-xl p-5 overflow-x-auto" style={{ background: 'var(--bg-elevated)', border: '1px solid var(--border)' }}>
      <div className="flex flex-col gap-4">
        {vgs.map(vg => {
          const vgPvs = pvs.filter(p => p.vg === vg.name);
          const vgLvs = lvs.filter(l => l.vg === vg.name);

          return (
            <div key={vg.name}>
              {/* VG section */}
              <div
                className="flex items-stretch gap-0 rounded-xl p-4"
                style={{ background: 'var(--bg-muted)', border: '1px solid var(--border)' }}
              >
                {/* PV column */}
                <div className="flex flex-col min-w-[160px]">
                  <ColHeader label="Physical Volumes" color="#f85149" />
                  <div className="flex flex-col gap-2 flex-1 justify-center">
                    {vgPvs.length > 0
                      ? vgPvs.map(pv => <PvCard key={pv.name} {...pv} />)
                      : <div className="text-xs italic" style={{ color: 'var(--text-muted)' }}>—</div>
                    }
                  </div>
                </div>

                <Arrow />

                {/* VG column */}
                <div className="flex flex-col items-center justify-center">
                  <ColHeader label="Volume Group" color="#3fb950" />
                  <VgCard
                    name={vg.name}
                    size={vg.size}
                    free={vg.free}
                    pvCount={vgPvs.length}
                    lvCount={vgLvs.length}
                  />
                </div>

                <Arrow />

                {/* LV column */}
                <div className="flex flex-col flex-1 min-w-[160px]">
                  <ColHeader label="Logical Volumes" color="#58a6ff" />
                  <div className="flex flex-col gap-2 justify-center">
                    {vgLvs.length > 0
                      ? vgLvs.map(lv => <LvCard key={lv.name} {...lv} />)
                      : <div className="text-xs italic" style={{ color: 'var(--text-muted)' }}>—</div>
                    }
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Legend */}
      <div className="flex gap-4 mt-4 text-[11px] justify-center" style={{ color: 'var(--text-muted)' }}>
        <span><span style={{ color: '#f85149' }}>■</span> Physical Volume (PV)</span>
        <span><span style={{ color: '#3fb950' }}>■</span> Volume Group (VG)</span>
        <span><span style={{ color: '#58a6ff' }}>■</span> Logical Volume (LV)</span>
      </div>
    </div>
  );
}
