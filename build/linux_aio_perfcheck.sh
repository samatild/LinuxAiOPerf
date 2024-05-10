#!/bin/bash

# Linux All-in-one Performance Collector 
# Description:  shell script which collects performance data for analysis
# About: https://github.com/samatild/LinuxAiOPerf
# version: 1.33
# Date: 10/May/2024
     
runmode="null"

setLocalInstructions(){
    clear
    echo -e "\e[1;33m"
    cat << "EOF"
 ==================================================================
        Instructions on how to update local Time Zone settings 
 ==================================================================
EOF

    echo -e "\n\e[0;31m[Linux Generic procedure is]\e[0m"
    echo -e "\033[1;34m# Check what Language packages we have installed\e[0m"
    echo -e "locale -a\n"
    echo -e "\033[1;34m# Install if necesarry\e[0m"
    echo -e "localedef -i en_US -f UTF-8 en_US.UTF-8\n"
    echo -e "\033[1;34m# Change LC_TIME to en_US.UTF-8\e[0m"
    echo -e "localectl set-locale LC_TIME=en_US.UTF-8\n"
    echo -e "\033[1;34m# Exit your current user session, and re-login\e[0m"
    echo -e "\033[1;34m# We need to source new locale settings\e[0m\n"
    echo -e "\033[1;34m# You can revert using same command\e[0m"
    echo -e "localectl set-locale LC_TIME=<original value>\n"
    
    # Exit
    echo "Once you are done with Time Zone adjustments, re-run the Collector script."
    echo "Press any key to exit..."
    read -s -n 1
    exit 0 
}


localeValidation() {

    CURRENT_LC_TIME=$(locale | grep LC_TIME | cut -d= -f2 | tr -d '"')
    
    if [[ "$CURRENT_LC_TIME" != "en_US.UTF-8" && "$CURRENT_LC_TIME" != "C.UTF-8" && "$CURRENT_LC_TIME" != "POSIX" && "$CURRENT_LC_TIME" != "en_GB.UTF-8" ]]; then
        echo -e "\n\e[0;31mIncompatible Time Zone Settings!\e[0m"
        echo -e "\e[0;37mLC_TIME=$CURRENT_LC_TIME\e[0m"
        echo -e "\n\e[1;33mCompatible LC_TIME formats are: \e[0men_US.UTF-8 ; C.UTF-8 ; POSIX ; "
        echo -e "\nThe script will now exit. Please change local Time Zone settings manually and then return."
        read -p "Do you want to see an example on how to change Time Zone settings? (y/n): " choice
        case "$choice" in
            [Yy])
                # Redirect to another script to change locale settings
                setLocalInstructions
                ;;
            [Nn])
                echo "Quitting without printing the example."
                echo -e "\e[0m"
                exit 0
                ;;
            *)
                echo "Invalid choice. Quitting."
                echo -e "\e[0m"
                exit 0
                
                ;;
        esac
    else
        echo -e "\n\e[0;32mLocal Timezone settings are compatible.\e[0m: $CURRENT_LC_TIME"
    fi
}


function packageValidation(){

    echo -e "\e[1;33m"
    cat << "EOF"
 ======================
   Package Validation  
 ======================
EOF
   
    # Function to check if a package is installed
    is_package_installed() {
        local package_name=$1
        local distro=$(grep -oP '(?<=^ID=).+' /etc/os-release | tr -d '"')
        
        if [[ $distro == "ubuntu" ]]; then
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
        ubuntu)
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
            echo "Unsupported distribution: $distro"
            exit 1
        ;;
    esac
    
    # Check if sysstat and iotop packaes are installed
    sysstat_installed=false
    iotop_installed=false
    
    if is_package_installed "$sysstat_package_name"; then
        sysstat_installed=true
        echo -e "\e[0;37m[sysstat] \e[0;32mInstalled\e[0m"
    else
        echo -e "\e[0;37m[sysstat] \e[0;31mNot installed\e[0m"
    fi
    
    if is_package_installed "$iotop_package_name"; then
        iotop_installed=true
        echo -e "\e[0;37m[iotop] \e[0;32mInstalled\e[0m"
    else
        echo -e "\e[0;37m[iotop] \e[0;31mNot installed\e[0m"
    fi
    
    # Prompt the user for installation
    if ! $sysstat_installed || ! $iotop_installed; then
        echo -e "\e[0m"
        read -rp "Dependecies not met. Do you want to install them? (y/n): " choice
        if [[ $choice == [Yy] ]]; then
            if ! $sysstat_installed; then
                # Install the sysstat package
                echo "Installing sysstat package..."
                install_package "$package_manager" "$sysstat_package_name"
                echo "sysstat package installed successfully."
            fi
            
            if ! $iotop_installed; then
                # Install the iotop package
                echo "Installing iotop package..."
                install_package "$package_manager" "$iotop_package_name"
                echo "iotop package installed successfully."
            fi
        else
            echo "Packages not installed. Exiting..."
            exit 0
        fi
    else
        echo -e "\e[0;37m"
        echo -e "Dependencies met. \e[0;32mValidation passed.\e[0m"
    fi
    displayMenu
}

