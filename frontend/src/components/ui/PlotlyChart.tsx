import { useEffect, useRef } from 'react';
import Plotly from 'plotly.js-dist-min';
import type { PlotlyFigure } from '../../types/report';

interface Props {
  figure: PlotlyFigure;
  className?: string;
}

// Minimal layout overrides on top of the figure layout.
// We use the 'plotly_dark' template for proper dark theming
// and only override things the template doesn't cover.
function buildLayout(figure: PlotlyFigure): Plotly.Layout {
  const fl = (figure.layout ?? {}) as Record<string, unknown>;
  const fxaxis = (fl.xaxis ?? {}) as Record<string, unknown>;
  const fyaxis = (fl.yaxis ?? {}) as Record<string, unknown>;

  return {
    ...fl,
    template: 'plotly_dark',
    paper_bgcolor: '#1a1d27',
    plot_bgcolor: '#1a1d27',
    font: { color: '#e2e8f0', family: 'Inter, system-ui, sans-serif', size: 12 },
    margin: { l: 50, r: 20, t: 40, b: 50 },
    // Deep-merge axes so we don't lose rangeselector colors from figure layout
    xaxis: {
      gridcolor: '#2d3149',
      linecolor: '#2d3149',
      zerolinecolor: '#2d3149',
      ...fxaxis,
      rangeselector: {
        bgcolor: '#21263a',
        activecolor: '#6366f1',
        bordercolor: '#2d3149',
        borderwidth: 1,
        font: { color: '#e2e8f0', size: 11 },
        ...((fxaxis.rangeselector as object) ?? {}),
      } as object,
    },
    yaxis: {
      gridcolor: '#2d3149',
      linecolor: '#2d3149',
      zerolinecolor: '#2d3149',
      ...fyaxis,
    },
    legend: {
      bgcolor: 'rgba(33,38,58,0.85)',
      bordercolor: '#2d3149',
      borderwidth: 1,
      ...((fl.legend as object) ?? {}),
    },
  } as unknown as Plotly.Layout;
}

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
    const layout = buildLayout(figure);
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
