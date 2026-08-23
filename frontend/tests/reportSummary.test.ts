import { describe, expect, it } from 'vitest';
import { summarizeReport } from '../src/components/report/overview/reportSummary';

it('summarizes available figures, process snapshots, and LVM volumes', () => {
  expect(summarizeReport({
    performance: { cpu: { figures: [{}, {}] }, disk: { per_device: { figures: [{}] } } },
    process_details: { pidstat_cpu: { timestamps: ['a', 'b'], header: [] } },
    sysconfig: { lvm: { topology: { pvs: [], vgs: [{}], lvs: [{}, {}] } } },
  } as never)).toEqual({ figures: 3, snapshots: 2, volumeGroups: 1, logicalVolumes: 2 });
});
