from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'webapp'))
from domains.sysconfig.lvm.lvmviz import relabel_iostat_figures


class IostatDeviceLabelsTests(unittest.TestCase):
    def test_relabels_only_mapped_dm_devices_in_titles_and_legends(self):
        figures = [{
            'layout': {'title': {'text': 'Disk Metrics - dm-5'}},
            'data': [{'name': 'dm-5'}, {'name': 'sda'}],
        }]

        relabel_iostat_figures(figures, {'dm-5': 'rootvg/rootlv (dm-5)'})

        self.assertEqual(
            figures[0]['layout']['title']['text'],
            'Disk Metrics - rootvg/rootlv (dm-5)',
        )
        self.assertEqual(figures[0]['data'][0]['name'], 'rootvg/rootlv (dm-5)')
        self.assertEqual(figures[0]['data'][1]['name'], 'sda')


if __name__ == '__main__':
    unittest.main()
