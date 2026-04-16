"""File watcher for source changes — pure stdlib polling."""

from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class FileState:
    """Tracks file modification times."""

    _mtimes: dict[str, float] = field(default_factory=dict)

    def snapshot(self, paths: list[Path]) -> None:
        """Take a snapshot of current file mtimes."""
        self._mtimes = {}
        for path in paths:
            if path.exists():
                self._mtimes[str(path)] = path.stat().st_mtime

    def changed_since(self, paths: list[Path]) -> list[Path]:
        """Return paths that changed since last snapshot."""
        changed = []
        for path in paths:
            key = str(path)
            if path.exists():
                mtime = path.stat().st_mtime
                if key not in self._mtimes or self._mtimes[key] != mtime:
                    changed.append(path)
            elif key in self._mtimes:
                changed.append(path)  # file was deleted
        return changed


def get_watch_paths(root: Path) -> list[Path]:
    """Get all paths that should be watched for changes."""
    paths: list[Path] = []

    # Source files
    for pattern in ["source/**/*.md", "source/**/*.toml"]:
        paths.extend(root.glob(pattern))

    # Config
    config = root / ".init-deep.toml"
    if config.exists():
        paths.append(config)

    return sorted(paths)


def watch_loop(
    root: Path,
    build_fn: Callable[[], int],
    interval: float = 1.0,
    on_change: Callable[[list[Path]], None] | None = None,
    max_iterations: int | None = None,
) -> None:
    """Poll for changes and rebuild.

    Args:
        root: project root
        build_fn: function to call on rebuild (no args, returns int)
        interval: seconds between polls
        on_change: callback(changed_paths) called before rebuild
        max_iterations: if set, stop after N iterations (for testing)
    """
    state = FileState()
    watch_paths = get_watch_paths(root)
    state.snapshot(watch_paths)

    print(f"Watching {len(watch_paths)} files for changes (poll every {interval}s)...")
    print("Press Ctrl+C to stop.\n")

    iterations = 0
    try:
        while max_iterations is None or iterations < max_iterations:
            time.sleep(interval)
            iterations += 1

            # Re-scan for new files
            watch_paths = get_watch_paths(root)
            changed = state.changed_since(watch_paths)

            if changed:
                rel_changed = []
                for p in changed:
                    try:
                        rel_changed.append(str(p.relative_to(root)))
                    except ValueError:
                        rel_changed.append(str(p))

                if on_change:
                    on_change(changed)

                print(f"[{time.strftime('%H:%M:%S')}] Changed: {', '.join(rel_changed)}")

                result = build_fn()
                if result == 0:
                    print(f"[{time.strftime('%H:%M:%S')}] Build succeeded.\n")
                else:
                    print(f"[{time.strftime('%H:%M:%S')}] Build failed (exit {result}).\n")

                state.snapshot(watch_paths)
    except KeyboardInterrupt:
        print("\nStopped watching.")
