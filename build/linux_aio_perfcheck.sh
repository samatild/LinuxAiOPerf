#!/bin/bash

# Linux All-in-one Performance Collector 
# Description:  shell script which collects performance data for analysis
# About: https://github.com/samatild/LinuxAiOPerf
# version: 2.1.2
# Date: 30/May/2025
     
runmode="null"

# Declare a global variable for High Resolution Disk metrics
high_res_disk_metrics="OFF"

# Declare a global variable for skipping validation checks
skip_checks="OFF"

function print_usage() {
    echo ""
    echo -e "\e[1;37mLinux All-in-One Performance Collector\e[0m"
    echo -e "\e[0;36m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\e[0m"
    echo ""
    echo -e "\e[1;33mUsage:\e[0m"
    echo -e "  $0 [OPTIONS] COMMAND"
    echo ""
    echo -e "\e[1;33mCommands:\e[0m"
    echo -e "  \e[1;32m--quick\e[0m                        Quick data collection mode"
    echo -e "  \e[1;32m--watchdog-status\e[0m              Check watchdog status"
    echo -e "  \e[1;32m--watchdog-stop\e[0m                Stop running watchdog"
    echo -e "  \e[1;32m--version\e[0m                      Show version information"
    echo ""
    echo -e "\e[1;33mOptions:\e[0m"
    echo -e "  \e[1;32m-t, --time\e[0m SECONDS            Duration in seconds (10-900)"
    echo -e "  \e[1;32m-hres\e[0m VALUE                   Enable/disable high resolution disk counters (ON/OFF)"
    echo -e "  \e[1;32m--high-resolution-disk-counters=\e[0mVALUE"
    echo -e "  \e[1;32m--skip-checks\e[0m                  Skip locale and package validation checks"
    echo ""
    echo -e "\e[1;33mExamples:\e[0m"
    echo -e "  \e[0;36m$0 --quick -t 60 -hres ON\e[0m"
    echo -e "  \e[0;36m$0 --quick --time 300 --high-resolution-disk-counters=OFF\e[0m"
    echo -e "  \e[0;36m$0 --quick -t 120 --skip-checks\e[0m"
    echo -e "  \e[0;36m$0 --watchdog-status\e[0m"
    echo ""
    echo -e "\e[0;90mNote: Run without arguments to start in interactive mode\e[0m"
    echo ""
}
setLocalInstructions(){
    clear
    echo ""
    echo -e "\e[1;37mInstructions: Update Local Time Zone Settings\e[0m"
    echo -e "\e[0;36m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\e[0m"
    echo ""
    echo -e "\e[1;37mLinux Generic Procedure:\e[0m"
    echo ""
    echo -e "\e[1;36m→\e[0m Check what Language packages are installed:"
    echo -e "  \e[0;90m$\e[0m locale -a"
    echo ""
    echo -e "\e[1;36m→\e[0m Install if necessary:"
    echo -e "  \e[0;90m$\e[0m localedef -i en_US -f UTF-8 en_US.UTF-8"
    echo ""
    echo -e "\e[1;36m→\e[0m Change LC_TIME to en_US.UTF-8:"
    echo -e "  \e[0;90m$\e[0m localectl set-locale LC_TIME=en_US.UTF-8"
    echo ""
    echo -e "\e[1;36m→\e[0m Exit your current user session and re-login"
    echo -e "  \e[0;90m(source new locale settings)\e[0m"
    echo ""
    echo -e "\e[1;36m→\e[0m Revert if needed:"
    echo -e "  \e[0;90m$\e[0m localectl set-locale LC_TIME=<original value>"
    echo ""
    echo -e "\e[0;90mOnce done, re-run the Collector script.\e[0m"
    echo ""
    echo -e "Press any key to exit..."
    read -s -n 1
    exit 0 
}


localeValidation() {

    CURRENT_LC_TIME=$(locale | grep LC_TIME | cut -d= -f2 | tr -d '"')
    
    if [[ "$CURRENT_LC_TIME" != "en_US.UTF-8" && "$CURRENT_LC_TIME" != "C.UTF-8" && "$CURRENT_LC_TIME" != "POSIX" && "$CURRENT_LC_TIME" != "en_GB.UTF-8" ]]; then
        echo ""
        echo -e "\e[1;31m[ERROR]\e[0m Incompatible locale settings detected"
        echo -e "  Current LC_TIME: \e[1;37m$CURRENT_LC_TIME\e[0m"
        echo ""
        echo -e "  Compatible formats:"
        echo -e "    • en_US.UTF-8"
        echo -e "    • C.UTF-8"
        echo -e "    • POSIX"
        echo -e "    • en_GB.UTF-8"
        echo ""
        echo -e "  The script will now exit. Please update your locale settings."
        echo ""
        read -p "$(echo -e "  View instructions? \e[0;36m(y/n)\e[0m: ")" choice
        case "$choice" in
            [Yy])
                # Redirect to another script to change locale settings
                setLocalInstructions
                ;;
            [Nn])
                echo ""
                echo "Exiting."
                exit 0
                ;;
            *)
                echo ""
                echo -e "\e[1;31m[ERROR]\e[0m Invalid choice. Exiting."
                exit 0
                ;;
        esac
    else
        echo ""
        echo -e "\e[1;32m[OK]\e[0m Locale settings validated (\e[0;90m$CURRENT_LC_TIME\e[0m)"
    fi
}


