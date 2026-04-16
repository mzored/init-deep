"""New build pipeline using registry + IR."""

from __future__ import annotations

from pathlib import Path

from .compiler import compile_command
from .loader import load_command
from .targets.registry import create_default_registry


def build_v2(
    source_dir: Path,
    selected_targets: list[str] | None = None,
) -> dict[str, str]:
    """Build artifacts using the new registry pipeline.

    Returns dict of relpath -> content, same format as legacy
    ``render_distribution()``.
    """
    spec, body = load_command(source_dir)
    cmd = compile_command(spec, body)

    registry = create_default_registry()
    targets = selected_targets or registry.list_targets()

    outputs: dict[str, str] = {}
    for target_name in targets:
        plugin = registry.get(target_name)
        if plugin is None:
            continue
        for planned in plugin.plan(cmd):
            content = plugin.render(planned, cmd)
            outputs[planned.relpath] = content

    return outputs
