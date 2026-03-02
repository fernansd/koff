import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from koff import core


class ScaffoldTempDirTests(unittest.TestCase):
    def test_scaffold_project_rejects_temp_dir_that_is_file(self) -> None:
        with tempfile.TemporaryDirectory() as sandbox:
            temp_dir_file = Path(sandbox) / "not-a-dir"
            temp_dir_file.write_text("x", encoding="utf-8")

            with self.assertRaises(NotADirectoryError):
                core.scaffold_project("owner/repo", sandbox, temp_dir=str(temp_dir_file))

    def test_scaffold_project_passes_temp_dir_to_temporary_directory(self) -> None:
        with tempfile.TemporaryDirectory() as sandbox:
            temp_root = Path(sandbox) / "tmp-root"
            destination = Path(sandbox) / "dest"

            with (
                patch("koff.core.tempfile.TemporaryDirectory") as temporary_directory,
                patch("koff.core.subprocess.run") as subprocess_run,
                patch("koff.core.copy_template") as copy_template,
            ):
                temporary_directory.return_value.__enter__.return_value = str(
                    Path(sandbox) / "clone-dir"
                )
                subprocess_run.return_value = None

                core.scaffold_project("owner/repo", str(destination), temp_dir=str(temp_root))

                self.assertTrue(temp_root.is_dir())
                temporary_directory.assert_called_once_with(dir=str(temp_root.resolve()))
                subprocess_run.assert_called_once()
                copy_template.assert_called_once()


if __name__ == "__main__":
    unittest.main()
