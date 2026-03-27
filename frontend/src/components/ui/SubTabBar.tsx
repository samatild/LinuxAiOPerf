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
    <div className="flex flex-wrap gap-1 mb-5 border-b border-[#2d3149] pb-3">
      {tabs.map(({ id, label, available = true }) => (
        <button
          key={id}
          onClick={() => available && onChange(id)}
          disabled={!available}
          className={`px-4 py-1.5 rounded-md text-sm font-medium transition-all duration-150 ${
            active === id
              ? 'bg-indigo-600 text-white shadow-sm shadow-indigo-900'
              : available
              ? 'text-slate-400 hover:text-slate-200 hover:bg-[#21263a]'
              : 'text-slate-600 cursor-not-allowed'
          }`}
        >
          {label}
        </button>
      ))}
    </div>
  );
}
