import PlotlyChart from './PlotlyChart';
import type { PlotlyFigure } from '../../types/report';

interface Props {
  figures?: PlotlyFigure[];
  emptyMessage?: string;
}

export default function FigureGrid({ figures, emptyMessage = 'No data available' }: Props) {
  if (!figures?.length) {
    return <p className="text-slate-500 text-center py-12">{emptyMessage}</p>;
  }
  return (
    <div className="space-y-4">
      {figures.map((fig, i) => (
        <div key={i} className="rounded-xl p-3" style={{ background: 'var(--bg-elevated)', border: '1px solid var(--border)' }}>
          <PlotlyChart figure={fig} />
        </div>
      ))}
    </div>
  );
}