function motd(){
    clear
    echo -e "\e[1;34m"
    cat << "EOF"

===============================
      Linux All-in-One        
   Performance Collector      
===============================
* Unlocking advanced Linux metrics for humans *
EOF

    # We always need to validate TZ first
    localeValidation

    # Validate Packages
    packageValidation

}

# Define the liveData function
function liveData() {
    # DATA CAPTURE STARTS HERE
    echo -e "\e[1;33m"
    cat << "EOF"
 =======================
    Live Data Capture  
 =======================
EOF
    
    echo -e "\e[1mEnter the capture duration in seconds (\e[0m\e[1;31mminimum 10\e[0m\e[1m, \e[0m\e[1;32mmaximum 900\e[0m\e[1m)\e[0m"
    read -p "Duration: " duration
    
    if (( duration < 10 || duration > 900 )); then
        echo "Invalid duration. Please enter a value between 10 and 900."
        exit 1
    fi

    # Record runmode
    runmode="Live Data Capture - $duration seconds"
    
    # Call the dataCapture function with the provided duration
    dataCapture $duration
}

function dataCapture() {
    local duration=$1
    # Inform the user about the collection and duration
    echo "Starting data capture for $duration seconds..."
    
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
    echo -e "\e[1;33mStarting\e[0m"
    
    echo "Gathering general system information (...)"
    
    # Check the last package update timestamp based on the distribution (yes we need to check according to distro)
    case $distro in
        ubuntu)
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

    # Hardware info
    lshw -short >> "$outputdir/lshw.txt"
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
    lsscsi >> "$outputdir/lsscsi.txt"

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


    # Perf captures
    echo "Initializing performance capture"
    elapsed_seconds=1
    iostat -xk 1 | awk '// {print strftime("%Y-%m-%d-%H:%M:%S"),$0}' >> "$outputdir/iostat-data.out" &
    vmstat -a 1 | awk '// {print strftime("%Y-%m-%d-%H:%M:%S"),$0}' >> "$outputdir/vmstat-data.out" &
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
            echo "Elapsed Time / Total: $elapsed_seconds / $duration (seconds)"
        fi
        
        # Generic outputs
        echo "$(date)" >> "$outputdir/date.txt"
        uptime >> "$outputdir/uptime.txt"
        free -h >> "$outputdir/free.txt"
        top -b -n 1 >> "$outputdir/top.txt"
        ps H -eo user,pid,ppid,start_time,%cpu,%mem,wchan,cmd --sort=%cpu >> "$outputdir/ps.txt"
        sar -q 0 >> "$outputdir/sar-load-avg.txt"
        # iotop output (we log data because iotop doesn't keep a timestamp)
        date >> "$outputdir/iotop.txt"
        iotop -b -n 1 >> "$outputdir/iotop.txt"
        
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

    # Log End Time
    echo "End Time:         $(date)" >> $outputdir/info.txt

    # Log runmode
    echo "Runtime Info:     $runmode" >> $outputdir/info.txt
    
    echo -e "\e[1;33mCapture Complete.\e[0m"
    createReport
}

