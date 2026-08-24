import type { PerformanceData, PlotlyFigure } from '../../types/report';

export interface AuditFigure {
  section: string;
  figure: PlotlyFigure;
}

function first(section: string, figures?: PlotlyFigure[]): AuditFigure[] {
  const figure = figures?.[0];
  return figure ? [{ section, figure }] : [];
}

/** A deliberately small, representative set. Never exports raw/process details. */
export function selectAuditFigures(performance?: PerformanceData): AuditFigure[] {
  if (!performance) return [];
  return [
    ...first('CPU', performance.cpu?.figures),
    ...first('Memory', performance.memory?.figures),
    ...first('Disk', performance.disk?.per_metric?.figures ?? performance.disk?.per_device?.figures),
    ...first('Network', performance.network?.figures),
  ];
}
