PSEUDO_FILESYSTEMS = {
    'devtmpfs', 'tmpfs', 'sysfs', 'proc', 'securityfs', 'devpts', 'cgroup', 'cgroup2',
    'mqueue', 'debugfs', 'tracefs', 'configfs',
}


def summarize_filesystems(df_h: str) -> list[dict]:
    """Parse real filesystem capacity rows from `df -h` output."""
    rows = []
    for line in df_h.splitlines()[1:]:
        parts = line.split()
        if len(parts) < 6:
            continue
        filesystem, size, used, available, percentage = parts[:5]
        mount = ' '.join(parts[5:])
        if filesystem in PSEUDO_FILESYSTEMS or filesystem.startswith('/dev/loop') or mount.startswith('/snap'):
            continue
        if not percentage.endswith('%'):
            continue
        try:
            use_percent = int(percentage[:-1])
        except ValueError:
            continue
        severity = 'critical' if use_percent >= 95 else 'warning' if use_percent >= 85 else 'normal'
        rows.append({
            'filesystem': filesystem,
            'size': size,
            'used': used,
            'available': available,
            'use_percent': use_percent,
            'mount': mount,
            'severity': severity,
        })
    return rows
