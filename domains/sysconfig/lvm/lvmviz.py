"""
LVM visualization processor.
"""
# Legacy function wrappers for backward compatibility with generate_html.py
# NOTE: This module only provides legacy function wrappers for backward
# compatibility. The class-based processor is not used in the current
# implementation.


def parse_pvs(filename='pvs.txt'):
    """Legacy function wrapper for backward compatibility."""
    pvs = []
    with open(filename, 'r') as f:
        for line in f.readlines()[1:]:
            parts = line.split()
            if len(parts) >= 6:  # Ensure that the line has enough parts
                pvs.append((parts[0], parts[1], parts[4], parts[5]))
    return pvs


def parse_vgs(filename='vgs.txt'):
    """Legacy function wrapper for backward compatibility."""
    vgs = []
    with open(filename, 'r') as f:
        for line in f.readlines()[1:]:
            parts = line.split()
            if len(parts) >= 7:
                vgs.append((parts[0], parts[5], parts[6]))
    return vgs


def parse_lvs(filename='lvs.txt'):
    """Legacy function wrapper for backward compatibility."""
    import re
    lvs = []
    with open(filename, 'r') as f:
        lines = f.readlines()
        if len(lines) < 2:
            return lvs

        for line in lines[1:]:
            parts = re.split(r'\s+', line.strip())

            if len(parts) >= 8:
                lvs.append((parts[0], parts[1], parts[3],
                           parts[7], parts[6], parts[5]))
            else:
                print(
                    f"Skipped line due to insufficient columns: {line.strip()}"
                    )

    return lvs


def create_graph(pvs, vgs, lvs):
    """Legacy function wrapper for backward compatibility."""
    from graphviz import Digraph
    import re

    def parse_lsblk(filename='lsblk-f.txt'):
        lsblk_data = {}
        lv_pattern = re.compile(
            r'([a-zA-Z0-9\-]+)\s+(xfs|ext4|vfat)?\s+'
            r'([a-zA-Z0-9\-]+)?\s+([/\w]+)?')

        with open(filename, 'r') as f:
            for line in f.readlines()[1:]:
                match = lv_pattern.search(line)
                if match:
                    name, fstype, _, mountpoint = match.groups()
                    # Extract just the LV name from the full name
                    lv_name = name.split('-')[-1] if '-' in name else name
                    lsblk_data[lv_name] = {
                        'fstype': fstype, 'mountpoint': mountpoint}
        return lsblk_data

    def parse_df(filename='df-h.txt'):
        df_data = {}
        with open(filename, 'r') as f:
            for line in f.readlines()[1:]:
                parts = line.split()
                if len(parts) >= 6:
                    filesystem, _, _, avail, use_percent, mountpoint = (
                        parts[0], parts[2], parts[3], parts[3],
                        parts[4], parts[5])
                    lv_name = filesystem.split(
                        '-')[-1] if '-' in filesystem else filesystem
                    df_data[lv_name] = {
                        'avail': avail, 'use_percent': use_percent}
                    # dummy check mountpoint var
                    if mountpoint == '-':
                        continue
        return df_data

    def parse_dev_mapper(filename='ls-l-dev-mapper.txt'):
        dev_mapper_data = {}
        with open(filename, 'r') as f:
            for line in f.readlines():
                if '->' in line:
                    parts = line.split()
                    mapper_path = parts[-3]
                    dm_number = parts[-1].split('/')[-1]
                    vg_lv_name = mapper_path.split('/')[-1]
                    dev_mapper_data[vg_lv_name] = dm_number
        return dev_mapper_data

    def create_graph_for_vg(
        vg,
        vg_size,
        vg_free,
        relevant_pvs,
        relevant_lvs,
        lsblk_data,
        df_data,
        dev_mapper_data
            ):
        dot = Digraph(format='svg')
        dot.attr(rankdir='TB', bgcolor='transparent')  # Top-to-Bottom layout

        # Color scheme
        soft_red = '#E06C75'
        soft_green = '#98C379'
        soft_blue = '#61AFEF'

        # Font settings
        diagram_font = 'Monospace'  # Modern monospaced font
        font_size = '10'

        for pv, size, free in relevant_pvs:
            dot.node(
                pv,
                label=f"PV: {pv}\nSize: {size}\nFree: {free}",
                shape='box',
                style='filled',
                fillcolor=soft_red,
                fontcolor='white',
                fontname=diagram_font,
                fontsize=font_size)

            dot.edge(pv, vg, color='white')

        dot.node(
            vg,
            label=f"VG: {vg}\nSize: {vg_size}\nFree: {vg_free}",
            shape='box',
            style='filled',
            fillcolor=soft_green,
            fontcolor='white',
            fontname=diagram_font,
            fontsize=font_size
                )

        for lv, size, devices, num_stripes, stripe_size in relevant_lvs:
            label = f"LV: {lv}\nSize: {size}\nType: {devices}"

            if devices == "striped":
                label += (
                    f"\nNumber of Stripes: {num_stripes}\n"
                    f"Stripe: {stripe_size}"
                )

            vg_lv_name = f"{vg}-{lv}"
            if vg_lv_name in dev_mapper_data:
                label += f"\nDM: {dev_mapper_data[vg_lv_name]}"

            # Add lsblk and df data if available
            if lv in lsblk_data:
                label += (
                    f"\nFS type: {lsblk_data[lv]['fstype']}\n"
                    f"Mountpoint: {lsblk_data[lv]['mountpoint']}"
                    )
            if lv in df_data:
                label += (
                    f"\nAvailable: {df_data[lv]['avail']}\n"
                    f"Use%: {df_data[lv]['use_percent']}"
                )

            dot.node(
                lv,
                label=label,
                shape='box',
                style='filled',
                fillcolor=soft_blue,
                fontcolor='white',
                fontname=diagram_font,
                fontsize=font_size
                )
            dot.edge(vg, lv, color='white')

        return (
            dot.pipe()
            .decode('utf-8')
            .replace(
                '<?xml version="1.0" encoding="UTF-8" standalone="no"?>',
                '')
            .strip()
        )

    svg_list = []
    lsblk_data = parse_lsblk()
    df_data = parse_df()
    dev_mapper_data = parse_dev_mapper()

    for vg, vg_size, vg_free in vgs:
        relevant_pvs = [(pv, size, free)
                        for pv, v, size, free in pvs if v == vg]

        relevant_lvs = [
            (lv, size, devices, num_stripes, stripe_size)
            for lv, v, size, devices, num_stripes, stripe_size in lvs
            if v == vg
        ]

        svg_content = create_graph_for_vg(
            vg,
            vg_size,
            vg_free,
            relevant_pvs,
            relevant_lvs,
            lsblk_data,
            df_data,
            dev_mapper_data
        )
        svg_content = svg_content.replace(
            '<svg ',
            '<svg style="display: block; margin-bottom: 20px;" fill="none" '
        )

        svg_list.append(svg_content)
    return svg_list
