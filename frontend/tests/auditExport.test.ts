import { describe, expect, it } from 'vitest';
import { selectAuditFigures } from '../src/components/report/auditExport';

const figure = { data: [], layout: {} };

describe('selectAuditFigures', () => {
  it('chooses one representative chart for each performance domain', () => {
    const selected = selectAuditFigures({
      cpu: { figures: [figure] }, memory: { figures: [figure] },
      disk: { per_metric: { figures: [figure] } }, network: { figures: [figure] },
    });
    expect(selected.map(item => item.section)).toEqual(['CPU', 'Memory', 'Disk', 'Network']);
  });

  it('does not export any chart when performance data is absent', () => {
    expect(selectAuditFigures()).toEqual([]);
  });
});