function packageValidation(){
    
    # Function to check if a package is installed
    is_package_installed() {
        local package_name=$1
        local distro=$(grep -oP '(?<=^ID=).+' /etc/os-release | tr -d '"')
        
        if [[ $distro == "ubuntu" || $distro == "debian" ]]; then
            dpkg-query -W -f='${Status}' "$package_name" 2>/dev/null | grep -q "ok installed"
        else
            if rpm -q "$package_name" >/dev/null 2>&1; then
                return 0  # Package is installed
            else
                return 1  # Package is not installed
            fi
        fi
    }
    
    # Function to install a package using the package manager
    install_package() {
        local package_manager=$1
        local package_name=$2
        if [[ "$package_manager" == "apt-get" ]]; then
            apt-get update >/dev/null 2>&1
            apt-get install -y "$package_name" >/dev/null 2>&1
            elif [[ "$package_manager" == "zypper" ]]; then
            echo "Using zypper, please be patient.. .it may take a while"
            zypper --non-interactive install "$package_name" >/dev/null 2>&1
            elif [[ "$package_manager" == "yum" ]]; then
            yum -y install "$package_name" >/dev/null 2>&1
        else
            echo "Package manager not found. Cannot install $package_name."
            exit 1
        fi
    }
    
    # Check the distribution to determine the package manager and package names
    distro=$(grep -oP '(?<=^ID=).+' /etc/os-release | tr -d '"')
    
    case "$distro" in
        ubuntu|debian)
            package_manager="apt-get"
            sysstat_package_name="sysstat"
            iotop_package_name="iotop"
        ;;
        sles)
            package_manager="zypper"
            sysstat_package_name="sysstat"
            iotop_package_name="iotop"
        ;;
        rhel|centos|ol)
            package_manager="yum"
            sysstat_package_name="sysstat"
            iotop_package_name="iotop"
        ;;
        *)
            echo ""
            echo -e "\e[1;31m[ERROR]\e[0m Unsupported distribution: $distro"
            echo "Supported distributions: Ubuntu, Debian, RHEL, CentOS, Oracle Linux, SLES"
            exit 1
        ;;
    esac
    
    # Check if sysstat and iotop packaes are installed
    sysstat_installed=false
    iotop_installed=false
    
    echo ""
    echo -e "\e[1;37mChecking dependencies...\e[0m"
    
    if is_package_installed "$sysstat_package_name"; then
        sysstat_installed=true
        echo -e "  \e[1;32m✓\e[0m sysstat"
    else
        echo -e "  \e[1;31m✗\e[0m sysstat"
    fi
    
    if is_package_installed "$iotop_package_name"; then
        iotop_installed=true
        echo -e "  \e[1;32m✓\e[0m iotop"
    else
        echo -e "  \e[1;31m✗\e[0m iotop"
    fi
    
    # Prompt the user for installation
    if ! $sysstat_installed || ! $iotop_installed; then
        echo ""
        read -rp "$(echo -e "\e[1;33m[WARNING]\e[0m Missing dependencies. Install now? \e[0;36m(y/n)\e[0m: ")" choice
        if [[ $choice == [Yy] ]]; then
            echo ""
            if ! $sysstat_installed; then
                # Install the sysstat package
                echo -e "\e[1;36m→\e[0m Installing sysstat..."
                install_package "$package_manager" "$sysstat_package_name"
                echo -e "  \e[1;32m[OK]\e[0m sysstat installed"
            fi
            
            if ! $iotop_installed; then
                # Install the iotop package
                echo -e "\e[1;36m→\e[0m Installing iotop..."
                install_package "$package_manager" "$iotop_package_name"
                echo -e "  \e[1;32m[OK]\e[0m iotop installed"
            fi
        else
            echo ""
            echo -e "\e[1;31m[ERROR]\e[0m Required packages not installed. Exiting."
            exit 0
        fi
    else
        echo ""
        echo -e "\e[1;32m[OK]\e[0m All dependencies installed"
    fi
    displayMenu
}

function motd(){
    clear
    echo ""
    echo -e "\e[1;37mLinux All-in-One Performance Collector\e[0m"
    echo -e "\e[0;90mUnlocking advanced Linux metrics for humans\e[0m"
    echo -e "\e[0;36m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\e[0m"

    # Check if we should skip validations
    if [ "$skip_checks" == "OFF" ]; then
        # We always need to validate TZ first
        localeValidation

        # Validate Packages
        packageValidation
    else
        echo ""
        echo -e "\e[1;33m[WARNING]\e[0m Validation checks skipped"
        displayMenu
    fi

}

# Define the liveData function
function liveData() {
    # DATA CAPTURE STARTS HERE
    echo ""
    echo -e "\e[1;37mLive Data Capture\e[0m"
    echo -e "\e[0;36m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\e[0m"
    echo ""
    echo -e "Enter capture duration \e[0;90m(10-900 seconds)\e[0m"
    read -p "Duration: " duration
    
    if (( duration < 10 || duration > 900 )); then
        echo -e "\e[1;31m[ERROR]\e[0m Invalid duration. Must be between 10 and 900 seconds."
        exit 1
    fi

    # Record runmode
    runmode="Live Data Capture - $duration seconds"
    
    # Call the dataCapture function with the provided duration
    dataCapture $duration $high_res_disk_metrics
}
# Function to collect high granularity disk statistics
function collectDiskStats() {
    echo -e "\e[1;36m→\e[0m Starting high resolution disk monitoring..."
    local output_dir=$1
    local duration=$2
    local output_file="$output_dir/diskstats_log.txt"

    # Write the header line to the output file
    echo "Timestamp Major Minor Device Reads_Completed Reads_Merged Sectors_Read Time_Reading Writes_Completed Writes_Merged Sectors_Written Time_Writing IO_Currently IO_Time Weighted_IO_Time Discards_Completed Discards_Merged Sectors_Discarded Time_Discarding Flush_Requests Time_Flushing" > "$output_file"

    # Calculate end time
    local end_time=$((SECONDS + duration))

    # Collect data until duration expires
    while [ $SECONDS -lt $end_time ]; do
        cat /proc/diskstats | awk -v ts="$(date '+%Y-%m-%d-%H:%M:%S.%3N')" '
            $3 ~ /^sd[a-z]+$/ || $3 ~ /^nvme[0-9]+n[0-9]+$/ {print ts, $0}
        ' >> "$output_file"
        sleep 0.05
    done
    echo -e "\e[1;36m→\e[0m Stopping high resolution disk monitoring..."
}

function dataCapture() {
    local duration=$1
    local high_res_disk_metrics=$2

    # Inform the user about the collection and duration
    echo ""
    echo -e "\e[1;37mData Capture\e[0m \e[0;90m($duration seconds)\e[0m"
    echo -e "\e[0;36m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\e[0m"
    
    # Show if validation checks were skipped
    if [ "$skip_checks" == "ON" ]; then
        echo ""
        echo -e "\e[1;33m[WARNING]\e[0m Validation checks skipped"
    fi
    
    # Output Dir
    outputdir="$(hostname)_$(date +'%Y%m%d_%H%M%S')_linuxaioperfcheck"
    mkdir -p "$outputdir"

    # Ensure all files are created before appending contents
    touch $outputdir/info.txt $outputdir/date.txt $outputdir/df-h.txt $outputdir/free.txt $outputdir/iostat-data.out $outputdir/iotop.txt $outputdir/ls-l-dev-mapper.txt $outputdir/lsblk-f.txt $outputdir/lvdisplay.txt $outputdir/lvs.txt $outputdir/mpstat.txt $outputdir/os-release $outputdir/parted-l.txt $outputdir/pidstat.txt $outputdir/ps.txt $outputdir/pvdisplay.txt $outputdir/pvs.txt $outputdir/sar-load-avg.txt $outputdir/sarnetwork.txt $outputdir/top.txt $outputdir/uptime.txt $outputdir/vgdisplay.txt $outputdir/vgs.txt $outputdir/vmstat-data.out $outputdir/lshw.txt $outputdir/dmidecode.txt $outputdir/lsscsi.txt $outputdir/lscpu.txt $outputdir/meminfo.txt $outputdir/sysctl.txt $outputdir/lsmod.txt $outputdir/pidstat-io.txt $outputdir/pidstat-memory.txt $outputdir/sestatus.txt $outputdir/apparmor_status.txt

    # Log Hostname

    echo "Hostname:         $(hostname)" >> $outputdir/info.txt
    # Log Start Time
    echo "Start Time:       $(date)" >> $outputdir/info.txt

    # Calculate end time
    remaining_seconds=$duration
    
    # Function to check the last package update timestamp on Ubuntu
    check_ubuntu_last_update() {
        ls -lt --time=ctime /var/log/apt/history.log | awk 'NR==2 {print $6, $7, $8}' >> $outputdir/apt-history.txt
    }
    
    # Function to check the last package update timestamp on SLES
    check_sles_last_update() {
        rpm -qa --last | grep "package installed" | awk '{print $1, $2, $3}' >> $outputdir/zypper-history.txt
    }
    
    # Function to check the last package update timestamp on RHEL/CentOS
    check_rhel_last_update() {
        grep -oP "Installed: \K.*" /var/log/yum.log* 2>/dev/null | tail -1 >> $outputdir/yum-history.txt
        grep -oP "Installed: \K.*" /var/log/dnf.log* 2>/dev/null | tail -1 >> $outputdir/yum-history.txt
        echo "yum history" >> $outputdir/yum-history.txt
        yum history >> $outputdir/yum-history.txt
    }
    
    # Determine the Linux distribution
    distro=$(grep -oP '(?<=^ID=).+' /etc/os-release | tr -d '"')
    
    echo ""
    echo -e "\e[1;36m→\e[0m Gathering system information..."
    
    # Check the last package update timestamp based on the distribution (yes we need to check according to distro)
    case $distro in
        ubuntu|debian)
            check_ubuntu_last_update
        ;;
        sles)
            check_sles_last_update
        ;;
        rhel|centos)
            check_rhel_last_update
        ;;
        *)
            echo "Skipping checking for last package updates."
        ;;
    esac
    
    # General sysinfo
    cp /etc/os-release $outputdir/

    # Hardware Info
    lshw -short 2>/dev/null >> "$outputdir/lshw.txt"
    dmidecode >> "$outputdir/dmidecode.txt"


    # Storage info
    df -ha >> "$outputdir/df-h.txt"
    lsblk -f >> "$outputdir/lsblk-f.txt"
    parted --script -l 2>/dev/null >> "$outputdir/parted-l.txt"
    pvdisplay >> "$outputdir/pvdisplay.txt"
    vgdisplay >> "$outputdir/vgdisplay.txt"
    lvdisplay >> "$outputdir/lvdisplay.txt"
    pvs >> "$outputdir/pvs.txt"
    vgs >> "$outputdir/vgs.txt"
    lvs -a -o +devices,stripes,stripe_size,segtype >> "$outputdir/lvs.txt"
    ls -l /dev/mapper/* >> "$outputdir/ls-l-dev-mapper.txt"
    lsscsi 2>/dev/null >> "$outputdir/lsscsi.txt"

    # CPU and memory info
    lscpu >> "$outputdir/lscpu.txt"
    cat /proc/meminfo >> "$outputdir/meminfo.txt"
    
    # Kernel parameters and modules
    sysctl -a >> "$outputdir/sysctl.txt"
    lsmod >> "$outputdir/lsmod.txt"

    # SELinux or AppArmor status
    if command -v sestatus &> /dev/null; then
        sestatus >> "$outputdir/sestatus.txt"
    fi
    if command -v apparmor_status &> /dev/null; then
        apparmor_status >> "$outputdir/apparmor_status.txt"
    fi

    # High granularity Disk Usage Capture
    if [ "$high_res_disk_metrics" = "ON" ]; then
        collectDiskStats $outputdir $duration  &
    fi
    
    # Perf captures
    echo -e "\e[1;36m→\e[0m Initializing performance monitoring..."
    elapsed_seconds=1
    iostat -xk 1 | awk '// {print strftime("%Y-%m-%d-%H:%M:%S"),$0}' >> "$outputdir/iostat-data.out" &
    vmstat -a 1 | awk '// {print strftime("%Y-%m-%d-%H:%M:%S"),$0}' >> "$outputdir/vmstat-data.out" &
    iotop -obtd 1 >> "$outputdir/iotop.txt" &

    # mpstat, pidstat, and sar should be executed on a subshell
    (
        mpstat -P ALL 1 >> "$outputdir/mpstat.txt" &
        # Process stats per CPU
        pidstat -p ALL 1 >> "$outputdir/pidstat.txt" &
        # Process IO stats
        pidstat -d 1 >> "$outputdir/pidstat-io.txt" &
        # Process memory stats
        pidstat -r 1 >> "$outputdir/pidstat-memory.txt" &
        sar -n DEV 1 >> "$outputdir/sarnetwork.txt" &
        disown %1 %2 %3
    ) 2>/dev/null

    # Repeat cycle every second until end time is reached
    while [[ $remaining_seconds -gt 0 ]]; do
        
        if (( elapsed_seconds % 10 == 0 )); then
            echo -e "  \e[0;90mCollecting... ${elapsed_seconds}s / ${duration}s\e[0m"
        fi
        
        # Generic outputs
        echo "$(date)" >> "$outputdir/date.txt"
        uptime >> "$outputdir/uptime.txt"
        free -h >> "$outputdir/free.txt"
        top -b -n 1 >> "$outputdir/top.txt"
        ps H -eo user,pid,ppid,start_time,%cpu,%mem,wchan,cmd --sort=%cpu >> "$outputdir/ps.txt"
        sar -q 0 >> "$outputdir/sar-load-avg.txt"
        
        # Sleep for 1 second
        sleep 1
        ((remaining_seconds--))
        ((elapsed_seconds++))
        
    done
    
    pkill iostat
    pkill vmstat
    pkill mpstat
    pkill pidstat
    pkill sar
    pkill iotop

    # Log End Time
    echo "End Time:         $(date)" >> $outputdir/info.txt

    # Log runmode
    echo "Runtime Info:     $runmode" >> $outputdir/info.txt
    
    echo ""
    echo -e "\e[1;32m[OK]\e[0m Capture complete"
    createReport
}

function createReport() {
    echo -e "\e[1;36m→\e[0m Creating archive..."
    # Create the zip file
    zip_filename="$(hostname)_$(date +'%Y%m%d_%H%M%S')_linuxaioperfcheck.tar.gz"
    tar cfz "$zip_filename" "$outputdir"
    
    # Remove the output directory
    rm -rf "$outputdir"
    
    echo ""
    echo -e "\e[1;32m[OK]\e[0m Collection complete"
    echo ""
    echo -e "Output: \e[1;37m$(pwd)/$zip_filename\e[0m"
    echo ""
}

# Define the defineCron function
function defineCron() {
    echo ""
    echo -e "\e[1;37mCronjob Setup\e[0m"
    echo -e "\e[0;36m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\e[0m"
    echo ""
    read -rp "Run recurrently? (y/n): " choice
    
    if [[ "$choice" == [Yy] ]]; then
        echo ""
        read -rp "Hour interval (0-23): " hour
        read -rp "Minutes (0-60): " minutes
        read -rp "Capture duration (10-900 seconds): " duration
        
        if (( duration < 10 || duration > 900 )); then
            echo -e "\e[1;31m[ERROR]\e[0m Invalid duration. Must be between 10 and 900 seconds."
            exit 1
        fi
        
        # Add the cron job entry for recurrent run
        crontab -l > mycron
        echo "$minutes */$hour * * * $(pwd)/linux_aio_perfcheck.sh --collect-now --time $duration" >> mycron
        crontab mycron
        rm mycron
        echo ""
        echo -e "\e[1;32m[OK]\e[0m Cron job added"
        echo -e "  Schedule: \e[1;37m$minutes */$hour * * *\e[0m"
        echo -e "  Duration: \e[1;37m${duration}s\e[0m"
    else
        echo ""
        echo "Enter cron schedule \e[0;90m(format: minute hour day month day-of-week)\e[0m"
        echo "Example: 30 2 * * * \e[0;90m(runs daily at 2:30 AM)\e[0m"
        read -rp "Schedule: " cron_schedule
        
        read -rp "Capture duration (10-900 seconds): " duration
        if (( duration < 10 || duration > 900 )); then
            echo -e "\e[1;31m[ERROR]\e[0m Invalid duration. Must be between 10 and 900 seconds."
            exit 1
        fi
        
        # Add the cron job entry for non-recurrent run
        crontab -l > mycron
        echo "$cron_schedule $(pwd)/linux_aio_perfcheck.sh --collect-now --time $duration" >> mycron
        crontab mycron
        rm mycron
        echo ""
        echo -e "\e[1;32m[OK]\e[0m Cron job added"
        echo -e "  Schedule: \e[1;37m$cron_schedule\e[0m"
        echo -e "  Duration: \e[1;37m${duration}s\e[0m"
    fi
    
    # Restart the chronyd service
    echo -e "\e[1;36m→\e[0m Restarting cron service..."
    systemctl restart cron
    echo -e "\e[1;32m[OK]\e[0m Cron service restarted"
    echo ""
}

