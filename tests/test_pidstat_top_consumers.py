import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'webapp'))
from domains.procperf.cpu.top_consumers import extract_top_cpu_consumers


class PidstatTopConsumersTests(unittest.TestCase):
    def test_repeated_timestamp_keeps_exact_top_consumer_values(self):
        with tempfile.TemporaryDirectory() as directory:
            Path(directory, 'info.txt').write_text('Start Time: Wed Sep 10 14:54:17 UTC 2025\n')
            source = Path(directory, 'pidstat.txt')
            source.write_text(
                '14:54:20 UID PID %usr %system %guest %wait %CPU CPU Command\n'
                '14:54:20 0 10 3.0 1.0 0.0 2.0 6.0 0 app\n'
                '14:54:20 0 11 4.0 2.0 0.0 1.0 7.0 0 app\n'
                '14:54:21 0 12 5.0 0.5 0.0 3.0 8.5 0 worker\n'
            )
            result = extract_top_cpu_consumers(str(source), top_n=1)

        self.assertEqual(result['timestamps'], ['2025-09-10 14:54:20', '2025-09-10 14:54:21'])
        self.assertEqual(result['top_usr']['worker']['values'], [0, 5.0])
        self.assertEqual(result['top_system']['app']['values'], [2.0, 0])
        self.assertEqual(result['top_wait']['worker']['values'], [0, 3.0])
