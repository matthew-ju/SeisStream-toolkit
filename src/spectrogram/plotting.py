"""
spectrogram.plotting
====================

All matplotlib figure construction and rendering for seismic spectrograms.

The figure layout (left panel = time-series, right panel = mean PSD):

  ┌─────────────────────────────────┐  ┌──┐
  │  ax_waveform   (seismogram)     │  │  │  ax_colorbar
  ├─────────────────────────────────┤  └──┘
  │  ax_highfreq   (f > 1 Hz)  [*] │   ┌──┐
  ├─────────────────────────────────┤  │  │  ax_psd_high [*]
  │  ax_lowfreq    (period 1–1000s) │  ├──┤
  └─────────────────────────────────┘  │  │  ax_psd_low
                                       └──┘
  [*] only drawn when ``plot_highfreq=True``

Public functions
----------------
setup_figure
plot_waveform_panel
plot_spectrogram_panel
apply_period_yticks
plot_psd_sidebar
finalize_figure
mark_catalog_events
"""

from __future__ import annotations

import os
import warnings
from typing import Optional

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.patches as patches
import matplotlib as mpl
from matplotlib.cbook import MatplotlibDeprecationWarning

# ---------------------------------------------------------------------------
# Global rcParams — applied once at import time
# ---------------------------------------------------------------------------
mpl.rcParams["mathtext.default"] = "regular"
mpl.rcParams["agg.path.chunksize"] = 10000
mpl.rc("font",   size=12)
mpl.rc("axes",   titlesize=12, labelsize=14)
mpl.rc("xtick",  labelsize=12)
mpl.rc("ytick",  labelsize=12)
mpl.rc("legend", fontsize=12)
mpl.rc("figure", titlesize=16)


# ---------------------------------------------------------------------------
# Figure layout
# ---------------------------------------------------------------------------

def setup_figure(
    plot_highfreq: bool,
    net: str = "",
) -> tuple[plt.Figure, dict[str, plt.Axes]]:
    """
    Create the multi-panel spectrogram figure.

    Parameters
    ----------
    plot_highfreq : bool
        Whether to include the high-frequency (> 1 Hz) spectrogram panel.
    net : str
        Network code — some networks use slightly wider left margins.

    Returns
    -------
    fig : matplotlib.figure.Figure
    axes : dict
        Keys: ``"waveform"``, ``"lowfreq"``, ``"colorbar"``, ``"psd_low"``
        and, when *plot_highfreq* is True, ``"highfreq"`` and ``"psd_high"``.
    """
    fig = plt.figure(figsize=(16, 8))

    # Slightly wider left margin for certain network codes
    t_left = 0.100 if net in ("1R", "4E") else 0.095
    t_width = 0.675 if net in ("1R", "4E") else 0.68
    p_left = 0.81
    p_width = 0.12

    ax_wave = fig.add_axes([t_left, 0.75, t_width, 0.20])
    ax_cbar = fig.add_axes([0.83,   0.75, 0.03,    0.20])

    axes: dict[str, plt.Axes] = {
        "waveform":  ax_wave,
        "colorbar":  ax_cbar,
    }

    if plot_highfreq:
        ax_hf = fig.add_axes([t_left, 0.42, t_width, 0.30], sharex=ax_wave)
        ax_lf = fig.add_axes([t_left, 0.10, t_width, 0.32], sharex=ax_wave)
        ax_ph = fig.add_axes([p_left, 0.42, p_width, 0.30], sharey=ax_hf)
        ax_pl = fig.add_axes([p_left, 0.10, p_width, 0.32], sharey=ax_lf)
        axes["highfreq"]  = ax_hf
        axes["psd_high"]  = ax_ph
    else:
        ax_lf = fig.add_axes([t_left, 0.10, t_width, 0.62], sharex=ax_wave)
        ax_pl = fig.add_axes([p_left, 0.10, p_width, 0.62], sharey=ax_lf)

    axes["lowfreq"]  = ax_lf
    axes["psd_low"]  = ax_pl

    return fig, axes


# ---------------------------------------------------------------------------
# Waveform panel
# ---------------------------------------------------------------------------