# ============================================================================
# Resource Watchdog Implementation
# ============================================================================

# PID file location
WATCHDOG_PID_FILE="/tmp/linuxaio_watchdog.pid"
WATCHDOG_LOG_DIR="/tmp/linuxaio_watchdog_logs"

# Setup Watchdog 
setupResourceWatchdog() {
    
    local monitor_cpu=0
    local monitor_mem=0
    local monitor_io=0
    local cpu_threshold=80
    local mem_threshold=80
    local io_threshold=80
    local duration=60

    echo ""
    echo -e "\e[1;37mResource Watchdog Mode\e[0m"
    echo -e "\e[0;36m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\e[0m"
    echo ""
    echo -e "  \e[1;32m1\e[0m  Auto   - CPU, memory, disk at 80% threshold (60s duration)"
    echo -e "  \e[1;32m2\e[0m  Manual - Choose resources and thresholds (1-300s duration)"
    echo ""
    read -p "Select mode (1 or 2): " mode


    if [[ "$mode" != "1" && "$mode" != "2" ]]; then
        echo -e "\e[1;31m[ERROR]\e[0m Invalid choice"
        exit 1
    fi

    if [ "$mode" == "2" ]; then
        echo ""
        echo -e "\e[1;37mManual Configuration\e[0m"
        echo ""
        
        read -p "Monitor CPU? (yes/no): " cpu_choice
        if [ "$cpu_choice" == "yes" ]; then
            monitor_cpu=1
            read -p "  CPU threshold (0-100): " cpu_threshold
        fi
        
        read -p "Monitor Memory? (yes/no): " mem_choice
        if [ "$mem_choice" == "yes" ]; then
            monitor_mem=1
            read -p "  Memory threshold (0-100): " mem_threshold
        fi
        
        read -p "Monitor Disk IO? (yes/no): " io_choice
        if [ "$io_choice" == "yes" ]; then
            monitor_io=1
            read -p "  Disk IO threshold (0-100): " io_threshold
        fi
    
        while true; do
            read -p "Capture duration (1-300 seconds): " duration
            if [[ "$duration" =~ ^[0-9]+$ ]]; then
                if [ "$duration" -ge 1 ] && [ "$duration" -le 300 ]; then
                    break
                else
                    echo -e "  \e[1;31m[ERROR]\e[0m Value must be between 1 and 300"
                fi
            else
                echo -e "  \e[1;31m[ERROR]\e[0m Please enter a valid number"
            fi
        done
        echo ""
    
    else
        monitor_cpu=1
        monitor_mem=1
        monitor_io=1
        cpu_threshold=80
        mem_threshold=80
        io_threshold=80
        duration=60
    fi

    # Start watchdog in background
    runResourceWatchdog "$monitor_cpu" "$monitor_mem" "$monitor_io" "$cpu_threshold" "$mem_threshold" "$io_threshold" "$duration" &
    
    # Wait a moment for the watchdog to write its PID
    sleep 0.5
    
    # Read the actual PID from the file (written by the watchdog itself)
    if [ -f "$WATCHDOG_PID_FILE" ]; then
        local watchdog_pid=$(cat "$WATCHDOG_PID_FILE")
        echo ""
        echo -e "\e[1;32m[OK]\e[0m Watchdog started in background"
        echo -e "  PID: \e[1;37m$watchdog_pid\e[0m"
        echo -e "  Log: \e[1;37m$WATCHDOG_LOG_DIR/watchdog_$watchdog_pid.log\e[0m"
        echo ""
        echo -e "To check status: \e[0;36m./$(basename $0) --watchdog-status\e[0m"
        echo -e "To stop:         \e[0;36m./$(basename $0) --watchdog-stop\e[0m"
        echo ""
    else
        echo ""
        echo -e "\e[1;31m[ERROR]\e[0m Failed to start watchdog"
        echo ""
    fi
}

