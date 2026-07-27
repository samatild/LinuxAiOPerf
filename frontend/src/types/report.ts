export interface PlotlyFigure {
  data: object[];
  layout: object;
}

export interface TimestampChunks {
  timestamps: string[];
  chunks: Record<string, { headers: string[]; rows: (string | number)[][] }>;
  thresholds?: Record<string, { warn: number; crit: number }>;
}

export interface ReportMetadata {
  hostname?: string;
  os?: string;
  kernel?: string;
  cpu_model?: string;
  collection_date?: string;
}

export interface SysConfigData {
  information?: { runtime_info: string; os_release: string };
  hardware?: { lshw: string; dmidecode: string };
  storage?: { lsscsi?: string; lsblk?: string; df?: string; ls_dev_mapper?: string };
  lvm?: {
    topology?: {
      pvs: { name: string; vg: string; size: string; free: string }[];
      vgs: { name: string; size: string; free: string }[];
      lvs: { name: string; vg: string; size: string; type: string }[];
    };
    pvs_raw?: string;
    vgs_raw?: string;
    lvs_raw?: string;
    pvdisplay_raw?: string;
    vgdisplay_raw?: string;
    lvdisplay_raw?: string;
  };
  cpu_info?: string;
  memory_info?: string;
  kernel_params?: string;
  kernel_modules?: string;
  security?: string;
}

export interface PerformanceData {
  cpu?: { figures: PlotlyFigure[] };
  memory?: { figures: PlotlyFigure[] };
  disk?: {
    per_device?: { figures: PlotlyFigure[] };
    per_metric?: { figures: PlotlyFigure[] };
    highres?: { figures: PlotlyFigure[] };
  };
  network?: { figures: PlotlyFigure[] };
}

export interface ProcessActivityData {
  cpu?: { figures: PlotlyFigure[] };
  io?: { figures: PlotlyFigure[] };
  memory?: { figures: PlotlyFigure[] };
}

export interface ProcessDetailsData {
  pidstat_cpu?: TimestampChunks;
  pidstat_io?: TimestampChunks;
  pidstat_memory?: TimestampChunks;
  top?: TimestampChunks;
  iotop?: TimestampChunks;
}

export interface ReportData {
  report_id: string;
  metadata: ReportMetadata;
  sysconfig?: SysConfigData;
  performance?: PerformanceData;
  process_activity?: ProcessActivityData;
  process_details?: ProcessDetailsData;
  error?: string;
}
