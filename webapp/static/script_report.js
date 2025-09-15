function openTab(evt, tabName) {
    var i, tabContent, tabLinks;
    tabContent = document.getElementsByClassName('tab-content');
    for (i = 0; i < tabContent.length; i++) {
        tabContent[i].style.display = 'none';
    }
    tabLinks = document.getElementsByClassName('subtab');
    for (i = 0; i < tabLinks.length; i++) {
        tabLinks[i].classList.remove('active');
    }
    document.getElementById(tabName).style.display = 'block';
    evt.currentTarget.classList.add('active');
    window.dispatchEvent(new Event('resize'));
    var content = document.querySelector(".collapsible-content");
    if (content) {
        content.style.width = "0";
        content.style.display = "none"; // Hide the content
        content.classList.remove("show");
        content.classList.add("hidden");
    }
}

function openSubTabs(subTabId) {
    // Get all primary tabs and submenus
    let primaryTabs = document.getElementsByClassName("tab");
    let subtabs = document.getElementsByClassName("subtabs");

    // Iterate through all submenus
    for (let i = 0; i < subtabs.length; i++) {
        // If the current submenu is the one associated with the clicked primary tab
        if (subtabs[i].id === subTabId) {
            // Check if the submenu is currently displayed
            if (subtabs[i].style.display === "flex") {
                // If displayed, hide it and deactivate the primary tab
                subtabs[i].style.display = "none";
                primaryTabs[i].classList.remove('active');
            } else {
                // If not displayed, show it and activate the primary tab
                subtabs[i].style.display = "flex";
                primaryTabs[i].classList.add('active');
            }
        } else {
            // Hide other submenus and deactivate their associated primary tabs
            subtabs[i].style.display = "none";
            primaryTabs[i].classList.remove('active');
        }
    }
}




// Hide the loading overlay when the page is fully loaded
document.addEventListener('DOMContentLoaded', function () {
    const loadingOverlay = document.querySelector('.loading-overlay');
    loadingOverlay.style.display = 'none';
});

document.addEventListener("DOMContentLoaded", function () {
    var btn = document.querySelector(".collapsible-button");
    var content = document.querySelector(".collapsible-content");

    btn.addEventListener("click", function () {
        if (content.style.display === "none" || content.style.width === "0px") {
            content.style.width = "450px";
            content.style.display = "block"; // Show the content
            content.classList.remove("hidden");
            content.classList.add("show");
        } else {
            content.style.width = "0";
            content.style.display = "none"; // Hide the content
            content.classList.remove("show");
            content.classList.add("hidden");
        }
    });
});



document.addEventListener("DOMContentLoaded", function () {
    // Query all elements that have a data-file attribute
    const elements = document.querySelectorAll("[data-file]");

    elements.forEach((element) => {
        // Fetch the filename from the data-file attribute
        const fileName = element.getAttribute("data-file");
        console.log('Filename:', fileName);  // Debugging line

        // Initialize the XMLHttpRequest
        var xhr = new XMLHttpRequest();
        xhr.onreadystatechange = function () {
            if (xhr.readyState === 4 && xhr.status === 200) {
                // Populate the innerText of the element with the response text
                element.innerText = xhr.responseText;
            }
        };

        // Configure and send the request
        xhr.open("GET", `/get_text?file_name=${fileName}`, true);
        xhr.send();
    });
});