def plot_waveform_panel(
    fig: plt.Figure,
    ax: plt.Axes,
    tr_filtered,
    fmin_plot: Optional[float],
    fmax_plot: Optional[float],
    was_filtered: bool,
    channel_label: str,
    show_grid: bool = False,
) -> None:
    """
    Draw the seismogram waveform onto *ax*.

    Parameters
    ----------
    fig : matplotlib.figure.Figure
        Parent figure (used to place the filter-description annotation).
    ax : matplotlib.axes.Axes
        Target waveform axis.
    tr_filtered : obspy.Trace
        Filtered (or raw) trace to plot.
    fmin_plot, fmax_plot : float or None
        Filter corner frequencies used for the annotation text.
    was_filtered : bool
        Whether a display filter was applied to the trace.
    channel_label : str
        Y-axis label (e.g. ``"Acceleration (m/s²)"``).
    show_grid : bool
        Draw grid lines.
    """
    dates = tr_filtered.times("matplotlib")
    ax.plot(dates, tr_filtered.data, "k", linewidth=0.5)

    # Autoscale to 99.99th percentile to avoid clipping from rare spikes
    ylim = np.percentile(np.abs(tr_filtered.data), q=99.99) * 1.1
    ax.set_ylim(-ylim, ylim)
    ax.set_ylabel(channel_label)

    if show_grid:
        ax.grid(True)

    plt.setp(ax.get_xticklabels(), visible=False)

    # Filter annotation
    if was_filtered:
        label = f"{fmin_plot}–{fmax_plot} Hz band-pass"
    else:
        label = "Raw data"
    ann = fig.text(0.11, 0.92, label)
    ann.set_bbox(dict(facecolor="white", alpha=0.7, edgecolor="white"))


# ---------------------------------------------------------------------------
# Spectrogram panels
# ---------------------------------------------------------------------------

def plot_spectrogram_panel(
    ax: plt.Axes,
    t_dates: np.ndarray,
    f: np.ndarray,
    s_db: np.ndarray,
    vmin: float,
    vmax: float,
    panel: str,
    fmin: float = 1e-2,
    show_grid: bool = False,
) -> None:
    """
    Render a single spectrogram panel using ``pcolormesh``.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        Target axis.
    t_dates : np.ndarray
        Time axis as matplotlib date numbers.
    f : np.ndarray
        Frequency axis (Hz).
    s_db : np.ndarray, shape (n_freq, n_time)
        Spectrogram power (dB).
    vmin, vmax : float
        Colour-scale range (dB).
    panel : str
        ``"highfreq"`` or ``"lowfreq"``.  Controls axis orientation and
        y-axis variable (Hz vs log₁₀ period in seconds).
    fmin : float
        Minimum frequency for the low-frequency panel y-axis limit (Hz).
    show_grid : bool
        Draw grid lines.
    """
    if panel == "highfreq":
        ax.pcolormesh(t_dates, f, s_db, vmin=vmin, vmax=vmax, cmap="plasma", shading="auto")
        ax.set_ylim(1, f[-1])
        ax.set_ylabel("Frequency (Hz)")
        ax.spines["bottom"].set_visible(False)
        plt.setp(ax.get_xticklabels(), visible=False)
    elif panel == "lowfreq":
        ax.pcolormesh(
            t_dates, np.log10(1.0 / f), s_db,
            vmin=vmin, vmax=vmax, cmap="plasma", shading="auto",
        )
        ax.set_ylim(np.log10(1.0 / fmin), 0)
        ax.set_ylabel("Period (s)")
    else:
        raise ValueError(f"panel must be 'highfreq' or 'lowfreq', got '{panel}'")

    if show_grid:
        ax.grid(axis="y", which="major", linewidth=1)
        ax.grid(axis="y", which="minor")
        ax.grid(axis="x")


