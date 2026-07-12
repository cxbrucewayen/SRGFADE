"""Public interface for the SRGFADE optimizer."""

from .base import BaseAlgorithm, OptimizationResult
from .core import SRGFADE

__all__ = ["BaseAlgorithm", "OptimizationResult", "SRGFADE"]
__version__ = "1.0.0"