function createReport() {
    echo -e "\e[1;33m"
    cat << "EOF"
 =====================
    Report Creation  
 =====================
EOF
    
    echo "Creating tarball and cleaning the trash."
    # Create the zip file
    zip_filename="$(hostname)_$(date +'%Y%m%d_%H%M%S')_linuxaioperfcheck.tar.gz"
    tar cfz "$zip_filename" "$outputdir"
    
    # Remove the output directory
    rm -rf "$outputdir"
    
    echo -e "\e[1;34mScript execution completed.\e[0m"
    echo -e "\e[1;34mOutput file:\e[0m \e[1;32m$(pwd)/$zip_filename\e[0m"
}

# Define the defineCron function
function defineCron() {
    echo -e "\033[1;34m=====================================================================\033[0m"
    echo -e "\033[1;32m[Cronjob Setup]\033[0m"
    echo -e "\033[1;34m=====================================================================\033[0m"
    echo "Do you want the job to run recurrently? (y/n): "
    read -r choice
    
    if [[ "$choice" == [Yy] ]]; then
        echo "Enter the hour - Every (0-23) hours: "
        read -r hour
        echo "and (0-60) Minutes: "
        read -r minutes
        
        # Ask for the duration of the capture
        echo "Enter the duration of the capture in seconds (between 10 and 900): "
        read -r duration
        if (( duration < 10 || duration > 900 )); then
            echo "Invalid duration. Please enter a value between 10 and 900."
            exit 1
        fi
        
        # Add the cron job entry for recurrent run
        crontab -l > mycron
        echo "$minutes */$hour * * * $(pwd)/linux_aio_perfcheck.sh --collect-now $duration" >> mycron
        crontab mycron
        rm mycron
        echo "Cron job added: $minutes */$hour * * * $(pwd)/linux_aio_perfcheck.sh --collect-now $duration"
    else
        echo "Enter the exact cron schedule."
        echo "The schedule consists of five fields: minute hour day month day-of-week"
        echo "For example, to run every day at 2:30 AM, enter: 30 2 * * *"
        read -r cron_schedule
        
        # Ask for the duration of the capture
        echo "Enter the duration of the capture in seconds (between 10 and 900): "
        read -r duration
        if (( duration < 10 || duration > 900 )); then
            echo "Invalid duration. Please enter a value between 10 and 900."
            exit 1
        fi
        
        # Add the cron job entry for non-recurrent run
        crontab -l > mycron
        echo "$cron_schedule $(pwd)/linux_aio_perfcheck.sh --cronjob $duration" >> mycron
        crontab mycron
        rm mycron
        echo "Cron job added: $cron_schedule $(pwd)/linux_aio_perfcheck.sh --cronjob $duration"
    fi
    
    # Restart the chronyd service
    echo "Restarting chronyd service..."
    systemctl restart chronyd
    echo "chronyd service restarted."
}

