import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Activity, Check, Copy, GitBranch, LockKeyhole, Terminal, Zap } from 'lucide-react';
import { useUpload } from '../hooks/useUpload';
import { setReportData } from '../store/reportStore';
import UploadBox from '../components/upload/UploadBox';
import Header from '../components/layout/Header';
import Footer from '../components/layout/Footer';
import Spinner from '../components/ui/Spinner';
import KofiButton from '../components/ui/KofiButton';
import { GITHUB_URL } from '../version';

const QUICK_START_COMMAND = `curl -fsSLO https://raw.githubusercontent.com/samatild/LinuxAiOPerf/main/build/linux_aio_perfcheck.sh
chmod +x linux_aio_perfcheck.sh
sudo ./linux_aio_perfcheck.sh
# Or for quick 60s capture:
# sudo ./linux_aio_perfcheck.sh --quick -t 60`;

export default function Upload() {
  const { state, upload } = useUpload();
  const navigate = useNavigate();
  const [copyStatus, setCopyStatus] = useState<'idle' | 'copied' | 'failed'>('idle');

  useEffect(() => {
    if (state.status === 'done') {
      setReportData(state.data);   // store in memory — no size limit
      navigate('/report');
    }
  }, [state, navigate]);

  function copyQuickStart() {
    navigator.clipboard.writeText(QUICK_START_COMMAND).then(
      () => {
        setCopyStatus('copied');
        window.setTimeout(() => setCopyStatus('idle'), 2000);
      },
      () => setCopyStatus('failed'),
    );
  }

  return (
    <div className="upload-shell min-h-screen flex flex-col">
      <Header />
      <main className="upload-main flex-1 flex flex-col items-center justify-center px-4 py-16">
        <div className="relative z-10 w-full max-w-3xl space-y-8">
          <div className="upload-hero text-center space-y-4">
            <h2 className="text-4xl font-bold tracking-tight" style={{ color: 'var(--text-primary)' }}>
              Analyse Linux performance data
            </h2>
            <p className="text-base max-w-xl mx-auto leading-7" style={{ color: 'var(--text-secondary)' }}>
              Import a{' '}
              <code
                className="mono px-1.5 py-0.5 rounded"
                style={{ color: 'var(--accent)', background: 'var(--accent-subtle)' }}
              >
                .tar.gz
              </code>{' '}
              archive from the Linux AIO Performance Collector to generate an interactive telemetry report.
            </p>
            <a
              href={GITHUB_URL}
              target="_blank"
              rel="noopener noreferrer"
              className="upload-project-link"
            >
              <GitBranch size={16} />
              View Project on GitHub
            </a>
          </div>

          {state.status === 'uploading' ? (
            <div
              className="upload-panel rounded-2xl p-12"
              style={{ background: 'var(--bg-surface)', border: '1px solid var(--border)' }}
            >
              <Spinner label="Processing archive — this may take up to 60 seconds..." />
            </div>
          ) : (
            <div
              className="upload-panel rounded-2xl p-4 sm:p-6"
              style={{ background: 'var(--bg-surface)', border: '1px solid var(--border)' }}
            >
              <UploadBox onFile={upload} />
            </div>
          )}

          <section className="quick-start" aria-labelledby="quick-start-title">
            <div className="quick-start-header">
              <div>
                <div className="quick-start-title">
                  <Terminal size={16} />
                  <h3 id="quick-start-title">Quick start</h3>
                </div>
                <p>Run this on the Linux system you want to analyse.</p>
              </div>
              <button type="button" onClick={copyQuickStart} className="quick-start-copy">
                {copyStatus === 'copied' ? <Check size={15} /> : <Copy size={15} />}
                {copyStatus === 'copied' ? 'Copied' : copyStatus === 'failed' ? 'Copy failed' : 'Copy'}
              </button>
            </div>
            <pre className="quick-start-command"><code>{QUICK_START_COMMAND}</code></pre>
          </section>

          {state.status === 'error' && (
            <div
              className="rounded-xl px-5 py-4 text-sm"
              style={{
                background: 'color-mix(in srgb, var(--status-error) 12%, transparent)',
                border: '1px solid color-mix(in srgb, var(--status-error) 40%, transparent)',
                color: 'var(--status-error)',
              }}
            >
              <span className="font-semibold">Error: </span>{state.message}
            </div>
          )}

          <div className="grid grid-cols-3 gap-4 text-center">
            {[
              { icon: <LockKeyhole size={20} />, title: 'Private', desc: 'Data is processed in memory and removed after analysis' },
              { icon: <Zap size={20} />, title: 'Interactive', desc: 'Explore charts without page reloads' },
              { icon: <Activity size={20} />, title: 'Comprehensive', desc: 'CPU, disk, memory, network, and processes' },
            ].map(({ icon, title, desc }) => (
              <div
                key={title}
                className="upload-capability rounded-xl p-4"
                style={{ background: 'var(--bg-surface)', border: '1px solid var(--border)' }}
              >
                <div className="flex justify-center mb-3" style={{ color: 'var(--accent)' }}>{icon}</div>
                <div className="text-sm font-semibold" style={{ color: 'var(--text-primary)' }}>{title}</div>
                <div className="text-xs mt-1" style={{ color: 'var(--text-muted)' }}>{desc}</div>
              </div>
            ))}
          </div>

          <KofiButton />
        </div>
      </main>
      <Footer />
    </div>
  );
}
