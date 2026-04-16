"""Generate project metadata from the target registry."""

from __future__ import annotations

from .targets.registry import create_default_registry


def generate_support_matrix(registry=None) -> str:
    """Generate a markdown support matrix table from the registry."""
    if registry is None:
        registry = create_default_registry()

    lines = [
        "| Platform | Primary Surface | Skills | Workflows | Commands |",
        "|----------|----------------|--------|-----------|----------|",
    ]
    for name in registry.list_targets():
        plugin = registry.get(name)
        caps = plugin.capabilities()
        lines.append(
            f"| {name.capitalize()} "
            f"| {caps.recommended_primary_surface or 'N/A'} "
            f"| {'Yes' if caps.supports_skills else 'No'} "
            f"| {'Yes' if caps.supports_workflows else 'No'} "
            f"| {'Yes' if caps.supports_commands else 'No'} |"
        )
    return "\n".join(lines) + "\n"


def generate_gitattributes_entries(outputs: dict[str, str]) -> str:
    """Generate .gitattributes entries for generated artifacts.

    Args:
        outputs: dict of relpath -> content from build pipeline
    """
    lines = ["# Generated artifacts — collapsed in GitHub diffs"]
    for relpath in sorted(outputs.keys()):
        lines.append(f"{relpath} linguist-generated=true")
    return "\n".join(lines) + "\n"


def generate_managed_paths_list(outputs: dict[str, str]) -> list[str]:
    """Generate sorted list of managed artifact paths."""
    return sorted(outputs.keys())


def generate_target_summary(registry=None) -> str:
    """Generate a human-readable target summary."""
    if registry is None:
        registry = create_default_registry()

    lines = []
    for name in registry.list_targets():
        plugin = registry.get(name)
        caps = plugin.capabilities()
        shared = (
            ", ".join(caps.shared_standard_docs)
            if caps.shared_standard_docs
            else "none"
        )
        lines.append(
            f"- **{name.capitalize()}**: "
            f"primary={caps.recommended_primary_surface}, "
            f"shared_docs={shared}"
        )
    return "\n".join(lines) + "\n"