runResourceWatchdog() {
    local monitor_cpu=$1
    local monitor_mem=$2
    local monitor_io=$3
    local cpu_threshold=$4
    local mem_threshold=$5
    local io_threshold=$6
    local duration=$7
    
    # Write our actual PID to the file (this is the real subprocess PID)
    echo "$$" > "$WATCHDOG_PID_FILE"
    
    # Setup logging
    mkdir -p "$WATCHDOG_LOG_DIR"
    local LOG_FILE="$WATCHDOG_LOG_DIR/watchdog_$$.log"
    local TEMP_IOSTAT="/tmp/linuxaio_iostat_$$.tmp"
    
    # Log startup
    echo "$(date '+%Y-%m-%d %H:%M:%S') [INFO] Watchdog started (PID: $$)" >> "$LOG_FILE"
    echo "$(date '+%Y-%m-%d %H:%M:%S') [INFO] Monitoring: CPU=$monitor_cpu MEM=$monitor_mem IO=$monitor_io" >> "$LOG_FILE"
    echo "$(date '+%Y-%m-%d %H:%M:%S') [INFO] Thresholds: CPU=${cpu_threshold}% MEM=${mem_threshold}% IO=${io_threshold}%" >> "$LOG_FILE"
    echo "$(date '+%Y-%m-%d %H:%M:%S') [INFO] Capture duration: ${duration}s" >> "$LOG_FILE"

    # Trap to cleanup on exit
    trap "rm -f '$TEMP_IOSTAT' '$WATCHDOG_PID_FILE'" EXIT SIGTERM SIGINT

    # Main monitoring loop
    while true; do
        local trigger=0
        local trigger_reason=""
        local cpu_util=0
        local mem_util=0
        local io_util=0

        # Check CPU
        if [ "$monitor_cpu" == "1" ]; then
            cpu_util=$(mpstat 1 1 2>/dev/null | awk '/Average:/ {printf "%.0f", 100 - $NF}')
            echo "$(date '+%Y-%m-%d %H:%M:%S') [METRIC] CPU: ${cpu_util}%" >> "$LOG_FILE"
            
            if [ -n "$cpu_util" ] && [ "$cpu_util" -gt "$cpu_threshold" ]; then
                trigger=1
                trigger_reason="CPU ${cpu_util}% > ${cpu_threshold}%"
            fi
        fi

        # Check Memory
        if [ "$monitor_mem" == "1" ]; then
            mem_util=$(free 2>/dev/null | awk '/Mem:/ {printf "%.0f", 100 - (($7 / $2) * 100)}')
            echo "$(date '+%Y-%m-%d %H:%M:%S') [METRIC] Memory: ${mem_util}%" >> "$LOG_FILE"
            
            if [ -n "$mem_util" ] && [ "$mem_util" -gt "$mem_threshold" ]; then
                trigger=1
                trigger_reason="${trigger_reason:+$trigger_reason, }Memory ${mem_util}% > ${mem_threshold}%"
            fi
        fi

        # Check Disk IO
        if [ "$monitor_io" == "1" ]; then
            iostat -d -x 1 2 2>/dev/null | grep -E '^(sd|nvme)' > "$TEMP_IOSTAT"
            
            if [ -s "$TEMP_IOSTAT" ]; then
                io_util=$(awk '{if ($NF > max) max = $NF} END {printf "%.0f", max}' "$TEMP_IOSTAT")
                echo "$(date '+%Y-%m-%d %H:%M:%S') [METRIC] Disk IO: ${io_util}%" >> "$LOG_FILE"
                
                if [ -n "$io_util" ] && [ "$io_util" -gt "$io_threshold" ]; then
                    trigger=1
                    trigger_reason="${trigger_reason:+$trigger_reason, }IO ${io_util}% > ${io_threshold}%"
                fi
            fi
        fi

        # Trigger collection if threshold exceeded
        if [ "$trigger" == "1" ]; then
            echo "$(date '+%Y-%m-%d %H:%M:%S') [TRIGGER] Threshold exceeded: $trigger_reason" >> "$LOG_FILE"
            echo "$(date '+%Y-%m-%d %H:%M:%S') [ACTION] Starting data collection (${duration}s)" >> "$LOG_FILE"
            
            # Set runmode for the collection
            runmode="Watchdog Triggered - $trigger_reason - $duration seconds"
            
            # Call dataCapture directly (no script spawning!)
            dataCapture "$duration" "$high_res_disk_metrics"
            
            echo "$(date '+%Y-%m-%d %H:%M:%S') [INFO] Collection complete" >> "$LOG_FILE"
            echo "$(date '+%Y-%m-%d %H:%M:%S') [INFO] Watchdog exiting (triggered)" >> "$LOG_FILE"
            
            # Clean up and exit
            rm -f "$TEMP_IOSTAT" "$WATCHDOG_PID_FILE"
            exit 0
        fi

        # Sleep before next check
        sleep 5
    done
}

