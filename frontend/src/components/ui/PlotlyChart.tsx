import { useEffect, useRef } from 'react';
import Plotly from 'plotly.js-dist-min';
import type { PlotlyFigure } from '../../types/report';

interface Props {
  figure: PlotlyFigure;
  className?: string;
}

const DARK_LAYOUT: Partial<Plotly.Layout> = {
  paper_bgcolor: '#1a1d27',
  plot_bgcolor: '#1a1d27',
  font: { color: '#e2e8f0', family: 'Inter, system-ui, sans-serif', size: 12 },
  xaxis: { gridcolor: '#2d3149', linecolor: '#2d3149', zerolinecolor: '#2d3149' },
  yaxis: { gridcolor: '#2d3149', linecolor: '#2d3149', zerolinecolor: '#2d3149' },
  legend: { bgcolor: '#21263a', bordercolor: '#2d3149', borderwidth: 1 },
  margin: { l: 50, r: 20, t: 40, b: 50 },
};

const CONFIG: Partial<Plotly.Config> = {
  displayModeBar: true,
  displaylogo: false,
  modeBarButtonsToRemove: ['sendDataToCloud', 'lasso2d', 'select2d'],
  responsive: true,
};

export default function PlotlyChart({ figure, className }: Props) {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!ref.current) return;
    const layout = { ...DARK_LAYOUT, ...figure.layout } as Plotly.Layout;
    Plotly.newPlot(ref.current, figure.data as Plotly.Data[], layout, CONFIG);

    const observer = new ResizeObserver(() => {
      if (ref.current) Plotly.Plots.resize(ref.current);
    });
    observer.observe(ref.current);

    return () => {
      observer.disconnect();
      if (ref.current) Plotly.purge(ref.current);
    };
  }, [figure]);

  return <div ref={ref} className={className ?? 'w-full'} />;
}
