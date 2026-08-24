import unittest

from api.capture_health import summarize_capture_health


class CaptureHealthTests(unittest.TestCase):
    def test_summarizes_normalized_load_memory_and_swap_pressure(self):
        summary = summarize_capture_health(
            lscpu='CPU(s):                          8\n',
            sar_load='12:00:01 runq-sz plist-sz ldavg-1 ldavg-5 ldavg-15 blocked\n12:00:02 3 200 4.00 2.00 1.00 1\n',
            meminfo='MemTotal:       16777216 kB\nMemAvailable:    2097152 kB\nSwapTotal:        1048576 kB\nSwapFree:          524288 kB\n',
        )
        self.assertEqual(summary['cpu_count'], 8)
        self.assertEqual(summary['peak_normalized_load_1m'], 0.5)
        self.assertEqual(summary['min_available_memory_bytes'], 2147483648)
        self.assertEqual(summary['peak_swap_used_bytes'], 536870912)

    def test_omits_unavailable_metrics(self):
        self.assertEqual(summarize_capture_health('', '', ''), {})


if __name__ == '__main__':
    unittest.main()