# Check watchdog status
checkWatchdogStatus() {
    if [ ! -f "$WATCHDOG_PID_FILE" ]; then
        echo ""
        echo -e "\e[1;33m[INFO]\e[0m No watchdog is currently running"
        echo ""
        return 1
    fi
    
    local pid=$(cat "$WATCHDOG_PID_FILE")
    
    if ps -p "$pid" > /dev/null 2>&1; then
        echo ""
        echo -e "\e[1;32m[OK]\e[0m Watchdog is running"
        echo -e "  PID: \e[1;37m$pid\e[0m"
        
        # Show log file if it exists
        local log_file="$WATCHDOG_LOG_DIR/watchdog_${pid}.log"
        if [ -f "$log_file" ]; then
            echo -e "  Log: \e[1;37m$log_file\e[0m"
            echo ""
            echo "Recent activity:"
            tail -n 10 "$log_file" | while read line; do
                echo "  $line"
            done
        fi
        echo ""
        return 0
    else
        echo ""
        echo -e "\e[1;33m[WARNING]\e[0m Watchdog PID file exists but process is not running"
        echo "Cleaning up stale PID file..."
        rm -f "$WATCHDOG_PID_FILE"
        echo ""
        return 1
    fi
}

# Stop watchdog
stopWatchdog() {
    if [ ! -f "$WATCHDOG_PID_FILE" ]; then
        echo ""
        echo -e "\e[1;33m[INFO]\e[0m No watchdog is currently running"
        echo ""
        return 1
    fi
    
    local pid=$(cat "$WATCHDOG_PID_FILE")
    
    if ps -p "$pid" > /dev/null 2>&1; then
        echo ""
        echo -e "\e[1;36m→\e[0m Stopping watchdog (PID: $pid)..."
        kill "$pid" 2>/dev/null
        
        # Wait for process to terminate
        local count=0
        while ps -p "$pid" > /dev/null 2>&1 && [ $count -lt 10 ]; do
            sleep 0.5
            ((count++))
        done
        
        # Force kill if still running
        if ps -p "$pid" > /dev/null 2>&1; then
            kill -9 "$pid" 2>/dev/null
        fi
        
        rm -f "$WATCHDOG_PID_FILE"
        echo -e "\e[1;32m[OK]\e[0m Watchdog stopped"
        echo ""
        return 0
    else
        echo ""
        echo -e "\e[1;33m[WARNING]\e[0m Watchdog process not found"
        echo "Cleaning up stale PID file..."
        rm -f "$WATCHDOG_PID_FILE"
        echo ""
        return 1
    fi
}

