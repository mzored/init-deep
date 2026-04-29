"""Target selection resolution."""

from __future__ import annotations


def resolve_targets(
    available: list[str],
    config_targets: tuple[str, ...],
    only: list[str] | None = None,
    skip: list[str] | None = None,
) -> list[str]:
    """Resolve which targets to generate.

    Precedence: only > skip > config > all available

    Raises ValueError if --only and --skip are both provided.
    Raises ValueError if unknown targets are specified.
    """
    if only and skip:
        raise ValueError("Cannot use --only and --skip together")

    available_set = set(available)

    if only:
        unknown = set(only) - available_set
        if unknown:
            raise ValueError(f"Unknown targets: {', '.join(sorted(unknown))}")
        return sorted(only)

    if config_targets:
        unknown = set(config_targets) - available_set
        if unknown:
            raise ValueError(f"Unknown targets: {', '.join(sorted(unknown))}")

    # Start with config targets or all available
    base = list(config_targets) if config_targets else list(available)

    if skip:
        unknown = set(skip) - available_set
        if unknown:
            raise ValueError(f"Unknown targets: {', '.join(sorted(unknown))}")
        base = [t for t in base if t not in set(skip)]

    return sorted(base)
