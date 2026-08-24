import type { PerformanceData, PlotlyFigure, ProcessActivityData } from '../../types/report';

export interface AuditFigure {
  section: string;
  title: string;
  figure: PlotlyFigure;
}

const CPU_TITLES = ['All CPU Usage Data', '%usr - CPU Usage Data', '%sys - CPU Usage Data', '%iowait - CPU Usage Data', '%idle - CPU Usage Data'];
const DISK_TITLES = ['Disk r/s - All Devices', 'Disk w/s - All Devices', 'Disk rkB/s - All Devices', 'Disk wkB/s - All Devices', 'Disk aqu-sz - All Devices', 'Disk r_await - All Devices', 'Disk w_await - All Devices'];

function titleOf(figure: PlotlyFigure) {
  const title = (figure.layout as { title?: string | { text?: string } }).title;
  return typeof title === 'string' ? title : title?.text ?? '';
}

function selectTitles(section: string, figures: PlotlyFigure[] | undefined, wanted: string[]): AuditFigure[] {
  return (figures ?? []).filter(figure => wanted.includes(titleOf(figure))).map(figure => ({ section, title: titleOf(figure), figure }));
}

/** Explicit audit selection; raw output and process details never enter this list. */
export function selectAuditFigures(performance?: PerformanceData, processActivity?: ProcessActivityData): AuditFigure[] {
  const disk = performance?.disk?.per_metric?.figures ?? performance?.disk?.per_device?.figures;
  const processFigures = [
    ...(processActivity?.cpu?.figures ?? []),
    ...(processActivity?.io?.figures ?? []),
    ...(processActivity?.memory?.figures ?? []),
  ];
  return [
    ...selectTitles('CPU', performance?.cpu?.figures, CPU_TITLES),
    ...selectTitles('Memory', performance?.memory?.figures, (performance?.memory?.figures ?? []).map(titleOf)),
    ...selectTitles('Disk', disk, DISK_TITLES),
    ...selectTitles('Network', performance?.network?.figures, (performance?.network?.figures ?? []).map(titleOf)),
    ...processFigures.map(figure => ({ section: 'Process activity', title: titleOf(figure), figure })),
  ];
}
