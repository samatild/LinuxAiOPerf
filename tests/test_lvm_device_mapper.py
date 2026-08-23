import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'webapp'))
from domains.sysconfig.lvm.lvmviz import parse_dev_mapper


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


if __name__ == '__main__':
    unittest.main()
