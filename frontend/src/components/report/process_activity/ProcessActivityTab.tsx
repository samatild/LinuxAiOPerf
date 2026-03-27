import { useState } from 'react';
import type { ProcessActivityData } from '../../../types/report';
import SubTabBar from '../../ui/SubTabBar';
import FigureGrid from '../../ui/FigureGrid';

interface Props { data: ProcessActivityData; }

const SUBTABS = [
  { id: 'cpu',    label: 'Top CPU Consumers' },
  { id: 'io',     label: 'Top IO Consumers' },
  { id: 'memory', label: 'Top Memory Consumers' },
];

export default function ProcessActivityTab({ data }: Props) {
  const [sub, setSub] = useState('cpu');

  const tabs = SUBTABS.map(t => ({
    ...t,
    available: !!(data[t.id as keyof ProcessActivityData]?.figures?.length),
  }));

  const activeSub = tabs.find(t => t.id === sub && t.available)
    ? sub
    : (tabs.find(t => t.available)?.id ?? sub);

  const figures = data[activeSub as keyof ProcessActivityData]?.figures;

  return (
    <div>
      <SubTabBar tabs={tabs} active={activeSub} onChange={setSub} />
      <FigureGrid figures={figures} />
    </div>
  );
}
