import os
import tempfile
import unittest

from api.report_metadata import extract_metadata


class ReportMetadataTests(unittest.TestCase):
    def test_extracts_capture_start_end_and_runtime_from_info(self):
        with tempfile.TemporaryDirectory() as work_dir:
            with open(os.path.join(work_dir, 'info.txt'), 'w') as file:
                file.write('Hostname: host-a\nStart Time: Wed Sep 10 14:54:17 UTC 2025\nEnd Time: Wed Sep 10 14:54:55 UTC 2025\nRuntime Info: Quick Data Capture - 30 seconds\n')
            metadata = extract_metadata(work_dir)
        self.assertEqual(metadata['capture_start'], 'Wed Sep 10 14:54:17 UTC 2025')
        self.assertEqual(metadata['capture_end'], 'Wed Sep 10 14:54:55 UTC 2025')
        self.assertEqual(metadata['runtime'], 'Quick Data Capture - 30 seconds')


if __name__ == '__main__':
    unittest.main()
