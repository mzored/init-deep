"""Allow running init-deep as ``python -m init_deep``."""

from .cli import main

raise SystemExit(main())
