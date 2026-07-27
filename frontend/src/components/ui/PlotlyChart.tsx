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
  const isDark = (document.documentElement.getAttribute('data-theme') ?? 'dark') !== 'light';

  const chartBg    = getCSSVar('--chart-bg')      || (isDark ? '#1f1f1f' : '#fafafa');
  const border     = getCSSVar('--border')         || (isDark ? '#444444' : '#d3d3d4');
  const textColor  = getCSSVar('--text-primary')   || (isDark ? '#f5f5f5' : '#383a42');
  const accent     = getCSSVar('--accent')         || '#79b8ff';
  const bgMuted    = getCSSVar('--bg-muted')       || (isDark ? '#333333' : '#e5e5e6');
  const bgSurface  = getCSSVar('--bg-surface')     || (isDark ? '#242424' : '#ffffff');

  const fl      = (figure.layout ?? {}) as Record<string, unknown>;
  const fxaxis  = (fl.xaxis  ?? {}) as Record<string, unknown>;
  const fyaxis  = (fl.yaxis  ?? {}) as Record<string, unknown>;

  return {
    ...fl,
    template:       isDark ? 'plotly_dark' : 'plotly_white',
    paper_bgcolor:  chartBg,
    plot_bgcolor:   chartBg,
    font: { color: textColor, family: 'Inter, system-ui, sans-serif', size: 12 },
    margin: { l: 50, r: 20, t: 40, b: 50 },
    xaxis: {
      gridcolor: border, linecolor: border, zerolinecolor: border,
      ...fxaxis,
      rangeselector: {
        bgcolor: bgMuted, activecolor: accent,
        bordercolor: border, borderwidth: 1,
        font: { color: textColor, size: 11 },
        ...((fxaxis.rangeselector as object) ?? {}),
      } as object,
    },
    yaxis: {
      gridcolor: border, linecolor: border, zerolinecolor: border,
      ...fyaxis,
    },
    legend: {
      bgcolor: bgSurface, bordercolor: border, borderwidth: 1,
      ...((fl.legend as object) ?? {}),
    },
  } as unknown as Plotly.Layout;
}

const CONFIG: Partial<Plotly.Config> = {
  displayModeBar: 'hover',
  displaylogo: false,
  modeBarButtonsToRemove: ['sendDataToCloud', 'lasso2d', 'select2d'],
  responsive: true,
};

export default function PlotlyChart({ figure, className }: Props) {
  const ref = useRef<HTMLDivElement>(null);

  // Re-render when figure changes OR when theme changes (listen for data-theme mutations)
  useEffect(() => {
    if (!ref.current) return;
    Plotly.newPlot(ref.current, figure.data as Plotly.Data[], buildLayout(figure), CONFIG);

    const resizeObs = new ResizeObserver(() => {
      if (ref.current) Plotly.Plots.resize(ref.current);
    });
    resizeObs.observe(ref.current);

    // Redraw when theme toggle changes data-theme on <html>
    const themeObs = new MutationObserver(() => {
      if (ref.current)
        Plotly.react(ref.current, figure.data as Plotly.Data[], buildLayout(figure), CONFIG);
    });
    themeObs.observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });

    return () => {
      resizeObs.disconnect();
      themeObs.disconnect();
      if (ref.current) Plotly.purge(ref.current);
    };
  }, [figure]);

  return <div ref={ref} className={className ?? 'w-full'} />;
}
