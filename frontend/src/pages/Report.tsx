import { useState } from 'react';
import { Navigate } from 'react-router-dom';
import type { ReportData } from '../types/report';
import { getReportData } from '../store/reportStore';
import Header from '../components/layout/Header';
import CountersPanel from '../components/ui/CountersPanel';
import SysConfigTab from '../components/report/sysconfig/SysConfigTab';
import PerformanceTab from '../components/report/performance/PerformanceTab';
import ProcessActivityTab from '../components/report/process_activity/ProcessActivityTab';
import ProcessDetailsTab from '../components/report/process_details/ProcessDetailsTab';
import AboutTab from '../components/report/AboutTab';

const MAIN_TABS = [
  { id: 'sysconfig',        label: 'System Configuration' },
  { id: 'performance',      label: 'System Performance' },
  { id: 'process_activity', label: 'Process Activity' },
  { id: 'process_details',  label: 'Process Details' },
  { id: 'about',            label: 'About' },
];

export default function Report() {
  const data = getReportData() as ReportData | null;
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
        case 'about':            return true;
        default: return false;
      }
    })(),
  }));

  const effectiveTab = tabs.find(t => t.id === activeTab && t.available)
    ? activeTab
    : (tabs.find(t => t.available)?.id ?? activeTab);

  return (
    <div className="min-h-screen flex flex-col" style={{ background: 'var(--bg-base)' }}>
      <Header metadata={data.metadata} showBack />
      <CountersPanel />

      {/* Main tab bar */}
      <div className="sticky top-[57px] z-40" style={{ background: 'var(--bg-base)', borderBottom: '1px solid var(--border)' }}>
        <div className="w-[80%] max-w-[1600px] mx-auto px-6 flex overflow-x-auto">
          {tabs.map(({ id, label, available }) => (
            <button
              key={id}
              onClick={() => available && setActiveTab(id)}
              disabled={!available}
              className="px-5 py-3.5 text-sm font-medium whitespace-nowrap border-b-2 transition-all duration-150 cursor-pointer"
              style={
                effectiveTab === id
                  ? { borderBottomColor: 'var(--accent)', color: 'var(--accent)' }
                  : available
                  ? { borderBottomColor: 'transparent', color: 'var(--text-secondary)' }
                  : { borderBottomColor: 'transparent', color: 'var(--text-dim)', cursor: 'not-allowed' }
              }
              onMouseEnter={e => {
                if (available && effectiveTab !== id)
                  (e.currentTarget as HTMLElement).style.color = 'var(--text-primary)';
              }}
              onMouseLeave={e => {
                if (available && effectiveTab !== id)
                  (e.currentTarget as HTMLElement).style.color = 'var(--text-secondary)';
              }}
            >
              {label}
            </button>
          ))}
        </div>
      </div>

      {/* Tab content */}
      <main className="flex-1 w-[80%] max-w-[1600px] mx-auto w-full px-6 py-6">
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
        {effectiveTab === 'about' && <AboutTab />}
      </main>
    </div>
  );
}
