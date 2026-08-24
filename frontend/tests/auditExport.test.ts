import { describe, expect, it } from 'vitest';
import { selectAuditFigures } from '../src/components/report/auditExport';

const named = (text: string) => ({ data: [], layout: { title: { text } } });

describe('selectAuditFigures', () => {
  it('selects the requested CPU and disk audit charts by metric title', () => {
    const selected = selectAuditFigures({
      cpu: { figures: ['All CPU Usage Data', '%usr - CPU Usage Data', '%sys - CPU Usage Data', '%iowait - CPU Usage Data', '%idle - CPU Usage Data', '%nice - CPU Usage Data'].map(named) },
      disk: { per_metric: { figures: ['Disk r/s - All Devices', 'Disk w/s - All Devices', 'Disk rkB/s - All Devices', 'Disk wkB/s - All Devices', 'Disk aqu-sz - All Devices', 'Disk r_await - All Devices', 'Disk w_await - All Devices', 'Disk %util - All Devices'].map(named) } },
    });
    expect(selected.map(item => item.section)).toEqual([
      'CPU', 'CPU', 'CPU', 'CPU', 'CPU',
      'Disk · IOPS', 'Disk · IOPS', 'Disk · Bandwidth', 'Disk · Bandwidth', 'Disk · Queue depth', 'Disk · Latency', 'Disk · Latency',
    ]);
  });

  it('places process activity before network at the end of the audit', () => {
    const selected = selectAuditFigures(
      { network: { figures: [named('Network rxpck/s')] } },
      { cpu: { figures: [named('Top 10 Processes — %usr')] } },
    );
    expect(selected.map(item => item.section)).toEqual(['Process activity', 'Network']);
  });

  it('includes all process activity figures and excludes raw process details', () => {
    const selected = selectAuditFigures(undefined, {
      cpu: { figures: [named('Top 10 Processes — %usr')] },
      io: { figures: [named('Top 10 Processes — kB_rd/s')] },
      memory: { figures: [named('Top 10 Processes — RSS (MB)')] },
    });
    expect(selected.map(item => item.section)).toEqual(['Process activity', 'Process activity', 'Process activity']);
  });
});
