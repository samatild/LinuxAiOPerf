#!/bin/bash

# Linux All-in-one Performance checker [without netowork]
# Description:  shell script which collects performance data for analysis
# Author: samatild
# Date: 26/07/2023

echo "[Linux AIO Perfomance Checker]"

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

# Check the distribution to determine the package manager and package name
distro=$(grep -oP '(?<=^ID=).+' /etc/os-release | tr -d '"')

case "$distro" in
    ubuntu)
        package_manager="apt-get"
        package_name="sysstat"
        ;;
    sles)
        package_manager="zypper"
        package_name="sysstat"
        ;;
    rhel|centos)
        package_manager="yum"
        package_name="sysstat"
        ;;
    *)
        echo "Unsupported distribution: $distro"
        exit 1
        ;;
esac


# Check if sysstat package is installed
if is_package_installed "$package_name"; then
    echo "[sysstat package is installed]"
else
    # Prompt the user for installation
    read -rp "sysstat package is not installed. Do you want to install it? (y/n): " choice
    if [[ $choice == [Yy] ]]; then
        # Install the package
        echo "Installing sysstat package..."
        install_package "$package_manager" "$package_name"
        echo "sysstat package installed successfully."
    else
        echo "sysstat package not installed. Exiting..."
        exit 0
    fi
fi



# Prompt for duration in seconds
read -p "Enter the capture duration in seconds (minimum 10, maximum 900): " duration

# Validate duration input
if (( duration < 10 || duration > 900 )); then
    echo "Invalid duration. Please enter a value between 10 and 900."
    exit 1
fi
# Create output directory
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

echo "Logging which packages were last updated (...)"
# Check the last package update timestamp based on the distribution
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
echo "Gathering general system information (...)"
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
    
    
    
    # IO and vmstat info
    sar -q 0 >> "$outputdir/sar-load-avg.txt"
    #iostat -xk 1 | awk '// {print strftime("%Y-%m-%d-%H:%M:%S"),$0}' >> "$outputdir/iostat-data.out"
    #vmstat -a 1 | awk '// {print strftime("%Y-%m-%d-%H:%M:%S"),$0}' >> "$outputdir/vmstat-data.out"
    #mpstat -P ALL 1 >> "$outputdir/mpstat.txt"

    # iotop output
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


echo "Complete. Creating ZIP Package and cleaning the thrash."
# Create the zip file with hostname, date, time, and description
zip_filename="$(hostname)_$(date +'%Y%m%d_%H%M%S')_linuxaioperfcheck.zip"
zip -r "$zip_filename" "$outputdir"

# Remove the output directory
rm -rf "$outputdir"

echo "Script execution completed. Output file: $(pwd)/$zip_filename"