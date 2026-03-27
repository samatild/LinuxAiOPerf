import { useState } from 'react';
import { useLocation, Navigate } from 'react-router-dom';
import type { ReportData } from '../types/report';
import Header from '../components/layout/Header';
import SysConfigTab from '../components/report/sysconfig/SysConfigTab';
import PerformanceTab from '../components/report/performance/PerformanceTab';
import ProcessActivityTab from '../components/report/process_activity/ProcessActivityTab';
import ProcessDetailsTab from '../components/report/process_details/ProcessDetailsTab';

const MAIN_TABS = [
  { id: 'sysconfig',        label: 'System Configuration' },
  { id: 'performance',      label: 'System Performance' },
  { id: 'process_activity', label: 'Process Activity' },
  { id: 'process_details',  label: 'Process Details' },
];

export default function Report() {
  const { state } = useLocation();
  const data = state?.data as ReportData | undefined;
  const [activeTab, setActiveTab] = useState('sysconfig');

  if (!data) return <Navigate to="/" replace />;

  const tabs = MAIN_TABS.map(t => ({
    ...t,
    available: (() => {
      switch (t.id) {
        case 'sysconfig':        return !!data.sysconfig;
        case 'performance':      return !!data.performance;
        case 'process_activity': return !!data.process_activity;
        case 'process_details':  return !!data.process_details;
        default: return false;
      }
    })(),
  }));

  const effectiveTab = tabs.find(t => t.id === activeTab && t.available)
    ? activeTab
    : (tabs.find(t => t.available)?.id ?? activeTab);

  return (
    <div className="min-h-screen bg-[#0f1117] flex flex-col">
      <Header metadata={data.metadata} showBack />

      {/* Main tab bar */}
      <div className="bg-[#0f1117] border-b border-[#2d3149] sticky top-[57px] z-40">
        <div className="max-w-screen-2xl mx-auto px-6 flex overflow-x-auto">
          {tabs.map(({ id, label, available }) => (
            <button
              key={id}
              onClick={() => available && setActiveTab(id)}
              disabled={!available}
              className={`px-5 py-3.5 text-sm font-medium whitespace-nowrap border-b-2 transition-all duration-150 ${
                effectiveTab === id
                  ? 'border-indigo-500 text-indigo-400'
                  : available
                  ? 'border-transparent text-slate-400 hover:text-slate-200 hover:border-[#2d3149]'
                  : 'border-transparent text-slate-600 cursor-not-allowed'
              }`}
            >
              {label}
            </button>
          ))}
        </div>
      </div>

      {/* Tab content */}
      <main className="flex-1 max-w-screen-2xl mx-auto w-full px-6 py-6">
        {effectiveTab === 'sysconfig' && data.sysconfig && (
          <SysConfigTab data={data.sysconfig} />
        )}
        {effectiveTab === 'performance' && data.performance && (
          <PerformanceTab data={data.performance} />
        )}
        {effectiveTab === 'process_activity' && data.process_activity && (
          <ProcessActivityTab data={data.process_activity} />
        )}
        {effectiveTab === 'process_details' && data.process_details && (
          <ProcessDetailsTab data={data.process_details} />
        )}
      </main>
    </div>
  );
}