def apply_period_yticks(ax: plt.Axes, sta: str, net: str) -> None:
    """
    Set human-readable period tick labels on the low-frequency spectrogram axis.

    Tick values are in log₁₀(period/s) — matching the y-axis of the
    low-frequency spectrogram panel.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The low-frequency spectrogram axis.
    sta : str
        Station code (post alias resolution).
    net : str
        Network code.
    """
    if sta == "FARBX":
        ax.set_yticks([1, 2, 3, 4, 5])
        ax.set_yticklabels([1, 10, 100, 1_000, 10_000])
        ax.set_yticks(np.log10([2, 5, 20, 50, 200, 500, 2_000, 5_000]) + 1, minor=True)
        ax.set_yticklabels([2, 5, 20, 50, 200, 500, 2_000, 5_000], minor=True)
    elif sta in ("MONT", "9410"):
        ax.set_yticks([1, 2, 3, 4])
        ax.set_yticklabels([1, 10, 100, 1_000])
        ax.set_yticks(np.log10([2, 5, 20, 50, 200, 500, 2_000]) + 1, minor=True)
        ax.set_yticklabels([2, 5, 20, 50, 200, 500, 2_000], minor=True)
    elif net in ("1R", "4E"):
        ax.set_yticks([1, 2, 3])
        ax.set_yticklabels([1, 10, 100])
        ax.set_yticks(np.log10([2, 5, 20, 50]) + 1, minor=True)
        ax.set_yticklabels([2, 5, 20, 50], minor=True)
    else:
        # Default: 1–1000 s with minor ticks
        ax.set_yticks([0, 1, 2, 3])
        ax.set_yticklabels([1, 10, 100, 1_000])
        ax.set_yticks(np.log10([2, 5, 20, 50, 200, 500]), minor=True)
        ax.set_yticklabels([2, 5, 20, 50, 200, 500], minor=True)


# ---------------------------------------------------------------------------
# PSD sidebar panels
# ---------------------------------------------------------------------------

def plot_psd_sidebar(
    ax: plt.Axes,
    s_db: np.ndarray,
    f: np.ndarray,
    vmin: float,
    vmax: float,
    panel: str,
    sta: str = "",
    net: str = "",
    show_grid: bool = False,
) -> None:
    """
    Plot the mean PSD and the 5th/95th percentiles on a sidebar axis.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        Target sidebar axis.
    s_db : np.ndarray, shape (n_freq, n_time)
        Spectrogram power (dB).
    f : np.ndarray
        Frequency axis (Hz).
    vmin, vmax : float
        X-axis range (dB).
    panel : str
        ``"highfreq"`` or ``"lowfreq"``.
    sta, net : str
        Used to apply per-station y-axis limits on the high-freq panel.
    show_grid : bool
        Draw grid lines.
    """
    mean_psd  = np.mean(s_db, axis=1)
    p05_psd   = np.percentile(s_db, 5,  axis=1)
    p95_psd   = np.percentile(s_db, 95, axis=1)

    if panel == "highfreq":
        ax.plot(mean_psd, f, color="black")
        ax.plot(p05_psd,  f, color="darkgrey", linestyle="--")
        ax.plot(p95_psd,  f, color="darkgrey", linestyle="--")
        ax.set_ylim(1, f[-1])
        if sta == "P100":
            ax.set_ylim(1, 20)
        if net in ("1R", "4E"):
            ax.set_ylim(1, 50)
        ax.spines["bottom"].set_visible(False)
        ax.set_xticklabels([])
    elif panel == "lowfreq":
        log_period = np.log10(1.0 / f)
        ax.plot(mean_psd, log_period, color="black")
        ax.plot(p05_psd,  log_period, color="darkgrey", linestyle="--")
        ax.plot(p95_psd,  log_period, color="darkgrey", linestyle="--")
        apply_period_yticks(ax, sta, net)
    else:
        raise ValueError(f"panel must be 'highfreq' or 'lowfreq', got '{panel}'")

    ax.set_xlim(vmin, vmax)
    ax.yaxis.tick_right()
    ax.yaxis.set_label_position("right")

    if show_grid:
        ax.grid(axis="y", which="major", linewidth=1)
        ax.grid(axis="y", which="minor")
        ax.grid(axis="x")


# ---------------------------------------------------------------------------
# X-axis formatting
# ---------------------------------------------------------------------------

