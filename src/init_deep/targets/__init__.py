"""Target plugin system for init-deep compiler."""

from .base import (
    Diagnostic,
    PlannedArtifact,
    TargetCapabilities,
    TargetPlugin,
)
from .registry import TargetRegistry, create_default_registry

__all__ = [
    "Diagnostic",
    "PlannedArtifact",
    "TargetCapabilities",
    "TargetPlugin",
    "TargetRegistry",
    "create_default_registry",
]