// ===== PIDSTAT CPU rendering utilities =====
(function () {
    function parseHeader(headerLine) {
        return headerLine.trim().split(/\s+/);
    }

    function coerceValue(value) {
        const n = Number(value);
        return Number.isFinite(n) ? n : value;
    }

    function parsePidstatChunk(headerLine, rawChunk) {
        const columns = parseHeader(headerLine);
        const numCols = columns.length;
        const lines = (rawChunk || '').split('\n').filter(l => l.trim().length > 0);
        const rows = [];
        for (const line of lines) {
            const tokens = line.trim().split(/\s+/);
            if (tokens.length === 0) continue;
            if (tokens.length < numCols) continue;
            const fixed = tokens.slice(0, numCols - 1);
            const last = tokens.slice(numCols - 1).join(' ');
            const rowTokens = fixed.concat([last]);
            const obj = {};
            for (let i = 0; i < columns.length; i++) {
                obj[columns[i]] = coerceValue(rowTokens[i] ?? '');
            }
            rows.push(obj);
        }
        return { columns, rows };
    }

    function isNumericColumn(columnName) {
        return /%|^PID$|^UID$|^CPU$|^TIME|^kB|^VSZ$|^RSS$|^prio$/i.test(columnName);
    }

    function getCommandColumnName(columns) {
        const found = columns.find(c => /command/i.test(c));
        return found || columns[columns.length - 1];
    }

    function chooseFallbackMetric(columns) {
        if (columns.includes('%CPU')) return '%CPU';
        if (columns.includes('%MEM')) return '%MEM';
        if (columns.includes('kB_rd/s')) return 'kB_rd/s';
        if (columns.includes('kB_wr/s')) return 'kB_wr/s';
        // last numeric column
        for (let i = columns.length - 2; i >= 0; i--) { // avoid COMMAND at end
            if (isNumericColumn(columns[i])) return columns[i];
        }
        return columns[0];
    }

    function renderPidstatTable(containerId, parsed, options) {
        const container = document.getElementById(containerId);
        if (!container) return;
        let metric = options && options.metric ? options.metric : '%CPU';
        const thresholds = (options && options.thresholds) || { warn: 60, crit: 80 };
        const defaultTopN = (options && options.defaultTopN) || 25;
        const topN = (options && typeof options.topN !== 'undefined') ? options.topN : defaultTopN;
        const searchTerm = (options && typeof options.searchTerm === 'string') ? options.searchTerm.trim().toLowerCase() : '';

        const columns = parsed.columns.slice();
        let rows = parsed.rows.slice();
        let metricIdx = columns.indexOf(metric);
        if (metricIdx === -1) {
            metric = chooseFallbackMetric(columns);
            metricIdx = columns.indexOf(metric);
        }

        // Determine highlight column and thresholds (may differ from metric)
        let highlightColName = (options && options.highlightColumn) || metric;
        let highlightIdx = columns.indexOf(highlightColName);
        if (highlightIdx === -1) highlightIdx = metricIdx;
        const hThresh = (options && options.highlightThresholds) || thresholds;

        // Filter by command substring if provided
        if (searchTerm) {
            const cmdCol = getCommandColumnName(columns);
            rows = rows.filter(r => String(r[cmdCol]).toLowerCase().includes(searchTerm));
        }

        // Sort by metric desc and slice TopN
        if (metricIdx !== -1) {
            const metricName = columns[metricIdx];
            rows.sort((a, b) => (Number(b[metricName]) || 0) - (Number(a[metricName]) || 0));
        }
        const visible = (topN && topN > 0) ? rows.slice(0, topN) : rows;

        // Build table
        const table = document.createElement('table');
        table.className = 'pid-table table-sticky-header';
        const thead = document.createElement('thead');
        const thr = document.createElement('tr');
        columns.forEach((col, idx) => {
            const th = document.createElement('th');
            th.textContent = col;
            th.setAttribute('role', 'columnheader');
            th.dataset.colIndex = String(idx);
            th.className = isNumericColumn(col) ? 'numeric' : '';
            th.style.cursor = 'pointer';
            thr.appendChild(th);
        });
        thead.appendChild(thr);

        const tbody = document.createElement('tbody');
        visible.forEach((row) => {
            const tr = document.createElement('tr');
            columns.forEach((col, idx) => {
                const td = document.createElement('td');
                const val = row[col];
                const isNum = typeof val === 'number';
                td.textContent = String(val);
                if (isNum) td.classList.add('numeric');
                if (idx === highlightIdx && isNum) {
                    const v = Number(val);
                    if (v >= hThresh.crit) td.classList.add('heat-high');
                    else if (v >= hThresh.warn) td.classList.add('heat-warn');
                }
                tr.appendChild(td);
            });
            tbody.appendChild(tr);
        });

        // Sorting behavior for currently visible rows
        let sortState = { idx: metricIdx, dir: 'desc' };
        thead.addEventListener('click', (e) => {
            const th = e.target.closest('th');
            if (!th) return;
            const idx = Number(th.dataset.colIndex);
            const col = columns[idx];
            const isNumCol = isNumericColumn(col);
            const dir = (sortState.idx === idx && sortState.dir === 'asc') ? 'desc' : 'asc';
            sortState = { idx, dir };
            const cmp = (a, b) => {
                const av = a[col];
                const bv = b[col];
                if (isNumCol) {
                    const an = Number(av) || 0;
                    const bn = Number(bv) || 0;
                    return dir === 'asc' ? an - bn : bn - an;
                }
                const as = String(av);
                const bs = String(bv);
                return dir === 'asc' ? as.localeCompare(bs) : bs.localeCompare(as);
            };
            const current = Array.from(tbody.children).map(tr => {
                const obj = {};
                columns.forEach((c, i) => {
                    obj[c] = tr.children[i].textContent;
                });
                return obj;
            });
            const sorted = current.sort(cmp);
            // Repaint tbody
            tbody.innerHTML = '';
            sorted.forEach((row) => {
                const tr = document.createElement('tr');
                columns.forEach((c, i) => {
                    const td = document.createElement('td');
                    const val = row[c];
                    const isNum = !isNaN(Number(val)) && val !== '' && val !== null;
                    td.textContent = String(val);
                    if (isNum) td.classList.add('numeric');
                    if (i === highlightIdx && isNum) {
                        const v = Number(val);
                        if (v >= hThresh.crit) td.classList.add('heat-high');
                        else if (v >= hThresh.warn) td.classList.add('heat-warn');
                    }
                    tr.appendChild(td);
                });
                tbody.appendChild(tr);
            });
        });

        table.appendChild(thead);
        table.appendChild(tbody);
        container.innerHTML = '';
        container.appendChild(table);
    }

    function ensureControls(selectEl, key) {
        const container = selectEl && selectEl.parentElement;
        if (!container) return {};
        const safeKey = key || 'Cpu';
        const topNId = 'pidTopNSelect' + safeKey;
        const searchId = 'pidSearchInput' + safeKey;
        // Avoid duplicates
        let topN = container.querySelector('#' + topNId);
        let search = container.querySelector('#' + searchId);
        if (!topN) {
            const label = document.createElement('label');
            label.style.marginLeft = '10px';
            label.textContent = 'Top N:';
            topN = document.createElement('select');
            topN.id = topNId;
            [10, 25, 50, 100, 0].forEach(v => {
                const opt = document.createElement('option');
                opt.value = String(v);
                opt.textContent = v === 0 ? 'All' : String(v);
                if (v === 25) opt.selected = true;
                topN.appendChild(opt);
            });
            label.appendChild(topN);
            container.appendChild(label);
        }
        if (!search) {
            const label = document.createElement('label');
            label.style.marginLeft = '10px';
            label.textContent = 'Search:';
            search = document.createElement('input');
            search.type = 'text';
            search.id = searchId;
            search.placeholder = 'Filter COMMAND';
            search.style.marginLeft = '6px';
            search.size = 22;
            label.appendChild(search);
            container.appendChild(label);
        }
        return { topN, search };
    }

    function initPidstatSection(selectId, containerId, chunks, header, options) {
        const select = document.getElementById(selectId);
        const container = document.getElementById(containerId);
        if (!select || !container) return;

        const controls = ensureControls(select, (options && options.controlsKey) || 'Cpu');
        let currentParsed = null;

        function currentOptions() {
            const n = controls.topN ? Number(controls.topN.value) : (options && options.defaultTopN) || 25;
            const term = controls.search ? controls.search.value : '';
            return Object.assign({}, options || {}, { topN: n, searchTerm: term });
        }

        function render(ts) {
            if (!ts || ts === 'all') { container.innerHTML = ''; return; }
            const raw = chunks[ts] || '';
            currentParsed = parsePidstatChunk(header, raw);
            renderPidstatTable(containerId, currentParsed, currentOptions());
        }

        select.addEventListener('change', function () {
            render(this.value);
        });
        if (controls.topN) controls.topN.addEventListener('change', function () {
            const ts = select.value; if (!currentParsed || !ts || ts === 'all') return;
            render(ts);
        });
        if (controls.search) controls.search.addEventListener('input', function () {
            const ts = select.value; if (!currentParsed || !ts || ts === 'all') return;
            render(ts);
        });
    }

    window.initPidstatSection = initPidstatSection;
    // Export renderer and controls for reuse by other sections (TOP/IOTOP)
    window.renderPidstatTable = renderPidstatTable;
    window.ensureControls = ensureControls;
})();



