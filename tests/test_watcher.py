"""Tests for the file watcher module."""

from __future__ import annotations

import os
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import MagicMock

from src.init_deep.watcher import FileState, get_watch_paths, watch_loop


class TestFileState(unittest.TestCase):
    """Tests for FileState mtime tracking."""

    def setUp(self) -> None:
        self.tmpdir = tempfile.mkdtemp()
        self.file_a = Path(self.tmpdir) / "a.md"
        self.file_b = Path(self.tmpdir) / "b.md"
        self.file_a.write_text("hello", encoding="utf-8")
        self.file_b.write_text("world", encoding="utf-8")

    def tearDown(self) -> None:
        import shutil

        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_snapshot_captures_mtimes(self) -> None:
        state = FileState()
        paths = [self.file_a, self.file_b]
        state.snapshot(paths)
        self.assertEqual(len(state._mtimes), 2)
        self.assertIn(str(self.file_a), state._mtimes)
        self.assertIn(str(self.file_b), state._mtimes)

    def test_changed_since_detects_mtime_change(self) -> None:
        state = FileState()
        paths = [self.file_a, self.file_b]
        state.snapshot(paths)

        # Ensure mtime actually changes (some filesystems have 1s granularity)
        time.sleep(0.05)
        self.file_a.write_text("updated", encoding="utf-8")
        # Force a different mtime by using os.utime
        new_mtime = self.file_a.stat().st_mtime + 1
        os.utime(self.file_a, (new_mtime, new_mtime))

        changed = state.changed_since(paths)
        self.assertEqual(changed, [self.file_a])

    def test_changed_since_detects_deleted_file(self) -> None:
        state = FileState()
        paths = [self.file_a, self.file_b]
        state.snapshot(paths)

        self.file_b.unlink()
        changed = state.changed_since(paths)
        self.assertEqual(changed, [self.file_b])

    def test_changed_since_returns_empty_for_unchanged(self) -> None:
        state = FileState()
        paths = [self.file_a, self.file_b]
        state.snapshot(paths)

        changed = state.changed_since(paths)
        self.assertEqual(changed, [])

    def test_changed_since_detects_new_file(self) -> None:
        state = FileState()
        paths = [self.file_a]
        state.snapshot(paths)

        new_file = Path(self.tmpdir) / "c.md"
        new_file.write_text("new", encoding="utf-8")

        changed = state.changed_since([self.file_a, new_file])
        self.assertEqual(changed, [new_file])


class TestGetWatchPaths(unittest.TestCase):
    """Tests for get_watch_paths discovery."""

    def setUp(self) -> None:
        self.tmpdir = tempfile.mkdtemp()
        self.root = Path(self.tmpdir)
        # Create source structure
        (self.root / "source" / "init-deep").mkdir(parents=True)
        (self.root / "source" / "init-deep" / "canonical.md").write_text(
            "# test", encoding="utf-8"
        )
        (self.root / "source" / "init-deep" / "spec.toml").write_text(
            "[test]", encoding="utf-8"
        )

    def tearDown(self) -> None:
        import shutil

        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_finds_source_md_files(self) -> None:
        paths = get_watch_paths(self.root)
        names = [p.name for p in paths]
        self.assertIn("canonical.md", names)

    def test_finds_source_toml_files(self) -> None:
        paths = get_watch_paths(self.root)
        names = [p.name for p in paths]
        self.assertIn("spec.toml", names)

    def test_includes_config_when_present(self) -> None:
        config = self.root / ".init-deep.toml"
        config.write_text("[targets]", encoding="utf-8")
        paths = get_watch_paths(self.root)
        self.assertIn(config, paths)

    def test_excludes_config_when_absent(self) -> None:
        paths = get_watch_paths(self.root)
        config = self.root / ".init-deep.toml"
        self.assertNotIn(config, paths)


class TestWatchLoop(unittest.TestCase):
    """Tests for the watch_loop polling loop."""

    def test_max_iterations_limits_loop(self) -> None:
        """watch_loop with max_iterations=1 runs exactly one poll cycle."""
        tmpdir = tempfile.mkdtemp()
        root = Path(tmpdir)
        (root / "source" / "init-deep").mkdir(parents=True)
        (root / "source" / "init-deep" / "canonical.md").write_text(
            "# test", encoding="utf-8"
        )

        build_fn = MagicMock(return_value=0)
        watch_loop(root, build_fn, interval=0.01, max_iterations=1)

        # No changes happened, so build_fn should not be called
        build_fn.assert_not_called()

        import shutil

        shutil.rmtree(tmpdir, ignore_errors=True)

    def test_on_change_callback(self) -> None:
        """on_change callback is invoked when files change."""
        tmpdir = tempfile.mkdtemp()
        root = Path(tmpdir)
        (root / "source" / "init-deep").mkdir(parents=True)
        src_file = root / "source" / "init-deep" / "canonical.md"
        src_file.write_text("# test", encoding="utf-8")

        # Set the file to a past mtime so the snapshot captures it
        past_mtime = src_file.stat().st_mtime - 10
        os.utime(src_file, (past_mtime, past_mtime))

        build_fn = MagicMock(return_value=0)
        callback = MagicMock()

        # Use a custom on_change that also verifies the changed path
        changed_paths: list[Path] = []

        def track_change(paths: list[Path]) -> None:
            changed_paths.extend(paths)

        # Patch watch_loop's sleep to modify the file during the first iteration
        original_sleep = time.sleep

        def fake_sleep(seconds: float) -> None:
            # Bump the mtime forward so the poll detects a change
            os.utime(src_file, (past_mtime + 20, past_mtime + 20))
            original_sleep(0.001)

        import unittest.mock

        with unittest.mock.patch("src.init_deep.watcher.time.sleep", fake_sleep):
            watch_loop(
                root,
                build_fn,
                interval=0.01,
                on_change=track_change,
                max_iterations=1,
            )

        self.assertEqual(len(changed_paths), 1)
        self.assertEqual(changed_paths[0], src_file)
        build_fn.assert_called_once()

        import shutil

        shutil.rmtree(tmpdir, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
