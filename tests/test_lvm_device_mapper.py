import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'webapp'))
from domains.sysconfig.lvm.lvmviz import (
    device_mapper_labels,
    parse_dev_mapper,
)


class DeviceMapperParserTests(unittest.TestCase):
    def test_maps_lvm_name_to_dm_device(self):
        content = '''lrwxrwxrwx. 1 root root 7 Aug 7 08:47 /dev/mapper/rootvg-rootlv -> ../dm-5\nlrwxrwxrwx. 1 root root 7 Aug 7 08:47 /dev/mapper/A10_A_datavg-A10_A_datalv -> ../dm-7\ncrw-------. 1 root root 10, 236 Aug 7 08:47 /dev/mapper/control\n'''
        with tempfile.NamedTemporaryFile('w', delete=False) as source:
            source.write(content)
            filename = source.name
        self.addCleanup(lambda: Path(filename).unlink(missing_ok=True))

        self.assertEqual(
            parse_dev_mapper(filename),
            {
                'rootvg-rootlv': 'dm-5',
                'A10_A_datavg-A10_A_datalv': 'dm-7',
            },
        )

    def test_labels_dm_devices_with_their_volume_group_and_logical_volume(self):
        labels = device_mapper_labels(
            [('rootlv', 'rootvg'), ('data-lv', 'data-vg')],
            {
                'rootvg-rootlv': 'dm-5',
                'data--vg-data--lv': 'dm-7',
            },
        )

        self.assertEqual(
            labels,
            {
                'dm-5': 'rootvg/rootlv (dm-5)',
                'dm-7': 'data-vg/data-lv (dm-7)',
            },
        )


if __name__ == '__main__':
    unittest.main()