// ===== Generic TOP/IOTOP rendering using the same table utilities =====
(function () {
    function parseGenericTableChunk(rawChunk) {
        const lines = (rawChunk || '').split('\n');
        let headerIdx = -1;
        for (let i = 0; i < lines.length; i++) {
            const line = lines[i].trim();
            if (!line) continue;
            if (/^top\s-\s/.test(line)) continue; // skip top summary header
            if (/^Tasks:/.test(line)) continue;
            if (/^%?Cpu\(s\)/.test(line)) continue;
            if (/^KiB|^MiB|^GiB/.test(line)) continue;
            if (/^Mem|^Swap/i.test(line)) continue;
            if (/^Total\s+DISK\s+READ/i.test(line)) continue; // iotop summary line
            if (line.includes('PID') && /COMMAND/i.test(line)) {
                headerIdx = i;
                break;
            }
        }
        if (headerIdx === -1) return { columns: [], rows: [] };
        let headerTokens = lines[headerIdx].trim().split(/\s+/);
        // Normalize iotop header tokens like [DISK, READ] -> DISK_READ
        const merged = [];
        for (let i = 0; i < headerTokens.length; i++) {
            const t = headerTokens[i];
            const n = headerTokens[i + 1];
            if (t === 'DISK' && (n === 'READ' || n === 'WRITE')) {
                merged.push(`DISK_${n}`);
                i++;
                continue;
            }
            if (t === 'IO' && n === '>') { merged.push('IO%'); i++; continue; }
            merged.push(t);
        }
        const header = merged;
        const numCols = header.length;
        const rows = [];
        for (let j = headerIdx + 1; j < lines.length; j++) {
            const ln = lines[j];
            if (!ln || !ln.trim()) continue;
            if (/^top\s-\s/.test(ln) || /^Tasks:/.test(ln) || /^Total\s+DISK\s+READ/i.test(ln)) break;
            const tokens = ln.trim().split(/\s+/);
            if (tokens.length < 2) continue;
            // For non-iotop tables, use generic last-column join
            const fixed = tokens.slice(0, numCols - 1);
            const last = tokens.slice(numCols - 1).join(' ');
            const rowTokens = fixed.concat([last]);
            const obj = {};
            for (let i = 0; i < header.length; i++) {
                const v = rowTokens[i] ?? '';
                const n = Number(v);
                obj[header[i]] = Number.isFinite(n) ? n : v;
            }
            rows.push(obj);
        }
        return { columns: header, rows };
    }

    function parseIotopChunk(rawChunk) {
        const lines = (rawChunk || '').split('\n');
        let headerIdx = -1;
        for (let i = 0; i < lines.length; i++) {
            const line = lines[i].trim();
            if (!line) continue;
            if (/^Total\s+DISK\s+READ/i.test(line)) continue; // summary line
            if ((/PID|TID/.test(line)) && /COMMAND/i.test(line)) { headerIdx = i; break; }
        }
        if (headerIdx === -1) return { columns: [], rows: [] };
        const headerRaw = lines[headerIdx].trim().split(/\s+/);
        // Merge tokens: DISK READ, DISK WRITE; keep IO as 'IO'
        const header = [];
        for (let i = 0; i < headerRaw.length; i++) {
            const t = headerRaw[i];
            const n = headerRaw[i + 1];
            if (t === 'DISK' && (n === 'READ' || n === 'WRITE')) { header.push(`DISK_${n}`); i++; continue; }
            header.push(t);
        }
        // Ensure COMMAND is last field name
        if (header[header.length - 1] !== 'COMMAND') header.push('COMMAND');

        const rows = [];
        for (let j = headerIdx + 1; j < lines.length; j++) {
            const ln = lines[j];
            if (!ln || !ln.trim()) continue;
            if (/^Total\s+DISK\s+READ/i.test(ln)) break;
            const tokens = ln.trim().split(/\s+/);
            if (tokens.length < 6) continue;
            let idx = 0;
            // TIME present?
            let TIME = tokens[idx];
            const timeLike = /^(\d{2}:){2}\d{2}$/.test(TIME);
            if (timeLike) idx++; else TIME = '';
            const TID = tokens[idx++];
            const PRIO = tokens[idx++] || '';
            const USER = tokens[idx++] || '';
            // DISK_READ value + unit
            const DRV = parseFloat(tokens[idx++]) || 0;
            const DRU = tokens[idx++] || '';
            // DISK_WRITE value + unit
            const DWV = parseFloat(tokens[idx++]) || 0;
            const DWU = tokens[idx++] || '';
            // SWAPIN can be '?unavailable?' or a percent number
            let SWAPIN = tokens[idx++] || '';
            if (SWAPIN === '%') { SWAPIN = 0; } // edge case
            const swapNum = parseFloat(SWAPIN);
            if (!isNaN(swapNum) && isFinite(swapNum)) {
                // optional trailing '%'
                if (tokens[idx] === '%') idx++;
                SWAPIN = swapNum;
            }
            // IO may be present (number with optional '%') or missing
            let IO = '';
            if (idx < tokens.length) {
                const maybeIO = tokens[idx];
                const ioNum = parseFloat(maybeIO);
                if (!isNaN(ioNum) && isFinite(ioNum)) {
                    idx++;
                    if (tokens[idx] === '%') idx++;
                    IO = ioNum;
                }
            }
            // COMMAND rest
            const COMMAND = tokens.slice(idx).join(' ');
            const obj = {
                TIME: TIME,
                TID: Number(TID) || TID,
                PRIO: PRIO,
                USER: USER,
                DISK_READ: DRV,
                DISK_WRITE: DWV,
                SWAPIN: SWAPIN,
                IO: IO,
                COMMAND: COMMAND
            };
            rows.push(obj);
        }
        const columns = ['TIME','TID','PRIO','USER','DISK_READ','DISK_WRITE','SWAPIN','IO','COMMAND'];
        return { columns, rows };
    }

    function initTopSection(selectId, containerId, chunks, options) {
        const select = document.getElementById(selectId);
        const container = document.getElementById(containerId);
        if (!select || !container) return;
        const controls = (window.ensureControls ? window.ensureControls(select, 'Top') : undefined);
        function currentOptions() {
            const defaultTopN = (options && options.defaultTopN) || 25;
            const n = controls && controls.topN ? Number(controls.topN.value) : defaultTopN;
            const term = controls && controls.search ? controls.search.value : '';
            return Object.assign({}, options || {}, { topN: n, searchTerm: term });
        }
        function render(ts) {
            if (!ts) { container.innerHTML = ''; return; }
            const raw = chunks[ts] || '';
            const parsed = parseGenericTableChunk(raw);
            if (window.renderPidstatTable) window.renderPidstatTable(containerId, parsed, currentOptions());
        }
        select.addEventListener('change', function () { render(this.value); });
        if (controls && controls.topN) controls.topN.addEventListener('change', function () {
            const ts = select.value; if (!ts) return; render(ts);
        });
        if (controls && controls.search) controls.search.addEventListener('input', function () {
            const ts = select.value; if (!ts) return; render(ts);
        });
    }

    function initIotopSection(selectId, containerId, chunks, options) {
        const select = document.getElementById(selectId);
        const container = document.getElementById(containerId);
        if (!select || !container) return;
        const controls = (window.ensureControls ? window.ensureControls(select, 'Iotop') : undefined);
        function currentOptions() {
            const defaultTopN = (options && options.defaultTopN) || 25;
            const n = controls && controls.topN ? Number(controls.topN.value) : defaultTopN;
            const term = controls && controls.search ? controls.search.value : '';
            return Object.assign({}, options || {}, { topN: n, searchTerm: term });
        }
        function render(ts) {
            if (!ts) { container.innerHTML = ''; return; }
            const raw = chunks[ts] || '';
            const parsed = parseIotopChunk(raw);
            if (window.renderPidstatTable) window.renderPidstatTable(containerId, parsed, currentOptions());
        }
        select.addEventListener('change', function () { render(this.value); });
        if (controls && controls.topN) controls.topN.addEventListener('change', function () {
            const ts = select.value; if (!ts) return; render(ts);
        });
        if (controls && controls.search) controls.search.addEventListener('input', function () {
            const ts = select.value; if (!ts) return; render(ts);
        });
    }

    window.initTopSection = initTopSection;
    window.initIotopSection = initIotopSection;
})();


