
The current project is a flask webapp that analyzes performance data collected from Linux systems. The user uploads a .tar.gz file containing the collected data, and the webapp generates interactive HTML reports for analysis. 

We have the following examples available of files being used inside:
- rhel9_20260326_123127_linuxaioperfcheck
- ubuntu2004_20250910_145417_linuxaioperfcheck

The website structure is as follows:
- Home page with upload form (drag and drop or file selector)
- Once a file is uploaded, the user is redirected to a report page with interactive charts and tables generated from the data.

# Report Structure
Report contains a overview page and then multiple tabs and subtabs with different types of analysis.

Tab structure with the respective subtab and their content is as follows:

- System Configuration (Main Tab)
  - Information (Default subtab): 
    - Runtime Information from info.txt
    - OS releas from os-release
  - Hardware:
    - lshw.txt
    - dmidecode.txt
  - Storage: 
    - lsscsi.txt
    - lsblk-f.txt
    - df-h.txt
    - ls-l-dev-mapper.txt
  - LVM Layout: <- only if LVM is detected
    - Constructs beauqtiful diagrams of the LVM layout using multiple files. There's a python method.
    - pvs.txt
    - vgs.txt
    - lvs.txt
    - pvdisplay.txt
    - vgdisplay.txt
    - lvdisplay.txt
  - CPU Info:
    - lscpu.txt
  - Memory Info:
    - meminfo.txt
  - Kernel Parameters:
    - sysctl.txt
  - Kernel Modules:
    - lsmod.txt
  - Security:
    - selinux.txt
    - apparmor.txt
  
- System Performance (Main Tab)
  - CPU Load DIstribution (Default subtab):
    - Contains a plot per CPU metric available from mpstat.txt (user, system, iowait, steal, etc). Each plot shows the distribution of the metric across all CPUs over time. We can filter per core except for All CPU Usage data. 
  - Memory Usage:
    - Contains a plot of memory usage over time from vmstat-data.out
  - Disk Metrics/Device: A single plot per each drive showing the disk metrics over time. The metrics are read from iostat-data.out. We filter per metric.
  - Disk Device/Metrics: A single plot per each metric showing the distribution of the metric across all devices over time. The metrics are read from iostat-data.out. We filter per device.
  - High Resolution Disk Metrics: Only if the user enabled high resolution disk metrics. Contains a single plot per each drive showing the disk metrics over time with 50ms sampling interval. The metrics are read from diskstats_log.txt. We can change time granularity from 1sec to 50ms. Theres'a a latency boxplot that shows the distribution of latency across all devices. There's an isolated python method that processes the high resolution disk metrics and generates the necessary data for the plots.
  - Network Performance: Contains plots of network performance metrics over time from sarnetwork.txt

- Process Activity (Main Tab)
  - Top Processes by CPU Usage (Default subtab): Plot from top 10 cpu consuming processes over time from pidstat-cpu.txt  check pythond method
  - Top 10 IO consuming processes: Plot from top 10 io consuming processes over time from pidstat-io.txt check pythond method
  - Top 10 Memory consuming processes: Plot from top 10 memory consuming processes over time

- Proccess Details (Main Tab)
  - Process stats (CPU): A searchable combobox with all available timestamps . When the user selects a timestamp, we show a table with all processes and their CPU usage at that timestamp. The data is read from pidstat-cpu.txt. check pythond method
  - Process stats (IO): A searchable combobox with all available timestamps . When the user selects a timestamp, we show a table with all processes and their IO usage at that timestamp. The data is read from pidstat-io.txt. check pythond method
  - Process stats (Memory): A searchable combobox with all available timestamps . When the user selects a timestamp, we show a table with all processes and their memory usage at that timestamp. The data is read from pidstat-memory.txt. check pythond method
  - top: the same approach but for top output. A searchable combobox with all available timestamps . When the user selects a timestamp, we show a table with all processes and their CPU, Memory and IO usage at that timestamp. The data is read from top.txt. check pythond method
  - iotop: the same approach but for iotop output. A searchable combobox with all available timestamps . When the user selects a timestamp, we show a table with all processes and their IO usage at that timestamp. The data is read from iotop.txt. check pythond method


# What is the goal (Main objective)
Create a serverless webapp and modernize the UI/UX of the report to make it more user friendly and visually appealing. The webapp should be able to handle large data sets efficiently and provide interactive visualizations for better analysis of the performance data. While maintaining the core functionality of the original report, we want to enhance the user experience and make it easier for users to navigate through the data and gain insights from it.

Important points to respect:
- We need to chose a serverless stack with a modern architecuture. GO/NodeJS for the backend and React for the frontend are good options. Vercel compatible would be good for free hosting. Otherwise we can also deploy locally with Docker.
- UI should be modern, but fast.
- Currently is fast to navigate as it's server app. 

# Job (step by step)
1. analyze the current codebase and understand how the data is processed and visualized in the current report. Identify the key components and functionalities that need to be replicated in the new webapp.
2. Design the architecture of the new webapp, choosing a serverless stack and defining the frontend and backend components. Decide on the data flow and how the different components will interact with each other.
3. Create a branch for the new webapp development and set up the necessary development environment and tools.
4. Migrate by phases. Starting each tab one by one. Once we get into plots we do a subtab at a time. For each tab/subtab, we need to replicate the same functionality and visualizations as in the original report, but with a modern UI/UX design. 
5. Chose a proper and modern graph/plot library for the frontend that can handle large data sets efficiently and provide interactive visualizations. 

