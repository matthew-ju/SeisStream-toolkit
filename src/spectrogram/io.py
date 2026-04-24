"""
spectrogram.io
==============

File I/O helpers: output-directory creation, PNG filename generation, and
spectral-pick writing.
"""

from __future__ import annotations

import os

import numpy as np
from obspy import UTCDateTime


def ensure_output_dirs(path_out: str) -> None:
    """
    Create the ``Spectrograms/`` and ``Picks/`` output sub-directories.

    Parameters
    ----------
    path_out : str
        Root output directory.  Created if it does not already exist.
    """
    os.makedirs(os.path.join(path_out, "Spectrograms"), exist_ok=True)


def build_output_filename(trace_id: str, starttime: UTCDateTime) -> str:
    """
    Build a standardised PNG filename for a spectrogram plot.

    The format is ``<NET.STA.LOC.CHA>_YYYY_MM_DD_HH.png``.

    Parameters
    ----------
    trace_id : str
        SEED trace identifier (e.g. ``"BB.DARS1.00.BHZ"``).
    starttime : obspy.UTCDateTime
        Start time of the data window.

    Returns
    -------
    str
        Filename string (no directory prefix).

    Examples
    --------
    >>> from obspy import UTCDateTime
    >>> build_output_filename("BB.DARS1.00.BHZ", UTCDateTime("2015-02-08"))
    'BB.DARS1.00.BHZ_2015_02_08_00.png'
    """
    return "{id}_{y:04d}_{m:02d}_{d:02d}_{h:02d}.png".format(
        id=trace_id,
        y=starttime.year,
        m=starttime.month,
        d=starttime.day,
        h=starttime.hour,
    )


def write_picks(
    path: str,
    times: list[float],
    vals: list[np.ndarray],
    stats: object,
    header: str,
) -> None:
    """
    Write spectral-peak picks to a plain-text file.

    One line per pick, with the absolute UTC timestamp followed by
    the measured values separated by spaces.

    Parameters
    ----------
    path : str
        Output directory (must already exist).
    times : list of float
        Pick times in seconds relative to ``stats.starttime``.
    vals : list of array-like
        One array per measured quantity (e.g. peak period, displacement).
        Each array must have the same length as *times*.
    stats : obspy.core.trace.Stats
        Trace statistics used to resolve absolute timestamps and build
        the output filename.
    header : str
        Single-line column description written as a ``#`` comment at the
        top of the output file.
    """
    os.makedirs(path, exist_ok=True)
    filename = os.path.join(
        path, "picks_{sta}_{chan}.txt".format(sta=stats.station, chan=stats.channel)
    )
    vals_array = np.asarray(vals)
    with open(filename, "w") as fid:
        fid.write("# " + header + "\n")
        for i, t in enumerate(times):
            abs_time = stats.starttime + t
            row = np.array2string(vals_array[:, i], precision=4, max_line_width=255)
            fid.write("{t} {v}\n".format(t=abs_time, v=row[1:-1]))
