import tempfile
import unittest
from pathlib import Path

from scripts.version_manager import inject_readme_version


class VersionManagerReadmeTests(unittest.TestCase):
    def test_updates_release_badge_version_in_readme(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'README.md').write_text('[![Latest Release](https://img.shields.io/badge/release-v2.3.2-blue.svg)](x)\n')
            inject_readme_version('2.3.5', root)
            self.assertIn('release-v2.3.5-blue.svg', (root / 'README.md').read_text())


if __name__ == '__main__':
    unittest.main()