# Setup Watchdog 
setupResourceWatchdog() {
    
    local monitor_cpu=0
    local monitor_mem=0
    local monitor_io=0
    local cpu_threshold=80
    local mem_threshold=80
    local io_threshold=80
    local duration=60

    echo -e "\033[1;34m=====================================================================\033[0m"
    echo -e "\033[1;32mChoose a mode for the Resource Watchdog:\033[0m"
    echo -e "\033[1;34m=====================================================================\033[0m"
    echo -e "\033[1;36m1 - Auto   \033[0m: Monitor CPU, memory, and disk at 80% Threshold. Duration: 60sec"
    echo -e "\033[1;36m2 - Manual \033[0m: Choose resources and Thresholds. Duration: 1-300sec"
    echo -e "\033[1;34m=====================================================================\033[0m"
    read -p "$(echo -e "\033[1;33mEnter 1 or 2: \033[0m")" mode


    if [[ "$mode" != "1" && "$mode" != "2" ]]; then
        echo "Invalid choice. Exiting."
        exit 1
    fi

    if [ "$mode" == "2" ]; then
        echo -e "\033[1;34m============================================\033[0m"
        echo -e "\033[1;32mResource Monitoring Choices:\033[0m"
        echo -e "\033[1;34m============================================\033[0m"
        
        read -p "$(echo -e "\033[1;36mMonitor CPU? (yes/no):\033[0m ")" cpu_choice
        
        if [ "$cpu_choice" == "yes" ]; then
            monitor_cpu=1
            read -p "$(echo -e "\033[1;33mSet CPU threshold (0-100):\033[0m ")" cpu_threshold
        fi
        
        read -p "$(echo -e "\033[1;36mMonitor Memory? (yes/no):\033[0m ")" mem_choice
        
        if [ "$mem_choice" == "yes" ]; then
            monitor_mem=1
            read -p "$(echo -e "\033[1;33mSet Memory threshold (0-100):\033[0m ")" mem_threshold
        fi
        
        read -p "$(echo -e "\033[1;36mMonitor Disk IO? (yes/no):\033[0m ")" io_choice
        
        if [ "$io_choice" == "yes" ]; then
            monitor_io=1
            read -p "$(echo -e "\033[1;33mSet Disk IO threshold (0-100):\033[0m ")" io_threshold
        fi
    
        while true; do
            read -p "$(echo -e "\033[1;36mDuration (1-300sec): \033[0m ")" duration

            # Check if the input is an integer
            if [[ "$duration" =~ ^[0-9]+$ ]]; then
                # Check if the input is between 0 and 300
                if [ "$duration" -ge 1 ] && [ "$duration" -le 300 ]; then
                break
                else
                echo -e "\033[1;31mInvalid input: Please enter a value between 1 and 300.\033[0m"
                fi
            else
                echo -e "\033[1;31mInvalid input: Please enter an integer.\033[0m"
            fi
        done
        
        echo -e "\033[1;34m============================================\033[0m"
    
    else
        monitor_cpu=1
        monitor_mem=1
        monitor_io=1
        cpu_threshold=80
        mem_threshold=80
        io_threshold=80
        duration=60
    fi

    $(pwd)/linux_aio_perfcheck.sh --watchdog "$monitor_cpu" "$monitor_mem" "$monitor_io" "$cpu_threshold" "$mem_threshold" "$io_threshold" "$duration" &
    
}

runResourceWatchdog() {

    local monitor_cpu=$1
    local monitor_mem=$2
    local monitor_io=$3
    local cpu_threshold=$4
    local mem_threshold=$5
    local io_threshold=$6
    local duration=$7
    local LOG_FILE=$(pwd)/LinuxAiO_watchdog_$(date +'%Y%m%d_%H%M%S').log
    local start_time=$(date +%s)
    local reset_interval=3600 # 1 Hour
  
    echo -e "\033[1;34mResource watchdog started. \033[1;32mPID: $$\033[0m"

    while true; do
        local highIO=0
        local cpu_util=0
        local mem_util=0

        if [ "$monitor_cpu" == "1" ]; then
            cpu_util=$(mpstat 1 1 | awk '/Average:/ {print 100 - $NF}')
            echo "$(date '+%Y-%m-%d %H:%M:%S ')Current CPU Utilization: $cpu_util%" >> "$LOG_FILE"
        fi

        if [ "$monitor_mem" == "1" ]; then
            mem_util=$(free | awk '/Mem:/ {print 100 -(($7 / $2) * 100)}')
            echo "$(date '+%Y-%m-%d %H:%M:%S ')Current Memory Utilization: $mem_util%" >> "$LOG_FILE"
        fi

        if [ "$monitor_io" == "1" ]; then
            iostat -d -x 1 2 | grep -v Device | grep -v cpu | grep -v CPU > .iostat.txt
            if [ -f .iostat.txt ]; then
                while read -r line; do
                    if [[ -n "$line" ]]; then
                        local last_column=$(echo "$line" | awk '{print $NF}')
                        if (( $(echo "$last_column > $io_threshold" | bc -l) )); then
                            highIO=1
                            break
                        fi
                    fi
                done < .iostat.txt
            fi
            rm -f .iostat.txt
        fi

        if (( $(echo "$cpu_util > $cpu_threshold" | bc -l) == 1 || $(echo "$mem_util > $mem_threshold" | bc -l) == 1 || $highIO == 1 )); then
            echo "$(date '+%Y-%m-%d %H:%M:%S ')Resource utilization above thresholds. Running Collector" >> "$LOG_FILE"
            $(pwd)/linux_aio_perfcheck.sh --runwatchdog $duration $monitor_cpu $monitor_mem $monitor_io $cpu_threshold $mem_threshold $io_threshold
            exit 1
        fi
        
        # Check if 1 hour has passed
        local current_time=$(date +%s)
        local elapsed_time=$((current_time - start_time))

        if [ $elapsed_time -ge $reset_interval ]; then
            echo "$(date '+%Y-%m-%d %H:%M:%S ')One hour has passed. Exiting." >> $LOG_FILE
            $(pwd)/linux_aio_perfcheck.sh --watchdog "$monitor_cpu" "$monitor_mem" "$monitor_io" "$cpu_threshold" "$mem_threshold" "$io_threshold" "$duration" &    
            find . -maxdepth 1 -type f -name "LinuxAiO_watchdog_*.log" -mmin +121 -exec rm -f {} \;
            exit 0
        fi

        sleep 5
    done
}

# Function to display a disclaimer and get user's agreement
function displayDisclaimer() {
    echo -e "\e[1;33m"
    echo "WARNING: Setting up a resource watchdog will run a separate process in the background."
    echo "This process will monitor CPU, memory, and disk IO utilization."
    echo -e "Do you agree to continue? (y/n) \e[0m"
    read -r choice
    if [[ "$choice" != [Yy] ]]; then
        echo "Aborted. Exiting..."
        exit 0
    else
        setupResourceWatchdog
    fi
}

function displayMenu(){
    # Menu for selecting run mode
    echo -e "\e[1;33m"
    cat << "EOF"
=====================
   Select Run Mode  
=====================
EOF
    
    echo -e "\033[1;34m===================================================================================\033[0m"
    echo -e "\033[1;32m1 - Collect live data            \e[1;31m(Now)"
    echo -e "\033[1;32m2 - Collect data via watchdog    \e[1;31m(Triggered by High CPU, Memory, or Disk IO)"
    echo -e "\033[1;32m3 - Collect data via cron        \e[1;31m(At a specific time)"
    echo -e "\033[1;34m===================================================================================\033[0m"
    echo ""

    read -p "$(echo -e "\033[1;36mEnter the mode number: \033[0m ")" run_mode
    
    case $run_mode in
        1)
            liveData
        ;;
        2)
            displayDisclaimer
        ;;
        3)
            
            defineCron
        ;;
        *)
            echo "Invalid mode number."
            exit 1
        ;;
    esac
    
}

# Check for command-line arguments
if [ "$1" = "--collect-now" ]; then
    if [ -n "$2" ] && [[ "$2" =~ ^[0-9]+$ ]]; then
        # Call dataCapture function with the specified duration
        dataCapture "$2"
    else
        echo "Usage: $0 --collect-now <duration in seconds>"
        exit 1
    fi
elif [ "$1" = "--watchdog" ]; then
    if [ $# -eq 8 ]; then
        runResourceWatchdog "$2" "$3" "$4" "$5" "$6" "$7" "$8" "$9"
    else
        echo "Usage: $0 --watchdog <monitor_cpu> <monitor_mem> <monitor_io> <cpu_threshold> <mem_threshold> <io_threshold>"
        exit 1
    fi
elif [ "$1" = "--runwatchdog" ]; then
    # Record runmode
    runmode="Watchdog Data Capture - $2 seconds Monitor_CPU=$3 Monitor_Memory=$4 Monitor_IO=$5 CPU_Threshold=$6 Mem_Threshold=$7 IO_Threshold=$8"
    # Call dataCapture function with the specified duration
    dataCapture "$2"
elif [ "$1" = "--cronjob" ]; then
    # Record runmode
    runmode="Cronjob Data Capture - $2 seconds"
    # Call dataCapture function with the specified duration
    dataCapture "$2"
elif [ "$1" = "--version" ]; then
    echo "Linux All-in-One Performance Collector, version 1.32"
else
    motd
fi
