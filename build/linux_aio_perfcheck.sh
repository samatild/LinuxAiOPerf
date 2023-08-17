#!/bin/bash

# Linux All-in-one Performance Collector
# Description:  shell script which collects performance data for analysis
# About: https://github.com/samatild/LinuxAiOPerf
# version: 1.3
# Date: 17/Aug/2023

clear
echo -e "\e[1;34m"
cat << "EOF"

 ================================
||      Linux All-in-One        ||
||   Performance Collector      ||
 ================================

* Unlocking advanced Linux metrics for humans *
EOF

echo -e "\e[1;33m"
cat << "EOF"
 --------------------
| Package Validation |
 --------------------
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
        echo "Using zypper, please be patient...it may take a while"
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
    rhel|centos)
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


# DATA CAPTURE STARTS HERE
echo -e "\e[1;33m"
cat << "EOF"
 --------------------
|    Data Capture    |
 --------------------
EOF

echo -e "\e[1mEnter the capture duration in seconds (\e[0m\e[1;31mminimum 10\e[0m\e[1m, \e[0m\e[1;32mmaximum 900\e[0m\e[1m)\e[0m"
read -p "Duration: " duration

if (( duration < 10 || duration > 900 )); then
    echo "Invalid duration. Please enter a value between 10 and 900."
    exit 1
fi
# Output Dir
outputdir="$(hostname)_$(date +'%Y%m%d_%H%M%S')_linuxaioperfcheck"
mkdir -p "$outputdir"

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
    grep -oP "Installed: \K.*" /var/log/yum.log | tail -1 >> $outputdir/yum-history.txt
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
df -h >> "$outputdir/df-h.txt"
lsblk -f >> "$outputdir/lsblk-f.txt"
parted -l 2>/dev/null >> "$outputdir/parted-l.txt"
pvdisplay >> "$outputdir/pvdisplay.txt"
vgdisplay >> "$outputdir/vgdisplay.txt" 
lvdisplay >> "$outputdir/lvdisplay.txt"
pvs >> "$outputdir/pvs.txt"
vgs >> "$outputdir/vgs.txt"
lvs >> "$outputdir/lvs.txt"
ls -l /dev/mapper/* >> "$outputdir/ls-l-dev-mapper.txt"

# Perf captures
echo "Initializing performance capture"
elapsed_seconds=1
iostat -xk 1 | awk '// {print strftime("%Y-%m-%d-%H:%M:%S"),$0}' >> "$outputdir/iostat-data.out" &
vmstat -a 1 | awk '// {print strftime("%Y-%m-%d-%H:%M:%S"),$0}' >> "$outputdir/vmstat-data.out" & 
mpstat -P ALL 1 >> "$outputdir/mpstat.txt" &
pidstat -p ALL 1 >> "$outputdir/pidstat.txt" &
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

echo -e "\e[1;33mCapture Complete.\e[0m"

echo -e "\e[1;33m"
cat << "EOF"
 --------------------
|  Report Creation   |
 --------------------
EOF

echo "Creating ZIP Package and cleaning the thrash."
# Create the zip file
zip_filename="$(hostname)_$(date +'%Y%m%d_%H%M%S')_linuxaioperfcheck.zip"
zip -r "$zip_filename" "$outputdir" >/dev/null 2>&1

# Remove the output directory
rm -rf "$outputdir"

echo -e "\e[1;34mScript execution completed.\e[0m"
echo -e "\e[1;34mOutput file:\e[0m \e[1;32m$(pwd)/$zip_filename\e[0m"