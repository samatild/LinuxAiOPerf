import type { ReportData } from '../../../types/report';

export interface ReportSummary {
  figures: number;
  snapshots: number;
  volumeGroups: number;
  logicalVolumes: number;
}

export function summarizeReport(data: ReportData): ReportSummary {
  const figures = [
    data.performance?.cpu,
    data.performance?.memory,
    data.performance?.disk?.per_device,
    data.performance?.disk?.per_metric,
    data.performance?.disk?.highres,
    data.performance?.network,
    data.process_activity?.cpu,
    data.process_activity?.io,
    data.process_activity?.memory,
  ].reduce((total, section) => total + (section?.figures.length ?? 0), 0);

  const snapshots = Object.values(data.process_details ?? {})
    .reduce((total, section) => total + (section?.timestamps.length ?? 0), 0);
  const topology = data.sysconfig?.lvm?.topology;

  return {
    figures,
    snapshots,
    volumeGroups: topology?.vgs.length ?? 0,
    logicalVolumes: topology?.lvs.length ?? 0,
  };
}