# Function to display a disclaimer and get user's agreement
function displayDisclaimer() {
    echo ""
    echo -e "\e[1;33m[WARNING]\e[0m Resource watchdog will run in the background"
    echo ""
    echo "  • Monitors CPU, memory, and disk IO utilization"
    echo "  • Triggers data collection when thresholds are exceeded"
    echo "  • Runs as a separate background process"
    echo ""
    read -rp "Continue? (y/n): " choice
    if [[ "$choice" != [Yy] ]]; then
        echo -e "\e[1;31m[ERROR]\e[0m Operation cancelled"
        exit 0
    else
        setupResourceWatchdog
    fi
}

function toggleHighResDiskMetrics() {
    if [ "$high_res_disk_metrics" == "OFF" ]; then
        high_res_disk_metrics="ON"
    else
        high_res_disk_metrics="OFF"
    fi
    echo ""
    echo -e "\e[1;32m[OK]\e[0m High resolution disk metrics: \e[1;37m$high_res_disk_metrics\e[0m"
    echo ""
}

# Non-interactive validation for command-line mode
function validateNonInteractive() {
    # Run locale validation
    localeValidation
    
    # Run package validation
    echo ""
    echo -e "\e[1;37mChecking dependencies...\e[0m"
    
    # Determine package manager
    distro=$(grep -oP '(?<=^ID=).+' /etc/os-release | tr -d '"')
    case "$distro" in
        ubuntu|debian)
            package_manager="apt-get"
            sysstat_package_name="sysstat"
            iotop_package_name="iotop"
        ;;
        sles)
            package_manager="zypper"
            sysstat_package_name="sysstat"
            iotop_package_name="iotop"
        ;;
        rhel|centos|ol)
            package_manager="yum"
            sysstat_package_name="sysstat"
            iotop_package_name="iotop"
        ;;
        *)
            echo ""
            echo -e "\e[1;31m[ERROR]\e[0m Unsupported distribution: $distro"
            echo "Supported distributions: Ubuntu, Debian, RHEL, CentOS, Oracle Linux, SLES"
            echo ""
            echo "To bypass this check, use: --skip-checks"
            exit 1
        ;;
    esac
    
    # Function to check if a package is installed (inline version)
    check_pkg() {
        local pkg=$1
        if [[ $distro == "ubuntu" || $distro == "debian" ]]; then
            dpkg-query -W -f='${Status}' "$pkg" 2>/dev/null | grep -q "ok installed"
        else
            rpm -q "$pkg" >/dev/null 2>&1
        fi
    }
    
    missing_packages=()
    
    if check_pkg "$sysstat_package_name"; then
        echo -e "  \e[1;32m✓\e[0m sysstat"
    else
        echo -e "  \e[1;31m✗\e[0m sysstat"
        missing_packages+=("$sysstat_package_name")
    fi
    
    if check_pkg "$iotop_package_name"; then
        echo -e "  \e[1;32m✓\e[0m iotop"
    else
        echo -e "  \e[1;31m✗\e[0m iotop"
        missing_packages+=("$iotop_package_name")
    fi
    
    # If packages are missing, exit with error
    if [ ${#missing_packages[@]} -gt 0 ]; then
        echo ""
        echo -e "\e[1;31m[ERROR]\e[0m Missing required packages: ${missing_packages[*]}"
        echo "Please install them manually or run in interactive mode for installation prompts."
        exit 1
    fi
    
    echo ""
    echo -e "\e[1;32m[OK]\e[0m All dependencies installed"
}

function displayMenu(){
    # Menu for selecting run mode
    echo ""
    echo -e "\e[1;37mSelect Run Mode\e[0m"
    echo -e "\e[0;36m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\e[0m"
    echo ""
    echo -e "  \e[1;32m1\e[0m  Collect live data"
    echo -e "     \e[0;90mImmediate data collection\e[0m"
    echo ""
    echo -e "  \e[1;32m2\e[0m  Collect via watchdog"
    echo -e "     \e[0;90mTriggered by resource utilization threshold\e[0m"
    echo ""
    echo -e "  \e[1;32m3\e[0m  Collect via cron"
    echo -e "     \e[0;90mScheduled at specific time\e[0m"
    echo ""
    echo -e "  \e[1;32m4\e[0m  Toggle high resolution disk metrics"
    echo -e "     \e[0;90m50ms samples (live capture only) - Current: \e[1;37m$high_res_disk_metrics\e[0m"
    echo ""
    echo -e "  \e[1;31m0\e[0m  Exit"
    echo ""

    read -p "Select option (0-4): " run_mode
    
    case $run_mode in
        0)
            echo ""
            echo "Exiting..."
            exit 0
        ;;
        1)
            liveData
        ;;
        2)
            displayDisclaimer
        ;;
        3)
            defineCron
        ;;
        4)
            toggleHighResDiskMetrics
            clear
            motd  # Redisplay the menu after toggling
        ;;
        *)
            echo -e "\e[1;31m[ERROR]\e[0m Invalid option"
            exit 1
        ;;
    esac
}

