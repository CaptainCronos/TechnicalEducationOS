"""TechnicalEducationOS public application API."""

__version__ = "1.2.0a1"

from teos.application import BuildConfig, BuildError, BuildResult, build

__all__ = [
    "BuildConfig",
    "BuildError",
    "BuildResult",
    "__version__",
    "build",
]
