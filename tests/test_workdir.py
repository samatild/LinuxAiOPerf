"""Regression tests for process-wide working-directory handling."""

import os
import shutil
import tempfile
import unittest

from api.workdir import working_directory


class WorkingDirectoryTests(unittest.TestCase):
    def setUp(self):
        self.anchor = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.anchor)

    def tearDown(self):
        os.chdir(self.original_cwd)
        shutil.rmtree(self.anchor, ignore_errors=True)

    def test_restores_anchor_when_body_raises(self):
        work_dir = tempfile.mkdtemp()
        try:
            with self.assertRaisesRegex(RuntimeError, "upload interrupted"):
                with working_directory(work_dir, restore_to=self.anchor):
                    self.assertEqual(os.getcwd(), work_dir)
                    raise RuntimeError("upload interrupted")
            self.assertEqual(os.getcwd(), self.anchor)
        finally:
            shutil.rmtree(work_dir, ignore_errors=True)

    def test_recovers_when_previous_working_directory_was_deleted(self):
        deleted_dir = tempfile.mkdtemp()
        work_dir = tempfile.mkdtemp()
        try:
            os.chdir(deleted_dir)
            shutil.rmtree(deleted_dir)
            with self.assertRaises(FileNotFoundError):
                os.getcwd()

            with working_directory(work_dir, restore_to=self.anchor):
                self.assertEqual(os.getcwd(), work_dir)

            self.assertEqual(os.getcwd(), self.anchor)
        finally:
            shutil.rmtree(work_dir, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
