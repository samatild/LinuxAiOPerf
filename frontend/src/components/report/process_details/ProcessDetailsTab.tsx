import { useState } from 'react';
import type { ProcessDetailsData } from '../../../types/report';
import SubTabBar from '../../ui/SubTabBar';
import DataTable from '../../ui/DataTable';

interface Props { data: ProcessDetailsData; }

const SUBTABS = [
  { id: 'pidstat_cpu',    label: 'Process Stats (CPU)' },
  { id: 'pidstat_io',     label: 'Process Stats (IO)' },
  { id: 'pidstat_memory', label: 'Process Stats (Memory)' },
  { id: 'top',            label: 'top' },
  { id: 'iotop',          label: 'iotop' },
];

export default function ProcessDetailsTab({ data }: Props) {
  const [sub, setSub] = useState('pidstat_cpu');

  const tabs = SUBTABS.map(t => ({
    ...t,
    available: !!data[t.id as keyof ProcessDetailsData]?.timestamps?.length,
  }));

  const activeSub = tabs.find(t => t.id === sub && t.available)
    ? sub
    : (tabs.find(t => t.available)?.id ?? sub);

  const chunkData = data[activeSub as keyof ProcessDetailsData];

  return (
    <div>
      <SubTabBar tabs={tabs} active={activeSub} onChange={setSub} />
      {chunkData
        ? <DataTable data={chunkData} />
        : <p className="text-center py-12" style={{ color: 'var(--text-muted)' }}>No data available</p>
      }
    </div>
  );
}
