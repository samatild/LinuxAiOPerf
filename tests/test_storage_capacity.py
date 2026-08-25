import unittest

from api.storage_capacity import summarize_filesystems


class StorageCapacityTests(unittest.TestCase):
    def test_keeps_real_mounts_and_marks_capacity_severity(self):
        rows = summarize_filesystems(
            'Filesystem Size Used Avail Use% Mounted on\n'
            '/dev/sda1 100G 92G 8G 92% /\n'
            'tmpfs 1G 1G 0 100% /run\n'
            '/dev/loop0 50M 50M 0 100% /snap/core\n'
        )
        self.assertEqual(rows, [{
            'filesystem': '/dev/sda1', 'size': '100G', 'used': '92G', 'available': '8G',
            'use_percent': 92, 'mount': '/', 'severity': 'warning',
        }])

    def test_uses_critical_threshold_at_95_percent(self):
        rows = summarize_filesystems('Filesystem Size Used Avail Use% Mounted on\n/dev/x 10G 10G 0 95% /data\n')
        self.assertEqual(rows[0]['severity'], 'critical')

    def test_uses_warning_threshold_at_85_percent(self):
        rows = summarize_filesystems('Filesystem Size Used Avail Use% Mounted on\n/dev/x 10G 8.5G 1.5G 85% /data\n')
        self.assertEqual(rows[0]['severity'], 'warning')


if __name__ == '__main__':
    unittest.main()
