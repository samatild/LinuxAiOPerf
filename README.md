# Linux AIO Performance Collector

[![Latest Release](https://img.shields.io/badge/release-v2.1.2-blue.svg)](https://github.com/samatild/LinuxAiOPerf/releases/latest)
[![Docker](https://img.shields.io/badge/docker-available-blue.svg)](https://hub.docker.com/r/samuelmatildes/linuxaioperf)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE.md)

<p float="left">
  <img src="assets/linuxaiologo.png" width="400" height="auto" />
</p>

A comprehensive performance data collector for Linux systems. Captures CPU, memory, storage, and system metrics for analysis via web interface.

## Latest Release

**Version 2.1.2** - November 2025
- Refactored resource watchdog with PID tracking and management
- Improved cron job setup with templates and management commands
- Added Debian distribution support
- Modern Python-style CLI output
- Skip validation checks flag for automation

## Web Application

**View your performance data:**

### https://linuxaioperf.matildes.dev/

The web application generates interactive HTML reports from collected data. Reports are automatically deleted after 10 minutes.

**Alternative - Run locally with Docker:**
```bash
docker run -p 8000:80 samuelmatildes/linuxaioperf:latest
# Access at http://localhost:8000
```

## Quick Start

Download and run the collector:

```bash
# Download
wget https://raw.githubusercontent.com/samatild/LinuxAiOPerf/main/build/linux_aio_perfcheck.sh

# Make executable
chmod +x linux_aio_perfcheck.sh

# Run (interactive mode)
sudo ./linux_aio_perfcheck.sh
```

Upload the generated .tar.gz file to the web application for analysis.

## Requirements

**Timezone:** LC_TIME must be set to `en_US.UTF-8`, `en_GB.UTF-8`, `C.UTF-8`, or `POSIX`. The script validates this and provides configuration instructions if needed.

**Packages:** Requires `sysstat` and `iotop`. The script will detect missing packages and offer to install them automatically.

**Supported Distributions:**
- Debian 11/12
- Ubuntu 18.04/20.04/22.04/24.04
- Red Hat Enterprise Linux 7/8/9
- Oracle Linux 7/8
- CentOS 7/8
- SUSE Linux Enterprise Server 12/15

## Usage

### Interactive Mode

Run without arguments to access the interactive menu:

```bash
sudo ./linux_aio_perfcheck.sh
```

Choose from:
1. **Collect live data** - Immediate capture (10-900 seconds)
2. **Collect via watchdog** - Trigger on resource threshold
3. **Collect via cron** - Schedule at specific times
4. **Toggle high resolution disk metrics** - 50ms sampling (live mode only)

### Command Line Mode

Quick collection without prompts:

```bash
# Quick 60-second collection
sudo ./linux_aio_perfcheck.sh --quick -t 60

# With high-resolution disk metrics
sudo ./linux_aio_perfcheck.sh --quick -t 120 -hres ON

# Skip validation checks (for automation)
sudo ./linux_aio_perfcheck.sh --quick -t 60 --skip-checks
```

### Watchdog Management

Monitor resources and trigger collection when thresholds are exceeded:

```bash
# Check watchdog status
./linux_aio_perfcheck.sh --watchdog-status

# Stop running watchdog
./linux_aio_perfcheck.sh --watchdog-stop
```

**Watchdog Features:**
- Monitors CPU, memory, and disk I/O utilization
- Configurable thresholds (default: 80%)
- Two modes: Auto (80% threshold, 60s capture) or Manual (custom settings)
- Runs as background process with PID tracking
- Logs activity to `/tmp/linuxaio_watchdog_logs/watchdog_PID.log`
- Triggers data collection automatically when thresholds exceeded
- Clean exit after collection completes

### Cron Job Management

Schedule automated collections:

```bash
# List scheduled jobs
./linux_aio_perfcheck.sh --cron-list

# Remove scheduled jobs
./linux_aio_perfcheck.sh --cron-remove
```

**Cron Features:**
- Template-based scheduling (hourly, every 6 hours, daily, custom)
- Full validation of schedules and duration
- Duplicate detection
- Uses absolute paths (works from any directory)
- Option to skip validation checks for reliability
- Easy management with list/remove commands

**Schedule Templates:**
- Every hour: `0 * * * *`
- Every 6 hours: `0 */6 * * *`
- Daily at 2:00 AM: `0 2 * * *`
- Daily at custom time
- Custom cron expression

## Collection Modes

### Live Data

Immediate data capture for troubleshooting active issues.

**Duration:** 10-900 seconds

**Use when:** Problem is happening now

**Command:**
```bash
sudo ./linux_aio_perfcheck.sh --quick -t 60
```

### Watchdog

Background monitoring that triggers collection when resource utilization exceeds thresholds.

**Duration:** 1-300 seconds (capture duration)

**Use when:** Problem happens unpredictably

**Features:**
- Single process architecture (no recursive spawning)
- PID file tracking at `/tmp/linuxaio_watchdog.pid`
- Structured logging with [INFO], [METRIC], [TRIGGER] prefixes
- Graceful shutdown with cleanup
- Status and stop commands for management

### Cron

Scheduled collections at specific times or intervals.

**Duration:** 10-900 seconds

**Use when:** Problem occurs at known times

**Features:**
- No service restart required
- Safe crontab manipulation with duplicate detection
- Timestamped comments in crontab for tracking
- Recommended to use with `--skip-checks` flag

## Collected Data

| Category | Metrics |
|----------|---------|
| CPU | mpstat, pidstat, uptime, cpuinfo |
| Memory | vmstat, free, meminfo |
| Storage | iostat, df, lsblk, parted, LVM (pv/vg/lv), /proc/diskstats, iotop, lsscsi |
| System | OS info, kernel parameters, modules, SELinux/AppArmor status |

**High Resolution Disk Metrics** (optional):
- 50ms sampling interval from `/proc/diskstats`
- Available only in live data mode
- Significantly increases data volume

## Privacy

**No PII collected:** No personal, organizational, or computer-identifying information is captured.

**Data retention:** Uploaded data is processed in-memory on the web server. Generated HTML reports are automatically deleted after 10 minutes. No database storage.

**Client-side processing:** Report visualization uses JavaScript executed in your browser. No data is sent back to the server during viewing.

## Command Reference

```
Commands:
  --quick                        Quick data collection mode
  --watchdog-status              Check watchdog status
  --watchdog-stop                Stop running watchdog
  --cron-list                    List scheduled cron jobs
  --cron-remove                  Remove scheduled cron jobs
  --version                      Show version information

Options:
  -t, --time SECONDS            Duration in seconds (10-900)
  -hres VALUE                   Enable/disable high resolution disk (ON/OFF)
  --skip-checks                 Skip locale and package validation

Examples:
  ./linux_aio_perfcheck.sh --quick -t 60
  ./linux_aio_perfcheck.sh --quick -t 120 --skip-checks
  ./linux_aio_perfcheck.sh --watchdog-status
  ./linux_aio_perfcheck.sh --cron-list
```

## Documentation

For detailed documentation and usage instructions:
- [Project Wiki](https://github.com/samatild/LinuxAiOPerf/wiki)

## Credits

Developed by [Samuel Matildes](https://github.com/samatild)

Built with:
- [Flask](https://palletsprojects.com/p/flask/) - Web framework
- [Plotly](https://plotly.com/) - Interactive visualizations
- [Pandas](https://pandas.pydata.org/) - Data processing

## License

MIT License - See LICENSE.md for details
