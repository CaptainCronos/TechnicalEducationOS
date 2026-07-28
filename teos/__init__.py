"""TechnicalEducationOS public application API."""

__version__ = "0.1.0"

from teos.application import BuildConfig, BuildError, BuildResult, build

__all__ = [
    "BuildConfig",
    "BuildError",
    "BuildResult",
    "__version__",
    "build",
]
