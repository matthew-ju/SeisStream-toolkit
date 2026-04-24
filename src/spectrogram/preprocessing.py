"""
spectrogram.preprocessing
==========================

Seismic data pre-processing: station-alias resolution, StationXML inventory
loading, instrument-response removal, and display filtering.
"""

from __future__ import annotations

import logging
import os
from typing import Optional

import obspy
from obspy import Stream, Trace
from obspy import read_inventory
from obspy.core.inventory import Inventory

from .config import STATION_ALIASES, INVENTORY_PATHS

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Station alias resolution
# ---------------------------------------------------------------------------

def resolve_station_alias(tr: Trace) -> Trace:
    """
    Remap raw sensor serial numbers to human-readable SEED station codes.

    Some MiniSEED files store the hardware serial number (e.g. ``"12166"``)
    as the station code rather than the canonical network name (``"MB01"``).
    This function checks :data:`~spectrogram.config.STATION_ALIASES` and
    updates the trace header **in-place** when a match is found.

    Parameters
    ----------
    tr : obspy.Trace
        Trace whose ``stats`` header may need updating.

    Returns
    -------
    obspy.Trace
        The same trace object with updated ``station``, ``network``, and
        ``location`` fields (unchanged if no alias matched).
    """
    alias = STATION_ALIASES.get(tr.stats.station)
    if alias:
        logger.debug(
            "Station alias: %s → %s (net %s)",
            tr.stats.station,
            alias["station"],
            alias["network"],
        )
        tr.stats.station = alias["station"]
        tr.stats.network = alias["network"]
        tr.stats.location = alias["location"]
    return tr


# ---------------------------------------------------------------------------
# Inventory loading
# ---------------------------------------------------------------------------

def load_inventory(
    net: str,
    sta: str,
    loc: str,
    com: str,
    inv_paths: Optional[dict] = None,
) -> Optional[Inventory]:
    """
    Load a StationXML inventory for the given NSLC codes.

    Lookup order:

    1. Direct per-station entry in *inv_paths*.
    2. Generic ``BB_template`` path pattern from *inv_paths*.

    Parameters
    ----------
    net, sta, loc, com : str
        Network, station, location, and channel codes.
    inv_paths : dict or None
        Path mapping; defaults to
        :data:`~spectrogram.config.INVENTORY_PATHS`.

    Returns
    -------
    Inventory or None
        The loaded StationXML inventory, or ``None`` if no file was found.
        A ``None`` return value causes the caller to skip response removal.
    """
    if inv_paths is None:
        inv_paths = INVENTORY_PATHS

    # 1. Direct per-station entry
    path = inv_paths.get(sta)
    if path and os.path.exists(path):
        return read_inventory(path)

    # 2. Generic template
    template = inv_paths.get("BB_template")
    if template:
        path = template.format(net=net, sta=sta, loc=loc, com=com)
        if os.path.exists(path):
            return read_inventory(path)

    logger.warning(
        "No inventory found for %s.%s.%s.%s — response removal disabled.",
        net, sta, loc, com,
    )
    return None


# ---------------------------------------------------------------------------
# Instrument-response removal
# ---------------------------------------------------------------------------

def remove_instrument_response(
    st: Stream,
    inv: Inventory,
    pre_filt: tuple[float, float, float, float],
    output: str = "ACC",
    decimate_factor: Optional[int] = None,
) -> Stream:
    """
    Detrend, taper, optionally decimate, then remove the instrument response.

    Parameters
    ----------
    st : obspy.Stream
        Raw waveform stream (modified **in-place** and also returned).
    inv : obspy.core.inventory.Inventory
        StationXML inventory containing the instrument response.
    pre_filt : tuple of four floats
        Corner frequencies ``(f1, f2, f3, f4)`` in Hz for the cosine taper
        applied during spectral response removal.
    output : str
        Physical unit of the deconvolved trace.
        One of ``"ACC"`` (m/s²), ``"VEL"`` (m/s), or ``"DISP"`` (m).
    decimate_factor : int or None
        Integer decimation factor applied *before* response removal.
        ``None`` skips decimation.

    Returns
    -------
    obspy.Stream
        Processed stream with data in physical units.
    """
    st.detrend("linear")
    st.detrend("demean")
    st.taper(0.01)

    if decimate_factor is not None:
        st.decimate(factor=decimate_factor, strict_length=False)

    st.remove_response(
        pre_filt=pre_filt,
        output=output,
        water_level=None,
        inventory=inv,
    )
    return st


# ---------------------------------------------------------------------------
# Display filter
# ---------------------------------------------------------------------------

def apply_display_filter(
    tr: Trace,
    fmin_plot: Optional[float],
    fmax_plot: Optional[float],
) -> tuple[Trace, bool]:
    """
    Apply an optional band-pass display filter for the waveform panel.

    A **copy** of the input trace is always returned; the original is never
    modified.  Filters are zero-phase to avoid phase distortion in the plot.

    Parameters
    ----------
    tr : obspy.Trace
        Source trace.
    fmin_plot : float or None
        High-pass corner frequency (Hz).  ``None`` skips high-pass filtering.
    fmax_plot : float or None
        Low-pass corner frequency (Hz).  ``None`` skips low-pass filtering.

    Returns
    -------
    tr_filtered : obspy.Trace
        Filtered copy of the input trace.
    was_filtered : bool
        ``True`` if at least one filter was applied.
    """
    tr_filtered = tr.copy()
    was_filtered = False

    if fmin_plot:
        tr_filtered.detrend("linear").detrend("demean").filter(
            "highpass", freq=fmin_plot, zerophase=True
        )
        was_filtered = True

    if fmax_plot:
        tr_filtered.detrend("linear").detrend("demean").filter(
            "lowpass", freq=fmax_plot, zerophase=True
        )
        was_filtered = True

    return tr_filtered, was_filtered