COMMAND=""
DURATION=""
HIGH_RES="OFF"

while [[ $# -gt 0 ]]; do
    case $1 in
        --quick|--collect-now)
            COMMAND="$1"
            shift
            ;;
        -t|--time)
            DURATION="$2"
            shift 2
            ;;
        --time=*)
            DURATION="${1#*=}"
            shift
            ;;
        -hres)
            HIGH_RES="$2"
            shift 2
            ;;
        --high-resolution-disk-counters=*)
            HIGH_RES="${1#*=}"
            shift
            ;;
        --skip-checks)
            skip_checks="ON"
            shift
            ;;
        --watchdog-status)
            checkWatchdogStatus
            exit $?
            ;;
        --watchdog-stop)
            stopWatchdog
            exit $?
            ;;
        --cronjob)
            COMMAND="$1"
            if [ -n "$2" ]; then
                DURATION="$2"
                shift 2
            else
                echo ""
                echo -e "\e[1;31m[ERROR]\e[0m --cronjob requires a duration parameter"
                exit 1
            fi
            ;;
        --version)
            echo "Linux All-in-One Performance Collector, version 2.1.2"
            exit 0
            ;;
        -h|--help)
            print_usage
            exit 0
            ;;
        *)
            echo ""
            echo -e "\e[1;31m[ERROR]\e[0m Unknown option: $1"
            echo ""
            print_usage
            exit 1
            ;;
    esac
