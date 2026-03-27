interface Tab {
  id: string;
  label: string;
  available?: boolean;
}

interface Props {
  tabs: Tab[];
  active: string;
  onChange: (id: string) => void;
}

export default function SubTabBar({ tabs, active, onChange }: Props) {
  return (
    <div className="flex flex-wrap gap-1 mb-5 pb-3" style={{ borderBottom: '1px solid var(--border)' }}>
      {tabs.map(({ id, label, available = true }) => (
        <button
          key={id}
          onClick={() => available && onChange(id)}
          disabled={!available}
          className="px-4 py-1.5 rounded-md text-sm font-medium transition-all duration-150"
          style={
            active === id
              ? { background: 'var(--accent)', color: 'var(--accent-fg)' }
              : available
              ? { background: 'transparent', color: 'var(--text-secondary)' }
              : { background: 'transparent', color: 'var(--text-dim)', cursor: 'not-allowed' }
          }
          onMouseEnter={e => {
            if (active !== id && available) {
              (e.currentTarget as HTMLButtonElement).style.background = 'var(--bg-elevated)';
              (e.currentTarget as HTMLButtonElement).style.color = 'var(--text-primary)';
            }
          }}
          onMouseLeave={e => {
            if (active !== id && available) {
              (e.currentTarget as HTMLButtonElement).style.background = 'transparent';
              (e.currentTarget as HTMLButtonElement).style.color = 'var(--text-secondary)';
            }
          }}
        >
          {label}
        </button>
      ))}
    </div>
  );
}
