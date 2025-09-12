import os
import datetime
import json
from ..procinfo.pidstat.pidstatcpu import (
    print_file_contents,
    pidstat_extract_header_line,
    generate_pidstat
)

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

script_version = "2.0.1"


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
            // Function to populate chunks when a timestamp is selected
            function displayChunk() {{
                const chunkData = {json.dumps(chunks)};
                const header = "{pidstat_header}";
                const selectedTimestamp =
                    document.getElementById("timestampSelect").value;
                const sanitizedChunk = chunkData[selectedTimestamp];
                const originalChunk = sanitizedChunk
                    .replace(/\\\\n/g, '\\n')
                    .replace(/\\\\t/g, '\\t')
                    .split('\\n');

                let formattedChunk = header + "\\n";
                for(let line of originalChunk) {{
                    const columns = line.split(/\\s+/);
                if (parseFloat(columns[7]) > 80) {{
                    // Apply red color if the 8th column is greater than 80
                    formattedChunk += '<span style="color: red;">' + \
                                      line + '</span>\\n';
                }} else if (parseFloat(columns[7]) > 60) {{
                    // Apply yellow color if the 8th column is greater than 60
                    // but less than or equal to 80
                    formattedChunk += '<span style="color: yellow;">' + \
                                      line + '</span>\\n';
                }} else {{
                    formattedChunk += line + '\\n';
                }}
                }}

                document.getElementById("chunkDisplay").innerHTML = \
                    formattedChunk.replace(/\\n/g, '<br>');
            }}
        </script>
            <h2>PID Statiscs - CPU Load Distribution</h2>
            <h3>Select sample where you obsvered high CPU utilization</h3>
            <select id="timestampSelect" onchange="displayChunk()">
    '''

    # Adding the options for the combobox in HTML
    sorted_timestamps = sorted(list(timestamps))
    rp += '<option value="all">Select Timestamp</option>\n'
    for timestamp in sorted_timestamps:
        rp += f'<option value="{timestamp}">{timestamp}</option>\n'

    rp += '''
            </select>
            <pre id="chunkDisplay"></pre>
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
            // Function to populate chunks when a timestamp is selected
            function piodisplayChunk() {{
                const piochunkData = {json.dumps(piochunks)};
                const pioheader = "{pidstatio_header}";
                const pioselectedTimestamp =
                    document.getElementById("piotimestampSelect").value;
                const piosanitizedChunk = piochunkData[pioselectedTimestamp];
                const piooriginalChunk = piosanitizedChunk
                    .replace(/\\\\n/g, '\\n')
                    .replace(/\\\\t/g, '\\t')
                    .split('\\n');
                console.log(document.getElementById("piochunkDisplay"));


                let pioformattedChunk = pioheader + "\\n";
                for(let line of piooriginalChunk) {{
                    const piocolumns = line.split(/\\s+/);
                if (parseFloat(piocolumns[7]) > 80) {{
                    // Apply red color if the 8th column is greater than 80
                    pioformattedChunk += '<span style="color: red;">' + \
                                      line + '</span>\\n';
                }} else if (parseFloat(piocolumns[7]) > 60) {{
                    // Apply yellow color if the 8th column is greater than 60
                    // but less than or equal to 80
                    pioformattedChunk += '<span style="color: yellow;">' + \
                                      line + '</span>\\n';
                }} else {{
                    pioformattedChunk += line + '\\n';
                }}
                }}

                document.getElementById("piochunkDisplay").innerHTML = \
                    pioformattedChunk.replace(/\\n/g, '<br>');
            }}
        </script>
            <h2>PID Statiscs - IO Load Distribution</h2>
            <h3>Select sample where you obsvered high IO utilization</h3>
            <select id="piotimestampSelect" onchange="piodisplayChunk()">
    '''

    # Adding the options for the combobox in HTML
    piosorted_timestamps = sorted(list(piotimestamps))
    rp += '<option value="all">Select Timestamp</option>\n'
    for piotimestamp in piosorted_timestamps:
        rp += f'''
        <option value="{piotimestamp}">{piotimestamp}</option>\n'
        '''
    rp += '''
            </select>
            <pre id="piochunkDisplay"></pre>
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
            // Function to populate chunks when a timestamp is selected
            function memdisplayChunk() {{
                const memchunkData = {json.dumps(memchunks)};
                const memheader = "{pidstatmem_header}";
                const memselectedTimestamp =
                    document.getElementById("memtimestampSelect").value;
                const memsanitizedChunk = memchunkData[memselectedTimestamp];
                const memoriginalChunk = memsanitizedChunk
                    .replace(/\\\\n/g, '\\n')
                    .replace(/\\\\t/g, '\\t')
                    .split('\\n');
                console.log(document.getElementById("memchunkDisplay"));


                let memformattedChunk = memheader + "\\n";
                for(let line of memoriginalChunk) {{
                    const memcolumns = line.split(/\\s+/);
                if (parseFloat(memcolumns[7]) > 80) {{
                    // Apply red color if the 8th column is greater than 80
                    memformattedChunk += '<span style="color: red;">' + \
                                      line + '</span>\\n';
                }} else if (parseFloat(memcolumns[7]) > 60) {{
                    // Apply yellow color if the 8th column is greater than 60
                    // but less than or equal to 80
                    memformattedChunk += '<span style="color: yellow;">' + \
                                      line + '</span>\\n';
                }} else {{
                    memformattedChunk += line + '\\n';
                }}
                }}

                document.getElementById("memchunkDisplay").innerHTML = \
                    memformattedChunk.replace(/\\n/g, '<br>');
            }}
        </script>
            <h2>PID Statiscs - Memory Load Distribution</h2>
            <h3>Select sample where you obsvered high Memory utilization</h3>
            <select id="memtimestampSelect" onchange="memdisplayChunk()">
    '''

    # Adding the options for the combobox in HTML
    memsorted_timestamps = sorted(list(memtimestamps))
    rp += '<option value="all">Select Timestamp</option>\n'
    for memtimestamp in memsorted_timestamps:
        rp += f'''
        <option value="{memtimestamp}">{memtimestamp}</option>\n'
        '''

    rp += '''
            </select>
            <pre id="memchunkDisplay"></pre>
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
            // Function to populate TOP chunks when a timestamp is selected
            function displayTOPChunk() {{
                const chunkData = {top_chunks_js_object};
                const selectedTimestamp =
                    document.getElementById("topTimestampSelect").value;
                const sanitizedChunk = chunkData[selectedTimestamp];
                const originalChunk = sanitizedChunk
                    .replace(/\\\\n/g, '\\n')
                    .replace(/\\\\t/g, '\\t');
                document.getElementById("topChunkDisplay").innerText = \
                    originalChunk;
            }}
        </script>
            <h2>top output - sampled</h2>
            <h3>Select sample bellow</h3>
            <select id="topTimestampSelect" onchange="displayTOPChunk()">
            <option value="" disabled selected>Select your option</option>
    '''

    # Adding the options for the top combobox in HTML
    for timestamp in sorted(list(top_timestamps)):
        rp += f'<option value="{timestamp}">{timestamp}</option>\n'

    rp += '''
            </select>
            <pre id="topChunkDisplay"></pre>

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
            // Function to populate IOTOP chunks when a timestamp is selected
            function displayIOTOPChunk() {{
                const chunkData = {iotop_chunks_js_object};
                const selectedTimestamp =
                    document.getElementById("iotopTimestampSelect").value;
                const sanitizedChunk = chunkData[selectedTimestamp];
                const originalChunk = sanitizedChunk
                    .replace(/\\\\n/g, '\\n')
                    .replace(/\\\\t/g, '\\t');
                document.getElementById("iotopChunkDisplay").innerText = \
                    originalChunk;
            }}
        </script>
            <h2>iotop output - sampled</h2>
            <h3>Select sample bellow -
            useful to understand which process is on top the Disk</h3>
            <select id="iotopTimestampSelect" onchange="displayIOTOPChunk()">
            <option value="" disabled selected>Select your option</option>
    '''

    # Adding the options for the iotop combobox in HTML
    for timestamp in sorted(list(iotop_timestamps)):
        rp += f'<option value="{timestamp}">{timestamp}</option>\n'

    rp += '''
            </select>
            <pre id="iotopChunkDisplay"></pre>
    '''

    content = content.replace(
        "<!-- procinfo.iotop_placeholder -->",
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
