import { useState } from 'react';
import type { PerformanceData } from '../../../types/report';
import SubTabBar from '../../ui/SubTabBar';
import FigureGrid from '../../ui/FigureGrid';

interface Props { data: PerformanceData; }

const SUBTABS = [
  { id: 'cpu',        label: 'CPU Load Distribution' },
  { id: 'memory',     label: 'Memory Usage' },
  { id: 'disk_dev',   label: 'Disk Metrics / Device' },
  { id: 'disk_metric',label: 'Disk Device / Metrics' },
  { id: 'disk_hires', label: 'High-Res Disk' },
  { id: 'network',    label: 'Network Performance' },
];

export default function PerformanceTab({ data }: Props) {
  const [sub, setSub] = useState('cpu');

  const tabs = SUBTABS.map(t => ({
    ...t,
    available: (() => {
      switch (t.id) {
        case 'cpu':         return !!data.cpu?.figures?.length;
        case 'memory':      return !!data.memory?.figures?.length;
        case 'disk_dev':    return !!data.disk?.per_device?.figures?.length;
        case 'disk_metric': return !!data.disk?.per_metric?.figures?.length;
        case 'disk_hires':  return !!data.disk?.highres?.figures?.length;
        case 'network':     return !!data.network?.figures?.length;
        default: return false;
      }
    })(),
  }));

  const activeSub = tabs.find(t => t.id === sub && t.available)
    ? sub
    : (tabs.find(t => t.available)?.id ?? sub);

  const figures = (() => {
    switch (activeSub) {
      case 'cpu':         return data.cpu?.figures;
      case 'memory':      return data.memory?.figures;
      case 'disk_dev':    return data.disk?.per_device?.figures;
      case 'disk_metric': return data.disk?.per_metric?.figures;
      case 'disk_hires':  return data.disk?.highres?.figures;
      case 'network':     return data.network?.figures;
    }
  })();

  return (
    <div>
      <SubTabBar tabs={tabs} active={activeSub} onChange={setSub} />
      <FigureGrid figures={figures} />
    </div>
  );
}
