import os
import datetime
import json
from ..procinfo.pidstat.pidstatcpu import (
    print_file_contents,
    pidstat_extract_header_line,
    generate_pidstat
)
from ..procperf.cpu.top_consumers import extract_top_cpu_consumers
from ..procperf.io.top_consumers import extract_top_io_consumers
from ..procperf.memory.top_consumers import extract_top_mem_consumers
import plotly.graph_objects as go

from ..procinfo.pidstat.pidstatio import (
    pidstatio_extract_header_line,
    generate_pidstatio
)

from ..procinfo.pidstat.pidstatmem import (
    pidstatmem_extract_header_line,
    generate_pidstatmem
)

from ..procinfo.top.topcmd import (
    generate_top
)

from ..procinfo.iotop.iotopcmd import (
    generate_iotop
)

from ..sysconfig.lvm.lvmviz import (
    parse_pvs,
    parse_vgs,
    parse_lvs,
    create_graph
)

script_version = "2.1.3"


def log_message(message, log_level='Info'):
    current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"{current_time}: [{log_level}] [generate_html.py] {message}")


def generate_report(
    mpstat_figs,
    iostatPD_figs,
    iostatPM_figs,
    vmstat_figs,
    sarnet_figs,
    diskstats_figs,
    output_filename='linuxaioperf_report.html'
):

    # Do not change, this are links to flask static files
    static_url = "/static/report_style.css"
    js_static_url = "/static/script_report.js"
    template_path = os.path.join(os.path.dirname(__file__), "template.html")

    # Assign the template content to a variable
    with open(template_path, 'r') as f:
        content = f.read()

    rp = ""
    rp += f"""<link rel="stylesheet" type="text/css" href="{static_url}">"""

    content = content.replace(
        "<!-- header.script1_placeholder -->",
        rp)

    rp = ""
    rp += f"""<script src="{js_static_url}" type="text/javascript"></script>"""

    content = content.replace(
        "<!-- header.script2_placeholder -->",
        rp)

    if os.stat("lvs.txt").st_size != 0:
        rp = """
                    <div class="subtab" onclick="event.stopPropagation();
                    openTab(event, 'subcontent-lvmdisplay')">LVM Layout</div>
                    """
        # Replace the placeholder with the code snippet
        content = content.replace(
            "<!-- lvm_tab_placeholder -->",
            rp)

    # System Configuration
    log_message("Generating System Overview")

    # System Configuration - Information
    # Check if the file "info.txt" exists
    if os.path.exists("info.txt"):
        # Execute the code only if the file exists
        with open("info.txt", "r") as file:
            runtimeinfo = file.read()

        rp = ""
        rp += f"""
            <h2>Runtime Information</h2>
            <div class="console-output">
                {runtimeinfo}
            </div> """

        content = content.replace(
            "<!-- sysinfo.runtime_placeholder -->",
            rp)

    rp = ""
    rp += """
                <h2>os-release</h2>
            <div class="console-output">
            """
    osrelease = print_file_contents("os-release")
    rp += osrelease
    rp += """</div>"""

    content = content.replace(
        "<!-- sysinfo.osinfo_placeholder -->",
        rp)

    # System Configuration - Hardware
    rp = ""
    rp += """
            <h2>lshw</h2>
            <div class="console-output">
            """
    lshw = print_file_contents("lshw.txt")
    rp += lshw
    rp += """</div>"""

    content = content.replace(
        "<!-- sysinfo.lshw_placeholder -->",
        rp)

    rp = ""
    rp += """
            <h2>dmidecode</h2>
            <div class="console-output">
            """
    dmidecode = print_file_contents("dmidecode.txt")
    rp += dmidecode
    rp += """</div>"""

    content = content.replace(
        "<!-- sysinfo.dmidecode_placeholder -->",
        rp)

    # System Configuration - Storage
    rp = ""
    rp += """
            <h2>lssci</h2>
            <div class="console-output">
            """
    lssci = print_file_contents("lsscsi.txt")
    rp += lssci
    rp += """</div>"""

    content = content.replace(
        "<!-- sysinfo.lssci_placeholder -->",
        rp)

    rp = ""
    rp += """
            <h2>lsblk -f</h2>
            <div class="console-output">
            """
    lsblk = print_file_contents("lsblk-f.txt")
    rp += lsblk
    rp += """</div>"""

    content = content.replace(
        "<!-- sysinfo.lsblk_placeholder -->",
        rp)

    rp = ""
    rp += """
            <h2>df -h</h2>
            <div class="console-output">
            """
    dfh = print_file_contents("df-h.txt")
    rp += dfh
    rp += """</div>"""

    content = content.replace(
        "<!-- sysinfo.df_placeholder -->",
        rp)

    rp = ""
    rp += """
            <h2>ls -l dev mapper</h2>
            <div class="console-output">
            """
    lsldevmapper = print_file_contents("ls-l-dev-mapper.txt")
    rp += lsldevmapper
    rp += """</div>"""

    content = content.replace(
        "<!-- sysinfo.lsdevmapper_placeholder -->",
        rp)

    rp = ""
    rp += """
            <h2>parted -l</h2>
            <div class="console-output">
            """
    partedl = print_file_contents("parted-l.txt")
    rp += partedl
    rp += """</div>"""

    # System Configuration - LVM
    if os.stat("lvs.txt").st_size != 0:
        rp = ""
        rp += """
            <div class="tab-content" id="subcontent-lvmdisplay">
            """
        pvs = parse_pvs()
        vgs = parse_vgs()
        lvs = parse_lvs()
        svg_contents = create_graph(pvs, vgs, lvs)

        for svg_content in svg_contents:
            rp += (
                f'<div style="text-align: center;">{svg_content}</div>'
                f'<hr style="border: 0.5px solid #666;">'
            )

        rp += """
                <h2>pvs</h2>
                <div class="console-output">
                """
        pvs = print_file_contents("pvs.txt")
        rp += pvs
        rp += """</div>"""
        rp += """
                <h2>vgs</h2>
                <div class="console-output">
                """
        vgs = print_file_contents("vgs.txt")
        rp += vgs
        rp += """</div>"""
        rp += """
                <h2>lvs</h2>
                <div class="console-output">
                """
        lvs = print_file_contents("lvs.txt")
        rp += lvs
        rp += """</div>"""
        rp += """
                <h2>pvdisplay</h2>
                <div class="console-output">
                """
        pvdisplay = print_file_contents("pvdisplay.txt")
        rp += pvdisplay
        rp += """</div>"""
        rp += """
                <h2>vgdisplay</h2>
                <div class="console-output">
                """
        vgdisplay = print_file_contents("vgdisplay.txt")
        rp += vgdisplay
        rp += """</div>"""
        rp += """
                <h2>lvdisplay</h2>
                <div class="console-output">
                """
        lvdisplay = print_file_contents("lvdisplay.txt")
        rp += lvdisplay
        rp += """</div>"""
        rp += """</div>"""

        content = content.replace(
            "<!-- sysinfo.lvm_placeholder -->",
            rp)

    # System Configuration - CPU Info
    rp = ""
    rp += """
            <h2>CPU Information</h2>
            <div class="console-output">
            """
    lscpu = print_file_contents("lscpu.txt")
    rp += lscpu
    rp += """</div>"""

    content = content.replace(
        "<!-- sysinfo.cpuinfo_placeholder -->",
        rp)

    # System Configuration - Memory Info
    rp = ""
    rp += """
            <h2>Memory Information</h2>
            <div class="console-output">
            """
    meminfo = print_file_contents("meminfo.txt")
    rp += meminfo
    rp += """</div>"""

    content = content.replace(
        "<!-- sysinfo.meminfo_placeholder -->",
        rp)

    # System Configuration - Kernel Parameters
    rp = ""
    rp += """
            <h2>Kernel Parameters</h2>
            <div class="console-output">
            """
    kernelparam = print_file_contents("sysctl.txt")
    rp += kernelparam
    rp += """</div>"""

    content = content.replace(
        "<!-- sysinfo.sysctl_placeholder -->",
        rp)

    # System Configuration - Kernel Modules
    rp = ""
    rp += """
            <h2>Kernel Modules</h2>
            <div class="console-output">
            """
    kernelmod = print_file_contents("lsmod.txt")
    rp += kernelmod
    rp += """</div>"""

    content = content.replace(
        "<!-- sysinfo.lsmod_placeholder -->",
        rp)

    # System Configuration - Security
    rp = ""

    if os.stat("apparmor_status.txt").st_size != 0:
        rp += """
            <h2>apparmor Status</h2>
            <div class="console-output">
            """
        apparmor = print_file_contents("apparmor_status.txt")
        rp += apparmor
        rp += """</div>"""
        content = content.replace(
            "<!-- sysinfo.apparmor_placeholder -->",
            rp)
    elif os.stat("sestatus.txt").st_size != 0:
        rp += """
            <h2>SELinux Status</h2>
            <div class="console-output">
            """
        sestatus = print_file_contents("sestatus.txt")
        rp += sestatus
        rp += """</div>"""
        content = content.replace(
            "<!-- sysinfo.selinux_placeholder -->",
            rp)

    # High Resolution Disk Stats Section
    log_message("Generating Performance Report - High Resolution Disk Metrics")
    rp = ""

    if len(diskstats_figs) > 0:
        for fig in diskstats_figs:
            div = fig.to_html(full_html=False, include_plotlyjs='cdn')
            rp += f'<div id="plotlyGraphDiskstats">{div}</div>'
    else:
        rp = '<style>#tab4, [onclick*="tab4"] { display: none; }</style>'

    content = content.replace(
        "<!-- perf.diskstats_placeholder -->",
        rp)

    # Performance Analysis - CPU Load Distribution
    log_message("Generating Performance Report 1/5 - CPU")
    rp = ""

    for figx in mpstat_figs:
        div = figx.to_html(full_html=False, include_plotlyjs='cdn')
        rp += f'<div id="plotlyGraphmpstat">{div}</div>'

    content = content.replace(
        "<!-- perf.mpstat_placeholder -->",
        rp)

    # Performance Analysis - Memory Utilization
    log_message("Generating Performance Report 2/5 - Memory")
    rp = ""

    for figu in vmstat_figs:
        div = figu.to_html(full_html=False, include_plotlyjs='cdn')
        rp += f'<div id="plotlyGraphmpstat">{div}</div>'

    content = content.replace(
        "<!-- perf.memory_placeholder -->",
        rp)

    # Performance Analysis - Disk Metrics/Device
    log_message("Generating Performance Report 3/5 - Disk Metrics/Device")
    rp = ""

    for figy in iostatPD_figs:
        div = figy.to_html(full_html=False, include_plotlyjs='cdn')
        rp += f'<div id="plotlyGraphiostatPD">{div}</div>'

    content = content.replace(
        "<!-- perf.iostatpd_placeholder -->",
        rp)

    # Performance Analysis - Disk Device/metrics
    log_message("Generating Performance Report 4/5 - Disk Device/metrics")
    rp = ""

    for figz in iostatPM_figs:
        div = figz.to_html(full_html=False, include_plotlyjs='cdn')
        rp += f'<div id="plotlyGraphiostatPM">{div}</div>'

    content = content.replace(
        "<!-- perf.iostatpm_placeholder -->",
        rp)

    # Performance Analysis - Network Statistics
    log_message("Generating Performance Report 5/5 - Network Statistics")
    rp = ""

    for figxy in sarnet_figs:
        div = figxy.to_html(full_html=False, include_plotlyjs='cdn')
        rp += f'<div id="plotlyGraphiostatPM">{div}</div>'

    content = content.replace(
        "<!-- perf.network_placeholder -->",
        rp)

    # Process Information - Process Stats CPU
    log_message("Process Information 1/5 - CPU")
    pidstat_input_file = "pidstat.txt"
    pidstat_header = pidstat_extract_header_line(pidstat_input_file)
    chunks, timestamps, chunks_js_object = generate_pidstat(
        pidstat_input_file, pidstat_header)

    rp = ""
    rp += f'''
        <script>
            document.addEventListener('DOMContentLoaded', function() {{
                const chunkData = {json.dumps(chunks)};
                const header = "{pidstat_header}";
                if (window.initPidstatSection) {{
                    window.initPidstatSection(
                        'timestampSelect',
                        'pidstatCpuTable',
                        chunkData,
                        header,
                        {{
                            metric: '%CPU',
                            thresholds: {{ warn: 60, crit: 80 }},
                            defaultTopN: 25
                        }}
                    );
                }}
            }});
        </script>
            <h2>PID Statistics - CPU Load Distribution</h2>
            <h3>Select sample where you observed high CPU utilization</h3>
            <div class="pid-controls">
                <select id="timestampSelect">
                    <option value="" disabled selected>
                        Select Timestamp
                    </option>
    '''

    # Adding the options for the combobox in HTML
    sorted_timestamps = sorted(list(timestamps))
    rp += '<option value="all">Select Timestamp</option>\n'
    for timestamp in sorted_timestamps:
        rp += f'<option value="{timestamp}">{timestamp}</option>\n'

    rp += '''
                </select>
            </div>
            <div class="table-container"><div id="pidstatCpuTable"></div></div>
    '''
    content = content.replace(
        "<!-- procinfo.pidstat_CPU_placeholder -->",
        rp)

    # Process Information - Process Stats IO
    log_message("Process Information 2/5 - IO")
    pidstatio_input_file = "pidstat-io.txt"
    pidstatio_header = pidstatio_extract_header_line(pidstatio_input_file)
    piochunks, piotimestamps, piochunks_js_object = generate_pidstatio(
        pidstatio_input_file, pidstatio_header)

    rp = ""
    rp += f'''
        <script>
            document.addEventListener('DOMContentLoaded', function() {{
                const chunkData = {json.dumps(piochunks)};
                const header = "{pidstatio_header}";
                if (window.initPidstatSection) {{
                    window.initPidstatSection(
                        'piotimestampSelect',
                        'pidstatIoTable',
                        chunkData,
                        header,
                        {{
                            metric: 'kB_rd/s',
                            thresholds: {{ warn: 10000, crit: 50000 }},
                            highlightColumn: 'iodelay',
                            highlightThresholds: {{ warn: 9, crit: 20 }},
                            defaultTopN: 25,
                            controlsKey: 'Io'
                        }}
                    );
                }}
            }});
        </script>
            <h2>PID Statistics - IO Load Distribution</h2>
            <h3>Select sample where you observed high IO utilization</h3>
            <div class="pid-controls">
                <select id="piotimestampSelect">
                    <option value="" disabled selected>
                        Select Timestamp
                    </option>
    '''

    # Adding the options for the combobox in HTML
    piosorted_timestamps = sorted(list(piotimestamps))
    rp += '<option value="all">Select Timestamp</option>\n'
    for piotimestamp in piosorted_timestamps:
        rp += f'<option value="{piotimestamp}">{piotimestamp}</option>\n'
    rp += '''
                </select>
            </div>
            <div class="table-container"><div id="pidstatIoTable"></div></div>
    '''

    content = content.replace(
        "<!-- procinfo.pidstat_IO_placeholder -->",
        rp)

    # Process Information - Process Stats Memory
    log_message("Process Information 3/5 - Memory")
    pidstatmem_input_file = "pidstat-memory.txt"
    pidstatmem_header = pidstatmem_extract_header_line(pidstatmem_input_file)
    memchunks, memtimestamps, memchunks_js_object = generate_pidstatmem(
        pidstatmem_input_file, pidstatmem_header)

    rp = ""
    rp += f'''
        <script>
            document.addEventListener('DOMContentLoaded', function() {{
                const chunkData = {json.dumps(memchunks)};
                const header = "{pidstatmem_header}";
                if (window.initPidstatSection) {{
                    window.initPidstatSection(
                        'memtimestampSelect',
                        'pidstatMemTable',
                        chunkData,
                        header,
                        {{
                            metric: '%MEM',
                            thresholds: {{ warn: 60, crit: 80 }},
                            highlightColumn: '%MEM',
                            highlightThresholds: {{ warn: 60, crit: 80 }},
                            defaultTopN: 25,
                            controlsKey: 'Mem'
                        }}
                    );
                }}
            }});
        </script>
            <h2>PID Statistics - Memory Load Distribution</h2>
            <h3>Select sample where you observed high Memory utilization</h3>
            <div class="pid-controls">
                <select id="memtimestampSelect">
                    <option value="" disabled selected>
                        Select Timestamp
                    </option>
    '''

    # Adding the options for the combobox in HTML
    memsorted_timestamps = sorted(list(memtimestamps))
    rp += '<option value="all">Select Timestamp</option>\n'
    for memtimestamp in memsorted_timestamps:
        rp += f'<option value="{memtimestamp}">{memtimestamp}</option>\n'

    rp += '''
                </select>
            </div>
            <div class="table-container"><div id="pidstatMemTable"></div></div>
        </div>
    '''

    content = content.replace(
        "<!-- procinfo.pidstat_mem_placeholder -->",
        rp)

    # Process Information - top
    log_message("Process Information 4/5 - top")
    top_chunks_js_object, top_timestamps = generate_top("top.txt")

    rp = ""
    rp += f'''
        <script>
            document.addEventListener('DOMContentLoaded', function() {{
                const chunkData = {top_chunks_js_object};
                if (window.initTopSection) {{
                    window.initTopSection(
                        'topTimestampSelect',
                        'topTable',
                        chunkData,
                        {{
                            // TOP: prefer %CPU if present; fall back handled
                            // in JS
                            metric: '%CPU',
                            thresholds: {{ warn: 60, crit: 80 }},
                            highlightColumn: '%CPU',
                            highlightThresholds: {{ warn: 60, crit: 80 }},
                            defaultTopN: 25,
                            controlsKey: 'Top'
                        }}
                    );
                }}
            }});
        </script>
            <h2>top output - sampled</h2>
            <h3>Select sample below</h3>
            <div class="pid-controls">
                <select id="topTimestampSelect">
                    <option value="" disabled selected>
                        Select Timestamp
                    </option>
    '''

    # Adding the options for the top combobox in HTML
    for timestamp in sorted(list(top_timestamps)):
        rp += f'<option value="{timestamp}">{timestamp}</option>\n'

    rp += '''
                </select>
            </div>
            <div class="table-container"><div id="topTable"></div></div>

    '''

    content = content.replace(
        "<!-- procinfo.top_placeholder -->",
        rp)

    # Process Information - iotop
    log_message("Process Information 5/5 - iotop")
    iotop_timestamps, iotop_chunks_js_object = generate_iotop("iotop.txt")

    rp = ""
    rp += f'''
        <script>
            document.addEventListener('DOMContentLoaded', function() {{
                const chunkData = {iotop_chunks_js_object};
                if (window.initIotopSection) {{
                    window.initIotopSection(
                        'iotopTimestampSelect',
                        'iotopTable',
                        chunkData,
                        {{
                            // iotop: highlight IO usage columns if present;
                            // fallback in JS
                            metric: 'DISK_READ',
                            thresholds: {{ warn: 10000, crit: 50000 }},
                            highlightColumn: 'IO%',
                            highlightThresholds: {{ warn: 60, crit: 80 }},
                            defaultTopN: 25,
                            controlsKey: 'Iotop'
                        }}
                    );
                }}
            }});
        </script>
            <h2>iotop output - sampled</h2>
            <h3>Select sample below - useful to understand which process is on
            top of the Disk</h3>
            <div class="pid-controls">
                <select id="iotopTimestampSelect">
                    <option value="" disabled selected>
                        Select Timestamp
                    </option>
    '''

    # Adding the options for the iotop combobox in HTML
    for timestamp in sorted(list(iotop_timestamps)):
        rp += f'<option value="{timestamp}">{timestamp}</option>\n'

    rp += '''
                </select>
            </div>
            <div class="table-container"><div id="iotopTable"></div></div>
    '''

    content = content.replace(
        "<!-- procinfo.iotop_placeholder -->",
        rp)

    # Process Performance - Top 10 CPU Consumers
    log_message("Process Performance 1/3 - Top 10 CPU Consumers")
    rp = ""

    try:
        top_cpu_data = extract_top_cpu_consumers("pidstat.txt", top_n=10)

        if top_cpu_data['timestamps']:
            # Color palette for distinct process lines
            colors = [
                '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7',
                '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9'
            ]

            # Create %usr graph (ranked by avg %usr)
            if top_cpu_data['top_usr']:
                fig_usr = go.Figure()
                for idx, (command, proc_data) in enumerate(
                        top_cpu_data['top_usr'].items()):
                    avg_val = proc_data['avg_metric']
                    pids_str = ', '.join(proc_data['pids'][:5])
                    if len(proc_data['pids']) > 5:
                        pids_str += '...'
                    label = f"{command[:35]} (avg:{avg_val}%)"
                    fig_usr.add_trace(
                        go.Scatter(
                            x=top_cpu_data['timestamps'],
                            y=proc_data['values'],
                            mode='lines',
                            name=label,
                            line=dict(color=colors[idx % len(colors)]),
                            hovertemplate=(
                                f"<b>{command}</b><br>"
                                f"PIDs: {pids_str}<br>"
                                f"Avg %usr: {avg_val}%<br>"
                                "Time: %{x}<br>"
                                "%usr: %{y:.2f}%<extra></extra>"
                            )
                        )
                    )
                fig_usr.update_layout(
                    title='Top 10 %usr Consumers (User CPU Time)',
                    xaxis_title='Timestamp',
                    yaxis_title='%usr',
                    height=500,
                    template="seaborn",
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=-0.4,
                        xanchor="center",
                        x=0.5
                    ),
                    margin=dict(b=150)
                )
                div_usr = fig_usr.to_html(full_html=False, include_plotlyjs='cdn')
                rp += f'<div id="plotlyGraphTop10CpuUsr">{div_usr}</div>'

            # Create %system graph (ranked by avg %system)
            if top_cpu_data['top_system']:
                fig_sys = go.Figure()
                for idx, (command, proc_data) in enumerate(
                        top_cpu_data['top_system'].items()):
                    avg_val = proc_data['avg_metric']
                    pids_str = ', '.join(proc_data['pids'][:5])
                    if len(proc_data['pids']) > 5:
                        pids_str += '...'
                    label = f"{command[:35]} (avg:{avg_val}%)"
                    fig_sys.add_trace(
                        go.Scatter(
                            x=top_cpu_data['timestamps'],
                            y=proc_data['values'],
                            mode='lines',
                            name=label,
                            line=dict(color=colors[idx % len(colors)]),
                            hovertemplate=(
                                f"<b>{command}</b><br>"
                                f"PIDs: {pids_str}<br>"
                                f"Avg %system: {avg_val}%<br>"
                                "Time: %{x}<br>"
                                "%system: %{y:.2f}%<extra></extra>"
                            )
                        )
                    )
                fig_sys.update_layout(
                    title='Top 10 %system Consumers (Kernel CPU Time)',
                    xaxis_title='Timestamp',
                    yaxis_title='%system',
                    height=500,
                    template="seaborn",
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=-0.4,
                        xanchor="center",
                        x=0.5
                    ),
                    margin=dict(b=150)
                )
                div_sys = fig_sys.to_html(full_html=False, include_plotlyjs='cdn')
                rp += f'<div id="plotlyGraphTop10CpuSys">{div_sys}</div>'

            # Create %wait graph (ranked by avg %wait)
            if top_cpu_data['top_wait']:
                fig_wait = go.Figure()
                for idx, (command, proc_data) in enumerate(
                        top_cpu_data['top_wait'].items()):
                    avg_val = proc_data['avg_metric']
                    pids_str = ', '.join(proc_data['pids'][:5])
                    if len(proc_data['pids']) > 5:
                        pids_str += '...'
                    label = f"{command[:35]} (avg:{avg_val}%)"
                    fig_wait.add_trace(
                        go.Scatter(
                            x=top_cpu_data['timestamps'],
                            y=proc_data['values'],
                            mode='lines',
                            name=label,
                            line=dict(color=colors[idx % len(colors)]),
                            hovertemplate=(
                                f"<b>{command}</b><br>"
                                f"PIDs: {pids_str}<br>"
                                f"Avg %wait: {avg_val}%<br>"
                                "Time: %{x}<br>"
                                "%wait: %{y:.2f}%<extra></extra>"
                            )
                        )
                    )
                fig_wait.update_layout(
                    title='Top 10 %wait Consumers (I/O Wait Time)',
                    xaxis_title='Timestamp',
                    yaxis_title='%wait',
                    height=500,
                    template="seaborn",
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=-0.4,
                        xanchor="center",
                        x=0.5
                    ),
                    margin=dict(b=150)
                )
                div_wait = fig_wait.to_html(full_html=False, include_plotlyjs='cdn')
                rp += f'<div id="plotlyGraphTop10CpuWait">{div_wait}</div>'

            if not rp:
                rp = '<p>No pidstat CPU data available for top consumers.</p>'
        else:
            rp = '<p>No pidstat CPU data available for top consumers.</p>'
    except Exception as e:
        log_message(f"Error generating top CPU consumers charts: {e}", "Error")
        rp = '<p>Error generating top CPU consumers charts.</p>'

    content = content.replace(
        "<!-- procperf.top10cpu_placeholder -->",
        rp)

    # Process Performance - Top 10 IO Consumers
    log_message("Process Performance 2/3 - Top 10 IO Consumers")
    rp = ""

    try:
        top_io_data = extract_top_io_consumers("pidstat-io.txt", top_n=10)

        if top_io_data['timestamps']:
            # Color palette for distinct process lines
            colors = [
                '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7',
                '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9'
            ]

            # Create kB_rd/s graph (ranked by avg read)
            if top_io_data['top_read']:
                fig_read = go.Figure()
                for idx, (command, proc_data) in enumerate(
                        top_io_data['top_read'].items()):
                    avg_val = proc_data['avg_metric']
                    pids_str = ', '.join(proc_data['pids'][:5])
                    if len(proc_data['pids']) > 5:
                        pids_str += '...'
                    label = f"{command[:35]} (avg:{avg_val})"
                    fig_read.add_trace(
                        go.Scatter(
                            x=top_io_data['timestamps'],
                            y=proc_data['values'],
                            mode='lines',
                            name=label,
                            line=dict(color=colors[idx % len(colors)]),
                            hovertemplate=(
                                f"<b>{command}</b><br>"
                                f"PIDs: {pids_str}<br>"
                                f"Avg kB_rd/s: {avg_val}<br>"
                                "Time: %{x}<br>"
                                "kB_rd/s: %{y:.2f}<extra></extra>"
                            )
                        )
                    )
                fig_read.update_layout(
                    title='Top 10 Disk Read Consumers (kB_rd/s)',
                    xaxis_title='Timestamp',
                    yaxis_title='kB_rd/s',
                    height=500,
                    template="seaborn",
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=-0.4,
                        xanchor="center",
                        x=0.5
                    ),
                    margin=dict(b=150),
                )
                div_read = fig_read.to_html(full_html=False, include_plotlyjs='cdn')
                rp += f'<div id="plotlyGraphTop10IoRead">{div_read}</div>'

            # Create kB_wr/s graph (ranked by avg write)
            if top_io_data['top_write']:
                fig_write = go.Figure()
                for idx, (command, proc_data) in enumerate(
                        top_io_data['top_write'].items()):
                    avg_val = proc_data['avg_metric']
                    pids_str = ', '.join(proc_data['pids'][:5])
                    if len(proc_data['pids']) > 5:
                        pids_str += '...'
                    label = f"{command[:35]} (avg:{avg_val})"
                    fig_write.add_trace(
                        go.Scatter(
                            x=top_io_data['timestamps'],
                            y=proc_data['values'],
                            mode='lines',
                            name=label,
                            line=dict(color=colors[idx % len(colors)]),
                            hovertemplate=(
                                f"<b>{command}</b><br>"
                                f"PIDs: {pids_str}<br>"
                                f"Avg kB_wr/s: {avg_val}<br>"
                                "Time: %{x}<br>"
                                "kB_wr/s: %{y:.2f}<extra></extra>"
                            )
                        )
                    )
                fig_write.update_layout(
                    title='Top 10 Disk Write Consumers (kB_wr/s)',
                    xaxis_title='Timestamp',
                    yaxis_title='kB_wr/s',
                    height=500,
                    template="seaborn",
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=-0.4,
                        xanchor="center",
                        x=0.5
                    ),
                    margin=dict(b=150),
                )
                div_write = fig_write.to_html(full_html=False, include_plotlyjs='cdn')
                rp += f'<div id="plotlyGraphTop10IoWrite">{div_write}</div>'

            # Create iodelay graph (ranked by avg iodelay)
            if top_io_data['top_iodelay']:
                fig_iodelay = go.Figure()
                for idx, (command, proc_data) in enumerate(
                        top_io_data['top_iodelay'].items()):
                    avg_val = proc_data['avg_metric']
                    pids_str = ', '.join(proc_data['pids'][:5])
                    if len(proc_data['pids']) > 5:
                        pids_str += '...'
                    label = f"{command[:35]} (avg:{avg_val})"
                    fig_iodelay.add_trace(
                        go.Scatter(
                            x=top_io_data['timestamps'],
                            y=proc_data['values'],
                            mode='lines',
                            name=label,
                            line=dict(color=colors[idx % len(colors)]),
                            hovertemplate=(
                                f"<b>{command}</b><br>"
                                f"PIDs: {pids_str}<br>"
                                f"Avg iodelay: {avg_val}<br>"
                                "Time: %{x}<br>"
                                "iodelay: %{y:.2f}<extra></extra>"
                            )
                        )
                    )
                fig_iodelay.update_layout(
                    title='Top 10 I/O Delay Consumers (iodelay)',
                    xaxis_title='Timestamp',
                    yaxis_title='iodelay (clock ticks)',
                    height=500,
                    template="seaborn",
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=-0.4,
                        xanchor="center",
                        x=0.5
                    ),
                    margin=dict(b=150),
                )
                div_iodelay = fig_iodelay.to_html(
                    full_html=False, include_plotlyjs='cdn')
                rp += f'<div id="plotlyGraphTop10IoDelay">{div_iodelay}</div>'

            if not rp:
                rp = '<p>No pidstat IO data available for top consumers.</p>'
        else:
            rp = '<p>No pidstat IO data available for top consumers.</p>'
    except Exception as e:
        log_message(f"Error generating top IO consumers charts: {e}", "Error")
        rp = '<p>Error generating top IO consumers charts.</p>'

    content = content.replace(
        "<!-- procperf.top10io_placeholder -->",
        rp)

    # Process Performance - Top 10 Memory Consumers
    log_message("Process Performance 3/3 - Top 10 Memory Consumers")
    rp = ""

    try:
        top_mem_data = extract_top_mem_consumers("pidstat-memory.txt", top_n=10)

        if top_mem_data['timestamps']:
            # Color palette for distinct process lines
            colors = [
                '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7',
                '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9'
            ]

            # Create %MEM graph (ranked by avg %MEM)
            if top_mem_data['top_mem_pct']:
                fig_mem = go.Figure()
                for idx, (command, proc_data) in enumerate(
                        top_mem_data['top_mem_pct'].items()):
                    avg_val = proc_data['avg_metric']
                    pids_str = ', '.join(proc_data['pids'][:5])
                    if len(proc_data['pids']) > 5:
                        pids_str += '...'
                    label = f"{command[:35]} (avg:{avg_val}%)"
                    fig_mem.add_trace(
                        go.Scatter(
                            x=top_mem_data['timestamps'],
                            y=proc_data['values'],
                            mode='lines',
                            name=label,
                            line=dict(color=colors[idx % len(colors)]),
                            hovertemplate=(
                                f"<b>{command}</b><br>"
                                f"PIDs: {pids_str}<br>"
                                f"Avg %MEM: {avg_val}%<br>"
                                "Time: %{x}<br>"
                                "%MEM: %{y:.2f}%<extra></extra>"
                            )
                        )
                    )
                fig_mem.update_layout(
                    title='Top 10 Memory Consumers (%MEM)',
                    xaxis_title='Timestamp',
                    yaxis_title='%MEM',
                    height=500,
                    template="seaborn",
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=-0.4,
                        xanchor="center",
                        x=0.5
                    ),
                    margin=dict(b=150)
                )
                div_mem = fig_mem.to_html(full_html=False, include_plotlyjs='cdn')
                rp += f'<div id="plotlyGraphTop10MemPct">{div_mem}</div>'

            # Create RSS graph (ranked by avg RSS)
            if top_mem_data['top_rss']:
                fig_rss = go.Figure()
                for idx, (command, proc_data) in enumerate(
                        top_mem_data['top_rss'].items()):
                    avg_val = proc_data['avg_metric']
                    # Convert KB to MB for display
                    avg_mb = round(avg_val / 1024, 2)
                    pids_str = ', '.join(proc_data['pids'][:5])
                    if len(proc_data['pids']) > 5:
                        pids_str += '...'
                    label = f"{command[:35]} (avg:{avg_mb} MB)"
                    # Convert values to MB for plotting
                    values_mb = [v / 1024 for v in proc_data['values']]
                    fig_rss.add_trace(
                        go.Scatter(
                            x=top_mem_data['timestamps'],
                            y=values_mb,
                            mode='lines',
                            name=label,
                            line=dict(color=colors[idx % len(colors)]),
                            hovertemplate=(
                                f"<b>{command}</b><br>"
                                f"PIDs: {pids_str}<br>"
                                f"Avg RSS: {avg_mb} MB<br>"
                                "Time: %{x}<br>"
                                "RSS: %{y:.2f} MB<extra></extra>"
                            )
                        )
                    )
                fig_rss.update_layout(
                    title='Top 10 RSS Consumers (Resident Set Size)',
                    xaxis_title='Timestamp',
                    yaxis_title='RSS (MB)',
                    height=500,
                    template="seaborn",
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=-0.4,
                        xanchor="center",
                        x=0.5
                    ),
                    margin=dict(b=150)
                )
                div_rss = fig_rss.to_html(full_html=False, include_plotlyjs='cdn')
                rp += f'<div id="plotlyGraphTop10Rss">{div_rss}</div>'

            # Create VSZ graph (ranked by avg VSZ)
            if top_mem_data['top_vsz']:
                fig_vsz = go.Figure()
                for idx, (command, proc_data) in enumerate(
                        top_mem_data['top_vsz'].items()):
                    avg_val = proc_data['avg_metric']
                    # Convert KB to MB for display
                    avg_mb = round(avg_val / 1024, 2)
                    pids_str = ', '.join(proc_data['pids'][:5])
                    if len(proc_data['pids']) > 5:
                        pids_str += '...'
                    label = f"{command[:35]} (avg:{avg_mb} MB)"
                    # Convert values to MB for plotting
                    values_mb = [v / 1024 for v in proc_data['values']]
                    fig_vsz.add_trace(
                        go.Scatter(
                            x=top_mem_data['timestamps'],
                            y=values_mb,
                            mode='lines',
                            name=label,
                            line=dict(color=colors[idx % len(colors)]),
                            hovertemplate=(
                                f"<b>{command}</b><br>"
                                f"PIDs: {pids_str}<br>"
                                f"Avg VSZ: {avg_mb} MB<br>"
                                "Time: %{x}<br>"
                                "VSZ: %{y:.2f} MB<extra></extra>"
                            )
                        )
                    )
                fig_vsz.update_layout(
                    title='Top 10 VSZ Consumers (Virtual Memory Size)',
                    xaxis_title='Timestamp',
                    yaxis_title='VSZ (MB)',
                    height=500,
                    template="seaborn",
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=-0.4,
                        xanchor="center",
                        x=0.5
                    ),
                    margin=dict(b=150)
                )
                div_vsz = fig_vsz.to_html(full_html=False, include_plotlyjs='cdn')
                rp += f'<div id="plotlyGraphTop10Vsz">{div_vsz}</div>'

            if not rp:
                rp = '<p>No pidstat memory data available for top consumers.</p>'
        else:
            rp = '<p>No pidstat memory data available for top consumers.</p>'
    except Exception as e:
        log_message(f"Error generating top memory consumers charts: {e}", "Error")
        rp = '<p>Error generating top memory consumers charts.</p>'

    content = content.replace(
        "<!-- procperf.top10mem_placeholder -->",
        rp)

    rp = ""
    rp += f'<p>| WebApp v{script_version}</p>'
    content = content.replace(
        "<!-- footer.version_placeholder -->",
        rp)

    # Output file path
    output_filepath = output_filename

    # Write the modified template content to the output file
    with open(output_filepath, 'w') as f:
        f.write(content)


if __name__ == "__generate_report__":
    generate_report()
