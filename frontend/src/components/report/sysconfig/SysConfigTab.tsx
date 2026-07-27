import { useState } from 'react';
import type { SysConfigData } from '../../../types/report';
import SubTabBar from '../../ui/SubTabBar';
import TextBlock from '../../ui/TextBlock';
import LvmDiagram from './LvmDiagram';

interface Props { data: SysConfigData; }

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

export default function SysConfigTab({ data }: Props) {
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
