"""
spectrogram
===========

A Python package for computing and plotting seismic spectrograms from MiniSEED
waveform data.

Public API
----------
calc_spec : callable
    Main entry point — compute and save a spectrogram from a single file.
SpectrogramConfig : dataclass
    All tunable parameters for a ``calc_spec`` run.

Example
-------
>>> from spectrogram import calc_spec, SpectrogramConfig
>>> cfg = SpectrogramConfig(vmin=-160, vmax=-60, winlen=600)
>>> calc_spec("data.mseed", cfg=cfg)
"""

from .config import SpectrogramConfig
from .core import calc_spec

__all__ = ["calc_spec", "SpectrogramConfig"]