done

# Validate and execute commands
if [ -n "$COMMAND" ]; then
    case $COMMAND in
        --quick|--collect-now)
            # Validate duration
            if [ -z "$DURATION" ] || ! [[ "$DURATION" =~ ^[0-9]+$ ]] || [ "$DURATION" -lt 10 ] || [ "$DURATION" -gt 900 ]; then
                echo ""
                echo -e "\e[1;31m[ERROR]\e[0m Duration must be between 10 and 900 seconds"
                exit 1
            fi
            
            # Validate high resolution setting
            if [ "$HIGH_RES" != "ON" ] && [ "$HIGH_RES" != "OFF" ]; then
                echo ""
                echo -e "\e[1;31m[ERROR]\e[0m High resolution disk counters must be ON or OFF"
                exit 1
            fi
            
            # Set runmode based on command
            if [ "$COMMAND" == "--quick" ]; then
                runmode="Quick Data Capture - $DURATION seconds"
            else
                runmode="Interactive (Collect Now) Data Capture - $DURATION seconds"
            fi
            
            # Run validation checks unless --skip-checks is enabled
            if [ "$skip_checks" == "OFF" ]; then
                validateNonInteractive
            fi
            
            # Call dataCapture with validated parameters
            dataCapture "$DURATION" "$HIGH_RES"
            ;;
        --cronjob)
            # Set runmode for cronjob
            runmode="Cron Job Data Capture - $DURATION seconds"
            
            # Run validation checks unless --skip-checks is enabled
            if [ "$skip_checks" == "OFF" ]; then
                validateNonInteractive
            fi
            
            # Call dataCapture with duration
            dataCapture "$DURATION" "$HIGH_RES"
            ;;
    esac
else
    # Run interactive menu
    motd
fi
