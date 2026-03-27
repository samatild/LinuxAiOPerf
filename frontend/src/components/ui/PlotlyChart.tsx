import { useEffect, useRef } from 'react';
import Plotly from 'plotly.js-dist-min';
import type { PlotlyFigure } from '../../types/report';

interface Props {
  figure: PlotlyFigure;
  className?: string;
}

function getCSSVar(name: string): string {
  return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
}

function buildLayout(figure: PlotlyFigure): Plotly.Layout {
  const fl = (figure.layout ?? {}) as Record<string, unknown>;
  const fxaxis = (fl.xaxis ?? {}) as Record<string, unknown>;
  const fyaxis = (fl.yaxis ?? {}) as Record<string, unknown>;

  const chartBg = getCSSVar('--chart-bg') || '#1a1d2e';
  const borderColor = getCSSVar('--border') || '#2d3149';
  const textColor = getCSSVar('--text-primary') || '#f0eeff';
  const accentColor = getCSSVar('--accent') || '#863bff';
  const bgMuted = getCSSVar('--bg-muted') || '#1e2235';
  const bgElevated = getCSSVar('--bg-elevated') || '#1a1d2e';

  return {
    ...fl,
    template: 'plotly_dark',
    paper_bgcolor: chartBg,
    plot_bgcolor: chartBg,
    font: { color: textColor, family: 'Inter, system-ui, sans-serif', size: 12 },
    margin: { l: 50, r: 20, t: 40, b: 50 },
    xaxis: {
      gridcolor: borderColor,
      linecolor: borderColor,
      zerolinecolor: borderColor,
      ...fxaxis,
      rangeselector: {
        bgcolor: bgMuted,
        activecolor: accentColor,
        bordercolor: borderColor,
        borderwidth: 1,
        font: { color: textColor, size: 11 },
        ...((fxaxis.rangeselector as object) ?? {}),
      } as object,
    },
    yaxis: {
      gridcolor: borderColor,
      linecolor: borderColor,
      zerolinecolor: borderColor,
      ...fyaxis,
    },
    legend: {
      bgcolor: bgElevated + 'dd',
      bordercolor: borderColor,
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
    const theme = document.documentElement.getAttribute('data-theme') ?? 'dark';
    const layout = buildLayout(figure);

    if (theme === 'light') {
      (layout as unknown as Record<string, unknown>).template = 'plotly_white';
      (layout as unknown as Record<string, unknown>).paper_bgcolor = getCSSVar('--chart-bg') || '#ffffff';
      (layout as unknown as Record<string, unknown>).plot_bgcolor = getCSSVar('--chart-bg') || '#ffffff';
    }

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
