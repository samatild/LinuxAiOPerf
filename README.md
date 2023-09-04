# Linux AIO Performance Checker

Linux AIO Performance Checker is a web application built with Flask that allows you to upload and process ZIP files containing performance data for analysis. It provides an intuitive interface to upload report files, extract their contents, execute performance analysis scripts, and view generated reports.

## Key Features

- All-in-one Linux Performance Collector Script.
- Report generated directly over Web Application.
- Fast, simple and user friendly.

## How to Generate Reports
### -> Open Report Generator: [Linux AIO Performance Checker](https://linuxaioperf.matildes.dev/) <-
![generate data](assets/uploading_data.gif)



## How to Collect Data (Capture)

![how to collect data](assets/collecting_data.gif)

1. You will need first to collect data from a Linux system using the collector: [Download Latest Release](https://github.com/samatild/LinuxAiOPerf/releases/latest) 
    
    Download it, and place it on the Linux system you want to collect data from.
    
    Example:
     ```bash
    wget https://github.com/samatild/LinuxAiOPerf/releases/download/1.7/linux_aio_perfcheck.tgz
    tar xfz linux_aio_perfcheck.tgz
     ```

2. Once uploaded to the Linux system, make it executable by running the following command:

   ```bash
    chmod +x linux_aio_perfcheck.sh
    ```

3. Execute the script as root:

   ```bash
    sudo ./linux_aio_perfcheck.sh 
    # Note: the script will ask you to enter the desired time interval for data collection The minimum time interval is 10 seconds. The maximum time interval is 900 seconds (15 minutes)
    ```

    > ⚠️ **Warning:** sysstat and iotop packages are required for the script to execute. If packages are not installed the script will prompt user to install them. If user disagrees the script will exit.

4. The script will collect performance data and generate a ZIP file containing the collected data. Upload the generated ZIP file to the [Linux AIO Perf Checker Web Application.](https://linuxaioperf.matildes.dev/)

## 🌟 Run Modes (New)


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
3. User can also define a custom Threshold to monitor each resource (eg: 100% of CPU)
4. Default options will monitor CPU, Memory and Disk activity and will trigger the collection at 80%

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
- CentOS 7
- CentOS 8
- Red Hat Enterprise Linux 7
- Red Hat Enterprise Linux 8
- SUSE Linux Enterprise Server 15
- SUSE Linux Enterprise Server 12

## Interpreting Reports

Work in progress... (will be updated soon with items below)

1. Report Overview
2. Understanding the metrics
3. Cross-referencing metrics with attached logs

## What data is collected?

The following data is collected:

| Resource Type | Collected Data |
|----------|----------|
| CPU  | mpstat, pidstat, uptime   |
| Memory   | vmstat, free   |
| Storage   | iostat, df -h, lsblk -f, parted -l, pvdisplay, vgdisplay, lvdisplay, pvscan, vgscan, lvscan, ls -l /dev/mapper, iotop   |
| Generic OS information   | date, top, ps -H, sar, os-release, last installed updates |

> ✅ **PII Notice:** No Personal, organization, or computer identifiable information is collected.


## Data privacy

The data collected is not stored on the web server. The data is stored in a temporary directory on the web server and is deleted after 10 minutes.

Part of the data processing requires the execution of JavaScript code on the client-side. The JavaScript code is executed in the browser and does not send any data to the web server.

## Data Retention Policy

Every report will have its own unique ID. The UID is randomly generated and is not related to the data contained in the report. The UID is used to identify the report and to allow the user to view it. The UID is not stored in the database. The UID is used as the name of the directory where the report is stored.

Each time a user uploads a ZIP file containing performance data, the data is stored in a temporary directory on the web server. The data is deleted after 10 minutes.

## Credits

This project was developed by [Samuel Matildes](https://github.com/samatild)

The code makes use of the following open-source projects:
- Flask - [
The Pallets Projects](https://palletsprojects.com/p/flask/)
- plotly - [
plotly](https://plotly.com/)
- pandas - [
pandas](https://pandas.pydata.org/)

