import tempfile
import unittest
from pathlib import Path

from koff import core


class LocalScaffoldGitignoreTests(unittest.TestCase):
    def test_local_scaffold_respects_simple_gitignore_rules(self) -> None:
        with tempfile.TemporaryDirectory() as sandbox:
            src = Path(sandbox) / "template"
            dest = Path(sandbox) / "output"
            (src / "build").mkdir(parents=True)
            (src / ".gitignore").write_text("*.log\nbuild/\n", encoding="utf-8")
            (src / "keep.txt").write_text("ok", encoding="utf-8")
            (src / "ignored.log").write_text("ignore", encoding="utf-8")
            (src / "build" / "artifact.txt").write_text("ignore-dir", encoding="utf-8")

            core.scaffold_project(str(src), str(dest))

            self.assertTrue((dest / "keep.txt").exists())
            self.assertFalse((dest / "ignored.log").exists())
            self.assertFalse((dest / "build").exists())

    def test_local_scaffold_supports_negation_and_anchored_rules(self) -> None:
        with tempfile.TemporaryDirectory() as sandbox:
            src = Path(sandbox) / "template"
            dest = Path(sandbox) / "output"
            (src / "nested").mkdir(parents=True)
            (src / ".gitignore").write_text(
                "/root.txt\n*.log\n!keep.log\n!nested/keep.log\n",
                encoding="utf-8",
            )
            (src / "root.txt").write_text("ignore-root-only", encoding="utf-8")
            (src / "keep.log").write_text("keep", encoding="utf-8")
            (src / "drop.log").write_text("drop", encoding="utf-8")
            (src / "nested" / "root.txt").write_text("keep-nested-root", encoding="utf-8")
            (src / "nested" / "keep.log").write_text("keep-nested-log", encoding="utf-8")
            (src / "nested" / "drop.log").write_text("drop-nested-log", encoding="utf-8")

            core.scaffold_project(str(src), str(dest))

            self.assertFalse((dest / "root.txt").exists())
            self.assertTrue((dest / "nested" / "root.txt").exists())
            self.assertTrue((dest / "keep.log").exists())
            self.assertTrue((dest / "nested" / "keep.log").exists())
            self.assertFalse((dest / "drop.log").exists())
            self.assertFalse((dest / "nested" / "drop.log").exists())


if __name__ == "__main__":
    unittest.main()
