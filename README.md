# Linux AIO Performance Checker

<p float="left">

  <img src="assets/linuxaiologo.png" />

</p>

Linux AIO Performance Checker is a script that collects performance data from a Linux system and generates a report in HTML format. The report can be uploaded to a web application that will display the data in a user-friendly way.

## Latest Release
➕ **Version 1.43.1** - 15/May 2025
- Added boxplot for High Resolution Disk Latency

🎉 **Version 1.43.0** - 06/May 2025
- Added NVMe disks support


## Key Features

- All-in-one Linux Performance Collector Script.
- Report generated directly over Web Application.
- Fast, simple and user friendly.

## Documentation

For detailed documentation and usage instructions, please visit:
- 📚 [Project Wiki](https://github.com/samatild/LinuxAiOPerf/wiki)

## Quick Start (Instructions)

1. **⬇️ Download and execute the script:**

   ```bash
    # Download
    wget https://raw.githubusercontent.com/samatild/LinuxAiOPerf/main/build/linux_aio_perfcheck.sh
    
    # Make it executable
    sudo chmod +x linux_aio_perfcheck.sh
    
    # Run it
    sudo ./linux_aio_perfcheck.sh
   ```



2. **📤 Upload the generated ZIP file:**
   > ### [➡️ Linux AIO Perf Checker Web Application](https://linuxaioperf.matildes.dev/)
   > This web interface will process your data and generate an interactive performance report.

## Command-Line Usage

Alternatively, the script can be run directly from the command line with various options:

Collect a 30 seconds quick report:
```
./linux_aio_perfcheck.sh --quick -t 30
```

Collect a 60 seconds quick report with high resolution disk metrics:
```
./linux_aio_perfcheck.sh --quick -t 60 -hres ON
```


## Requirements
⚠️ **Timezone:** Compatible LC_TIME formats are: en_US.UTF-8 ; en_GB.UTF-8 ; C.UTF-8 ; POSIX ; The script will validate this requirement at the beggining and will provide instructions to the user on how to change it.

⚠️ **Packages:** sysstat and iotop packages are required for the script to execute. If they are not installed, the script will install them automatically. If the script is not able to install them, it will exit with an error message.


## Run Modes


| Run Mode | What it does | For what occasion |  
|----------|----------|----------|
| Collect live data | It will collect data right away during a timespan from 10-900sec  | Problem is happening now |
| Collect data via watchdog (Triggered by High CPU, Memory, or Disk IO) | It will setup a watchdog that will keep an eye for resource Utilization. Auto or Manual modes available | For when you don't know when the problem is going to happen. | 
| Collect data via cron (At a specific time)  | It will setup a cronjob based on user instructions. There are 2 different cronjobs: Recurrent will repeat the collection based on user section. Not Recurrent will trigger the data collection at a specific time.  | For when you know when the problem happenss. |
 
   > ⚠️ **Attention:** When running on the 3rd mode (cronjob) the script will create a crontab entry but will not delete it. If you want to delete it you will need to do it manually. Don't forget to restart chronyd service after deleting the crontab entry.

### [Mode] Live Data

```
1. Live data mode is intended to initiate immediate capture.
2. User needs to select a duration between 10 seconds and 900 seconds (15min)
3. Report will be based on current metrics and will not contain historical data.
```
### [Mode] Watchdog

```
1. Watchdog is intended for scenarios when the user doesn't know when the problem is going to happen.
2. If the user knows what resource is affected , he can decide which resource to monitor.
3. User can also define a custom Threshold to monitor each resource (eg: 100% of CPU). On this mode, the user can select the duration of the collection between 1 and 300 seconds.
4. Default options will monitor CPU, Memory and Disk activity and will trigger the collection at 80% with the default duration of 60 seconds.
5. Watchdog will log its activity on a file located in current working dir named LinuxAiO_watchdog_$(date +'%Y%m%d_%H%M%S').log
6. Watchdog will automatically restart itself every hour for regular housekeeping.
7. Watchdog will run until user stops it or threshold is reached.
```
### [Mode] Cronjob

```
1. Cron is intended for scenarios where the user knows at which time the problem is going to happen.
2. User will be prompted if cronjob needs to be reccurent (every hour, every day) or not.
3. Cronjob will be setup according to user selection and will run until user deletes the cron entry.
```

## Compatibility

The collector script is compatible with most modern Linux distributions as it uses standard OS commands to collect data.

It as been tested with the following Linux distributions:

- Ubuntu 18.04
- Ubuntu 20.04
- Red Hat Enterprise Linux 7
- Red Hat Enterprise Linux 8
- Oracle Linux 7
- Oracle Linux 8
- CentOS 7
- CentOS 8
- SUSE Linux Enterprise Server 15
- SUSE Linux Enterprise Server 12


## What data is collected?

The following data is collected:

| Resource Type | Collected Data |
|----------|----------|
| CPU  | mpstat, pidstat, uptime, cpuinfo  |
| Memory   | vmstat, free, meminfo   |
| Storage   | iostat, df -h, lsblk -f, parted -l, pvdisplay, vgdisplay, lvdisplay, pvscan, vgscan, lvscan, ls -l /dev/mapper, iotop, lsscsi, /proc/diskstats    |
| Generic OS information   | date, top, ps -H, sar, os-release, last installed updates, sysctl -a, lsmod, selinux/apparmor dettection |

> ✅ **PII Notice:** No Personal, organization, or computer identifiable information is collected.


## Data privacy

The uploaded data will not be stored on the web server. The data is stored in a temporary directory on the web server and is deleted after 10 minutes.

Part of the data processing requires the execution of JavaScript code on the client-side. The JavaScript code is executed in the browser and does not send any data to the web server.

## Data Retention Policy

Every report will have its own unique ID. The UID is randomly generated and is not related to the data contained in the report. The UID is used to identify the report and to allow the user to view it. The UID is not stored in the database. 

Each time a user uploads a ZIP file containing performance data, the data is deleted once report is fully generated. The report HTML file will get deleted after 10 minutes.

## Credits

This project was developed by [Samuel Matildes](https://github.com/samatild)

The code makes use of the following open-source projects:
- Flask - [
The Pallets Projects](https://palletsprojects.com/p/flask/)
- plotly - [
plotly](https://plotly.com/)
- pandas - [
pandas](https://pandas.pydata.org/)

