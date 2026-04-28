"""
spectrogram.config
==================

Static lookup tables and the :class:`SpectrogramConfig` dataclass.

This module now dynamically loads configuration from `configs/config.yaml`.
"""

from __future__ import annotations

import os
import yaml
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

# Path to the central YAML configuration file
CONFIG_PATH = Path(__file__).resolve().parent.parent.parent / "configs" / "config.yaml"

def _load_config() -> dict:
    if not CONFIG_PATH.exists():
        return {}
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}

_raw_config = _load_config()

# ---------------------------------------------------------------------------
# Loaded configurations
# ---------------------------------------------------------------------------

STATION_ALIASES: dict[str, dict[str, str]] = _raw_config.get("station_aliases", {})
STATION_OVERRIDES: dict[str, dict] = _raw_config.get("station_overrides", {})
NETWORK_OVERRIDES: dict[str, dict] = _raw_config.get("network_overrides", {})
INVENTORY_PATHS: dict[str, Optional[str]] = _raw_config.get("inventory_paths", {})

_defaults = _raw_config.get("defaults", {})

# ---------------------------------------------------------------------------
# SpectrogramConfig dataclass
# ---------------------------------------------------------------------------

@dataclass
class SpectrogramConfig:
    """
    All parameters controlling a single :func:`~spectrogram.core.calc_spec` run.
    Defaults are loaded dynamically from configs/config.yaml.
    """

    fmin: float = _defaults.get("fmin", 1e-2)
    fmax: float = _defaults.get("fmax", 10.0)
    vmin: float = _defaults.get("vmin", -180.0)
    vmax: float = _defaults.get("vmax", -80.0)
    winlen: float = _defaults.get("winlen", 300.0)
    plot_highfreq: bool = _defaults.get("plot_highfreq", True)
    pick_harmonics: bool = _defaults.get("pick_harmonics", False)
    pick_peak: bool = _defaults.get("pick_peak", False)
    fmin_pick: float = _defaults.get("fmin_pick", 0.4)
    fmax_pick: float = _defaults.get("fmax_pick", 1.2)
    fmin_plot: Optional[float] = _defaults.get("fmin_plot", None)
    fmax_plot: Optional[float] = _defaults.get("fmax_plot", None)
    t_start: Optional[str] = _defaults.get("t_start", None)
    t_end: Optional[str] = _defaults.get("t_end", None)
    s_threshold: float = _defaults.get("s_threshold", -140.0)
    nharms: int = _defaults.get("nharms", 4)
    sigma_min: float = _defaults.get("sigma_min", 1e-3)
    p_peak_min: float = _defaults.get("p_peak_min", 5.0)
    dpi: int = _defaults.get("dpi", 150)
    path_out: str = _defaults.get("path_out", "output")
    fnam_aux: Optional[str] = _defaults.get("fnam_aux", None)
    show_grid: bool = _defaults.get("show_grid", False)
    cat: Optional[object] = None
