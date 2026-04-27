"""
spectrogram.config
==================

Static lookup tables and the :class:`SpectrogramConfig` dataclass.

Edit this file to:
  * Add new station serial-number aliases (``STATION_ALIASES``).
  * Override per-station filter parameters or labels (``STATION_OVERRIDES``).
  * Point to your local StationXML inventory files (``INVENTORY_PATHS``).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


# ---------------------------------------------------------------------------
# Station serial-number → canonical SEED code
# ---------------------------------------------------------------------------

#: Maps raw station IDs stored in MiniSEED headers (hardware serial numbers)
#: to human-readable ``{station, network, location}`` dicts.
#: Add new entries here as you encounter them.
STATION_ALIASES: dict[str, dict[str, str]] = {
    "12166": {"station": "MB01", "network": "1R", "location": "00"},
    "14020": {"station": "MB02", "network": "1R", "location": "00"},
    "19453": {"station": "MB03", "network": "1R", "location": "00"},
    "12446": {"station": "MB04", "network": "1R", "location": "00"},
    "14086": {"station": "BH04", "network": "1R", "location": "00"},
    "19351": {"station": "BH05", "network": "1R", "location": "00"},
    "12668": {"station": "BH05", "network": "1R", "location": "00"},  # active-source exp.
    "20430": {"station": "BH06", "network": "1R", "location": "00"},
}


# ---------------------------------------------------------------------------
# Per-station parameter overrides
# ---------------------------------------------------------------------------

#: Keys must match station codes *after* alias resolution.
#: Any key absent here falls back to the defaults in :class:`SpectrogramConfig`.
STATION_OVERRIDES: dict[str, dict] = {
    "P100": {
        # Nodal sensor — cap high-frequency corner at 20 Hz
        "f3_hz": 20,
        "f4_hz": 20 * 0.90 / 0.85,
        "plot_highfreq": True,
    },
    "FARBX": {
        "f1_hz": 1.0 / (100 * 60),
        "f2_hz": 1.0 / (90 * 60),
    },
    "MONT": {
        # Tide gauge — no instrument response file available
        "f1_hz": 1.0 / (100 * 60),
        "f2_hz": 1.0 / (90 * 60),
        "remove_response": False,
        "plot_highfreq": False,
        "psd_label": "PSD [10log(m²/Hz)] (dB)",
        "waveform_label": "Water level\n(m)",
    },
    "9410": {
        # Strainmeter — no instrument response file available
        "f1_hz": 1.0 / (100 * 60),
        "f2_hz": 1.0 / (90 * 60),
        "remove_response": False,
        "plot_highfreq": False,
        "psd_label": "PSD [10log(strain-rate²/Hz)] (dB)",
        "waveform_label": "Strain-rate\n(strain/s)",
    },
}

#: Network-level overrides (applied before station-level overrides).
NETWORK_OVERRIDES: dict[str, dict] = {
    "BKX": {"plot_highfreq": False},
    "1R":  {"f3_sample_rate_fraction": 0.425, "f4_sample_rate_fraction": 0.45},
    "4E":  {"f3_sample_rate_fraction": 0.425, "f4_sample_rate_fraction": 0.45},
}


# ---------------------------------------------------------------------------
# Inventory / StationXML paths
# ---------------------------------------------------------------------------

#: Map station or network codes to local StationXML files.
#: ``{net}`` and ``{sta}`` are template variables expanded at runtime.
#: Set a value to ``None`` to disable response removal for that entry.
INVENTORY_PATHS: dict[str, Optional[str]] = {
    # Station-specific overrides
    "P100":  None,   # set to "/path/to/station_BVtest.xml"
    "PORGT": None,   # set to "/path/to/station_BVtest.xml"
    # Generic per-network template (used as fallback)
    "BB_template": "/home/bsl/taira/dc6_doc/{net}.info/{net}.FDSN.xml/{net}.{sta}.xml",
}


# ---------------------------------------------------------------------------
# SpectrogramConfig dataclass
# ---------------------------------------------------------------------------

@dataclass
class SpectrogramConfig:
    """
    All parameters controlling a single :func:`~spectrogram.core.calc_spec` run.

    Parameters
    ----------
    fmin : float
        Lower frequency bound used for instrument response removal (Hz).
        Also sets the minimum period displayed in the long-period panel.
    fmax : float
        Upper frequency bound (Hz) — used for labelling only; the actual
        pre-filter corner is derived from the sampling rate.
    vmin : float
        Colour-scale minimum for the spectrogram panels (dB).
    vmax : float
        Colour-scale maximum for the spectrogram panels (dB).
    winlen : float
        Spectrogram window length (seconds).  Longer windows give finer
        frequency resolution at the cost of time resolution.
    plot_highfreq : bool
        Whether to render the high-frequency (> 1 Hz) spectrogram panel.
    pick_harmonics : bool
        Run the harmonic-product-spectrum picker on the spectrogram.
    pick_peak : bool
        Run the parabolic peak picker on the low-frequency spectrogram.
    fmin_pick : float
        Lower frequency bound for peak / harmonic picking (Hz).
    fmax_pick : float
        Upper frequency bound for peak / harmonic picking (Hz).
    fmin_plot : float or None
        If set, apply a zero-phase high-pass display filter to the waveform (Hz).
    fmax_plot : float or None
        If set, apply a zero-phase low-pass display filter to the waveform (Hz).
    t_start : str or None
        If set, trim the stream to this start time before processing.
        Accepts any string that :class:`obspy.UTCDateTime` can parse,
        e.g. ``"2026-01-01T06:00:00"``.
    t_end : str or None
        If set, trim the stream to this end time before processing.
        Accepts any string that :class:`obspy.UTCDateTime` can parse.
    s_threshold : float
        Minimum mean spectrogram power required to attempt harmonic picking (dB).
    nharms : int
        Number of harmonics to include in the harmonic product spectrum.
    sigma_min : float
        Minimum Gaussian width accepted by the harmonic picker (Hz).
    p_peak_min : float
        Minimum peak amplitude accepted by the harmonic picker (dB above noise).
    dpi : int
        Output image resolution (dots per inch).
    path_out : str
        Root directory for output files.  Sub-directories ``Spectrograms/``
        and ``Picks/`` are created automatically.
    fnam_aux : str or None
        Optional path to an auxiliary MiniSEED file plotted on a twin y-axis
        in the waveform panel.
    show_grid : bool
        Draw grid lines on all panels.
    cat : object or None
        An ObsPy :class:`~obspy.core.event.Catalog` of events to mark on
        the plot.  ``None`` disables event annotation.
    """

    fmin: float = 1e-2
    fmax: float = 10.0
    vmin: float = -180.0
    vmax: float = -80.0
    winlen: float = 300.0
    plot_highfreq: bool = True
    pick_harmonics: bool = False
    pick_peak: bool = False
    fmin_pick: float = 0.4
    fmax_pick: float = 1.2
    fmin_plot: Optional[float] = None
    fmax_plot: Optional[float] = None
    t_start: Optional[str] = None
    t_end: Optional[str] = None
    s_threshold: float = -140.0
    nharms: int = 4
    sigma_min: float = 1e-3
    p_peak_min: float = 5.0
    dpi: int = 150
    path_out: str = "output"
    fnam_aux: Optional[str] = None
    show_grid: bool = False
    cat: Optional[object] = None