def format_time_axes(
    axes: dict[str, plt.Axes],
    t0_global,
    t1_global,
    plot_highfreq: bool,
) -> None:
    """
    Apply date-based x-axis formatting to all shared time axes.

    Parameters
    ----------
    axes : dict
        Axes dict returned by :func:`setup_figure`.
    t0_global, t1_global : obspy.UTCDateTime
        Global start and end times of the dataset.
    plot_highfreq : bool
        Whether the high-frequency panel exists.
    """
    locator   = mdates.AutoDateLocator(maxticks=20)
    formatter = mdates.DateFormatter("%H:%M")

    ax_wave = axes["waveform"]
    ax_wave.xaxis.set_major_locator(locator)
    ax_wave.xaxis.set_major_formatter(formatter)

    t0_mdate = mdates.date2num(t0_global.datetime)
    t1_mdate = mdates.date2num(t1_global.datetime)
    axes["lowfreq"].set_xlim(t0_mdate, t1_mdate)

    ax_lf = axes["lowfreq"]
    ax_lf.xaxis.set_major_locator(mdates.AutoDateLocator(maxticks=20))
    ax_lf.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    ax_lf.set_xlabel(
        "Hours (UTC) starting {}".format(t0_global.strftime("%Y-%m-%d"))
    )
    plt.setp(ax_lf.get_xticklabels(), rotation=30, ha="right")


# ---------------------------------------------------------------------------
# Catalog event markers
# ---------------------------------------------------------------------------

def mark_catalog_events(
    ax: plt.Axes,
    cat,
    stats,
    ypos: float = 2.9,
    station_lat: float = 54.7,
    station_lon: float = 12.7,
) -> None:
    """
    Draw vertical markers and text annotations for catalog events.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The low-frequency spectrogram axis.
    cat : obspy.core.event.Catalog
        Event catalog.
    stats : obspy.core.trace.Stats
        Trace statistics (starttime / endtime used to filter events).
    ypos : float
        Y position (in axis units) for the event label.
    station_lat, station_lon : float
        Station coordinates used to compute epicentral distances.
    """
    from obspy.geodetics import locations2degrees

    for ev in cat:
        origin = ev.origins[0]
        if not (stats.starttime < origin.time < stats.endtime):
            continue

        dist   = locations2degrees(station_lat, station_lon,
                                   origin.latitude, origin.longitude)
        mag    = ev.magnitudes[0].mag
        region = ev.event_descriptions[0]["text"]
        text   = f"M{mag:.1f}, {dist:.0f}°\n{region}"
        xpos   = mdates.date2num(origin.time.datetime)

        ax.text(
            xpos - 100 / 86400.0, ypos, text,
            color="darkblue", rotation="vertical", fontsize=9,
            verticalalignment="bottom", horizontalalignment="right",
        )
        ax.vlines(xpos, ymin=0, ymax=4, color="darkblue",
                  linestyle="dashed", linewidth=2)


# ---------------------------------------------------------------------------
# Save figure
# ---------------------------------------------------------------------------

def save_figure(
    fig: plt.Figure,
    axes: dict[str, plt.Axes],
    psd_mappable,
    psd_label: str,
    vmin: float,
    vmax: float,
    path_out: str,
    filename: str,
    dpi: int,
    trace_id: str,
    t0_global,
    t1_global,
) -> None:
    """
    Add the colorbar, figure title, and write the PNG to disk.

    Parameters
    ----------
    fig : matplotlib.figure.Figure
    axes : dict
        Axes dict from :func:`setup_figure`.
    psd_mappable : matplotlib.cm.ScalarMappable
        Mappable returned by the final ``pcolormesh`` call (used for colorbar).
    psd_label : str
        Y-axis label for the colorbar (e.g. ``"PSD (dB)"``).
    vmin, vmax : float
        Colorbar range.
    path_out : str
        Root output directory.
    filename : str
        PNG filename (no directory prefix).
    dpi : int
        Image resolution.
    trace_id : str
        SEED trace ID for the figure title.
    t0_global, t1_global : obspy.UTCDateTime
        Data window start and end (used in title).
    """
    # Colorbar
    cb = plt.colorbar(mappable=psd_mappable, cax=axes["colorbar"])
    axes["colorbar"].set_ylabel(psd_label)
    dv = 20
    cb.set_ticks(np.arange(vmin, vmax + dv / 10, step=dv))

    # Title
    fig.suptitle(
        "{id}  {t0} — {t1}".format(
            id=trace_id,
            t0=t0_global.strftime("%Y/%m/%d %H:%M:%S"),
            t1=t1_global.strftime("%Y/%m/%d %H:%M:%S"),
        )
    )

    out_path = os.path.join(path_out, "Spectrograms", filename)
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=MatplotlibDeprecationWarning)
        fig.savefig(out_path, dpi=dpi)

    plt.close(fig)
