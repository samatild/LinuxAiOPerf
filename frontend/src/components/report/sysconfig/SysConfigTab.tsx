import { useState } from 'react';
import type { CaptureHealth, SysConfigData } from '../../../types/report';
import CaptureHealthPanel from '../CaptureHealthPanel';
import SubTabBar from '../../ui/SubTabBar';
import TextBlock from '../../ui/TextBlock';
import LvmDiagram from './LvmDiagram';

interface Props {
  data: SysConfigData;
  captureHealth?: CaptureHealth;
}

function CapacityRiskTable({ capacity }: { capacity: NonNullable<SysConfigData['storage']>['capacity'] }) {
  if (!capacity?.length) return null;

  return (
    <section className="mb-4 overflow-x-auto rounded-lg border border-[var(--border)]" aria-labelledby="capacity-risk-heading">
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-[var(--border)] px-4 py-3">
        <div>
          <h3 id="capacity-risk-heading" className="font-semibold">Filesystem capacity risk</h3>
          <p className="text-sm text-[var(--text-muted)]">Warning at 85%; critical at 95% used.</p>
        </div>
      </div>
      <table className="w-full min-w-[42rem] text-left text-sm">
        <thead className="bg-[var(--bg-elevated)] text-[var(--text-muted)]">
          <tr>
            <th scope="col" className="px-4 py-2 font-medium">Mount</th>
            <th scope="col" className="px-4 py-2 font-medium">Filesystem</th>
            <th scope="col" className="px-4 py-2 font-medium">Used</th>
            <th scope="col" className="px-4 py-2 font-medium">Available</th>
            <th scope="col" className="px-4 py-2 font-medium">Size</th>
            <th scope="col" className="px-4 py-2 font-medium">Risk</th>
          </tr>
        </thead>
        <tbody>
          {capacity.map(row => (
            <tr key={`${row.filesystem}-${row.mount}`} className="border-t border-[var(--border)]">
              <th scope="row" className="px-4 py-2 font-medium">{row.mount}</th>
              <td className="mono px-4 py-2">{row.filesystem}</td>
              <td className="px-4 py-2">{row.used} ({row.use_percent}%)</td>
              <td className="px-4 py-2">{row.available}</td>
              <td className="px-4 py-2">{row.size}</td>
              <td className="px-4 py-2">
                <span className={row.severity === 'critical' ? 'threshold-critical rounded px-2 py-1 font-medium' : row.severity === 'warning' ? 'threshold-warning rounded px-2 py-1 font-medium' : 'rounded bg-[var(--bg-elevated)] px-2 py-1 font-medium'}>
                  {row.severity === 'normal' ? 'Normal' : row.severity === 'warning' ? 'Warning' : 'Critical'}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}

const SUBTABS = [
  { id: 'information', label: 'Information' },
  { id: 'hardware',    label: 'Hardware' },
  { id: 'storage',     label: 'Storage' },
  { id: 'lvm',         label: 'LVM Layout' },
  { id: 'cpu_info',    label: 'CPU Info' },
  { id: 'memory_info', label: 'Memory Info' },
  { id: 'kernel_params', label: 'Kernel Parameters' },
  { id: 'kernel_modules', label: 'Kernel Modules' },
  { id: 'security',    label: 'Security' },
];

export default function SysConfigTab({ data, captureHealth }: Props) {
  const [sub, setSub] = useState('information');

  const available = SUBTABS.map(t => ({
    ...t,
    available: (() => {
      switch (t.id) {
        case 'information': return !!(data.information?.runtime_info || data.information?.os_release);
        case 'hardware':    return !!(data.hardware?.lshw || data.hardware?.dmidecode);
        case 'storage':     return !!(data.storage?.df || data.storage?.lsblk || data.storage?.lsscsi);
        case 'lvm':         return !!(data.lvm?.topology || data.lvm?.lvs_raw);
        case 'cpu_info':    return !!data.cpu_info;
        case 'memory_info': return !!data.memory_info;
        case 'kernel_params': return !!data.kernel_params;
        case 'kernel_modules': return !!data.kernel_modules;
        case 'security':    return !!data.security;
        default: return false;
      }
    })(),
  }));

  // Auto-select first available subtab
  const activeSub = available.find(t => t.id === sub && t.available)
    ? sub
    : (available.find(t => t.available)?.id ?? sub);

  return (
    <div>
      <SubTabBar tabs={available} active={activeSub} onChange={setSub} />
      <div className="mt-2">
        {activeSub === 'information' && (
          <>
            <TextBlock label="Runtime Information" content={data.information?.runtime_info} />
            {captureHealth && <CaptureHealthPanel data={captureHealth} />}
            <TextBlock label="OS Release" content={data.information?.os_release} />
          </>
        )}
        {activeSub === 'hardware' && (
          <>
            <TextBlock label="lshw" content={data.hardware?.lshw} />
            <TextBlock label="dmidecode" content={data.hardware?.dmidecode} />
          </>
        )}
        {activeSub === 'storage' && (
          <>
            <CapacityRiskTable capacity={data.storage?.capacity} />
            <TextBlock label="lsscsi" content={data.storage?.lsscsi} />
            <TextBlock label="lsblk -f" content={data.storage?.lsblk} />
            <TextBlock label="df -h" content={data.storage?.df} />
            <TextBlock label="ls -l /dev/mapper" content={data.storage?.ls_dev_mapper} />
          </>
        )}
        {activeSub === 'lvm' && (
          <div>
            {data.lvm?.topology && (
              <div className="mb-6">
                <LvmDiagram topology={data.lvm.topology} />
              </div>
            )}
            <TextBlock label="pvs" content={data.lvm?.pvs_raw} />
            <TextBlock label="vgs" content={data.lvm?.vgs_raw} />
            <TextBlock label="lvs" content={data.lvm?.lvs_raw} />
            <TextBlock label="pvdisplay" content={data.lvm?.pvdisplay_raw} />
            <TextBlock label="vgdisplay" content={data.lvm?.vgdisplay_raw} />
            <TextBlock label="lvdisplay" content={data.lvm?.lvdisplay_raw} />
          </div>
        )}
        {activeSub === 'cpu_info' && <TextBlock label="lscpu" content={data.cpu_info} />}
        {activeSub === 'memory_info' && <TextBlock label="meminfo" content={data.memory_info} />}
        {activeSub === 'kernel_params' && <TextBlock label="sysctl -a" content={data.kernel_params} />}
        {activeSub === 'kernel_modules' && <TextBlock label="lsmod" content={data.kernel_modules} />}
        {activeSub === 'security' && <TextBlock label="Security Status" content={data.security} />}
      </div>
    </div>
  );
}
