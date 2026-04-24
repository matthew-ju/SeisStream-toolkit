"""
spectrogram.core
================

Main entry point for computing and plotting seismic spectrograms.

Usage
-----
::

    from spectrogram import calc_spec, SpectrogramConfig

    cfg = SpectrogramConfig(vmin=-160, vmax=-60, winlen=600)
    f, t, s = calc_spec("waveform.mseed", cfg=cfg)
"""

from __future__ import annotations

import logging
from typing import Optional

import numpy as np
import obspy
import matplotlib.dates as mdates
from matplotlib.mlab import specgram

from .config import (
    SpectrogramConfig,
    STATION_OVERRIDES,
    NETWORK_OVERRIDES,
    INVENTORY_PATHS,
)
from .preprocessing import (
    resolve_station_alias,
    load_inventory,
    remove_instrument_response,
    apply_display_filter,
)
from .plotting import (
    setup_figure,
    plot_waveform_panel,
    plot_spectrogram_panel,
    apply_period_yticks,
    plot_psd_sidebar,
    format_time_axes,
    mark_catalog_events,
    save_figure,
)
from .io import ensure_output_dirs, build_output_filename
from .analysis import pick_spectrogram_peaks, pick_longperiod_windows

logger = logging.getLogger(__name__)


def calc_spec(
    fnam_smgr: str,
    cfg: Optional[SpectrogramConfig] = None,
    **kwargs,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Compute and save a multi-panel spectrogram plot from a MiniSEED file.

    The output PNG is written to ``<cfg.path_out>/Spectrograms/``.

    Parameters
    ----------
    fnam_smgr : str
        Path to the input MiniSEED waveform file (anything ObsPy can read).
    cfg : SpectrogramConfig or None
        Run configuration.  Any parameter in :class:`~spectrogram.config.SpectrogramConfig`
        can also be supplied as a keyword argument and will override the config
        value.  If ``None``, all defaults are used.
    **kwargs
        Keyword overrides for individual :class:`SpectrogramConfig` fields.

    Returns
    -------
    f : np.ndarray
        Frequency axis of the last computed spectrogram (Hz).
    t : np.ndarray
        Time axis of the last computed spectrogram (seconds from trace start).
    s : np.ndarray
        Power spectral density of the last computed spectrogram (m²/Hz or
        equivalent, depending on instrument response removal settings).

    Notes
    -----
    When the input stream contains multiple traces (i.e. the data has gaps),
    each trace is rendered separately so that genuine gaps appear as blank
    space in the plot.
    """
    if cfg is None:
        cfg = SpectrogramConfig()

    # Apply keyword overrides
    for key, value in kwargs.items():
        if hasattr(cfg, key):
            setattr(cfg, key, value)
        else:
            logger.warning("Unknown SpectrogramConfig field ignored: '%s'", key)

    # ------------------------------------------------------------------
    # Load stream and resolve metadata
    # ------------------------------------------------------------------
    st = obspy.read(fnam_smgr)

    # Resolve station alias for every trace
    for tr in st:
        resolve_station_alias(tr)

    # Derive NSLC from the first trace (all traces share the same channel)
    tr0 = st[0]
    net, sta, loc, com = tr0.id.split(".")

    logger.info("Processing %s  (%d trace(s))", tr0.id, len(st))

    # ------------------------------------------------------------------
    # Apply per-station / per-network config overrides
    # ------------------------------------------------------------------
    net_overrides = NETWORK_OVERRIDES.get(net, {})
    sta_overrides = STATION_OVERRIDES.get(sta, {})

    # Allow overrides to mutate cfg fields by name
    for overrides in (net_overrides, sta_overrides):
        for key, value in overrides.items():
            if hasattr(cfg, key):
                setattr(cfg, key, value)

    # Compute the pre-filter corner frequencies from the sampling rate.
    # These are the cosine-taper corners used during response removal:
    #   f1  —  very low; protects against amplification near DC
    #   f2  —  low; response removal starts here
    #   f3  —  high; response removal tapers off (≈ 0.85 × Nyquist)
    #   f4  —  very high; (≈ 0.90 × Nyquist)
    fs = tr0.stats.sampling_rate
    f1 = sta_overrides.get("f1_hz", net_overrides.get("f1_hz", 5e-4))
    f2 = sta_overrides.get("f2_hz", net_overrides.get("f2_hz", 1e-3))
    f3 = sta_overrides.get("f3_hz", int(fs * 0.5 * 0.85))
    f4 = sta_overrides.get("f4_hz", int(fs * 0.5 * 0.90))
    pre_filt = (f1, f2, f3, f4)

    remove_response = sta_overrides.get("remove_response", True)
    output_unit     = "ACC"
    psd_label_long  = sta_overrides.get("psd_label",      "PSD [10log(m²/s⁴/Hz)] (dB)")
    psd_label_short = "PSD"
    waveform_label  = sta_overrides.get("waveform_label", "Acceleration\n(m/s²)")

    logger.debug("pre_filt = %s", pre_filt)

    # ------------------------------------------------------------------
    # Instrument response removal
    # ------------------------------------------------------------------
    if remove_response:
        inv = load_inventory(net, sta, loc, com, INVENTORY_PATHS)
        if inv is not None:
            logger.info("Removing instrument response → %s", output_unit)
            st = remove_instrument_response(st, inv, pre_filt, output=output_unit)
            st.detrend("linear").detrend("demean").taper(0.01)
        else:
            logger.warning("Skipping response removal (no inventory found).")

    # ------------------------------------------------------------------
    # Timeline and output paths
    # ------------------------------------------------------------------
    t0_global = min(tr.stats.starttime for tr in st)
    t1_global = max(tr.stats.endtime   for tr in st)

    # Some stations record one extra leading sample — trim it
    for tr in st:
        tr.stats.starttime += 1

    ensure_output_dirs(cfg.path_out)
    output_filename = build_output_filename(tr0.id, t0_global)

    # ------------------------------------------------------------------
    # Figure canvas (created once; traces drawn on top in a loop)
    # ------------------------------------------------------------------
    fig, axes = setup_figure(cfg.plot_highfreq, net=net)

    # Track the last spectrogram arrays across the loop for the return value
    f_out: np.ndarray = np.array([])
    t_out: np.ndarray = np.array([])
    s_out: np.ndarray = np.array([])
    last_mappable = None  # pcolormesh handle for the colorbar

    # ------------------------------------------------------------------
    # Per-trace loop — preserves genuine data gaps as blank regions
    # ------------------------------------------------------------------
    for tr in st:
        nfft = int(cfg.winlen * tr.stats.sampling_rate)

        # --- Waveform panel ---
        tr_filtered, was_filtered = apply_display_filter(
            tr, cfg.fmin_plot, cfg.fmax_plot
        )
        plot_waveform_panel(
            fig, axes["waveform"],
            tr_filtered,
            cfg.fmin_plot, cfg.fmax_plot, was_filtered,
            channel_label=waveform_label,
            show_grid=cfg.show_grid,
        )

        if len(tr.data) < nfft:
            logger.warning(
                "Trace too short for spectrogram (%d samples, need %d) — skipped.",
                len(tr.data), nfft,
            )
            continue

        # --- Spectrogram computation ---
        s, f, t = specgram(
            tr.data,
            Fs=tr.stats.sampling_rate,
            NFFT=nfft,
            noverlap=nfft // 2,
        )

        # Avoid log10(0) by adding a negligible floor to the frequency axis
        f = f + 1e-15

        # Convert relative time axis to absolute matplotlib date numbers
        t0_mdate = mdates.date2num(tr.stats.starttime.datetime)
        t_dates  = t0_mdate + t / 86400.0   # seconds → fractional days

        s_db = 10.0 * np.log10(s)

        # --- High-frequency spectrogram (optional) ---
        if cfg.plot_highfreq:
            plot_spectrogram_panel(
                axes["highfreq"], t_dates, f, s_db,
                cfg.vmin, cfg.vmax, panel="highfreq",
                show_grid=cfg.show_grid,
            )
            plot_psd_sidebar(
                axes["psd_high"], s_db, f, cfg.vmin, cfg.vmax,
                panel="highfreq", sta=sta, net=net, show_grid=cfg.show_grid,
            )

            if cfg.pick_harmonics:
                pick_times, pick_freqs, pick_vals, _ = pick_spectrogram_peaks(
                    f, t, s_db,
                    fwin=(cfg.fmin_pick, cfg.fmax_pick),
                    winlen=cfg.winlen,
                    sigma_min=cfg.sigma_min,
                    p_peak_min=cfg.p_peak_min,
                    s_threshold=cfg.s_threshold,
                    nharms=cfg.nharms,
                )
                for pt, pf in zip(pick_times, pick_freqs):
                    axes["highfreq"].plot(
                        t0_mdate + pt / 86400.0, pf, "ko", alpha=0.2
                    )

        # --- Low-frequency spectrogram ---
        im = axes["lowfreq"].pcolormesh(
            t_dates, np.log10(1.0 / f), s_db,
            vmin=cfg.vmin, vmax=cfg.vmax, cmap="plasma", shading="auto",
        )
        last_mappable = im

        axes["lowfreq"].set_ylim(np.log10(1.0 / cfg.fmin), 0)
        apply_period_yticks(axes["lowfreq"], sta, net)
        if cfg.show_grid:
            axes["lowfreq"].grid(axis="y", which="major", linewidth=1)
            axes["lowfreq"].grid(axis="y", which="minor")
            axes["lowfreq"].grid(axis="x")

        if cfg.plot_highfreq:
            axes["lowfreq"].spines["top"].set_visible(False)

        # --- Low-frequency PSD sidebar ---
        plot_psd_sidebar(
            axes["psd_low"], s_db, f, cfg.vmin, cfg.vmax,
            panel="lowfreq", sta=sta, net=net, show_grid=cfg.show_grid,
        )

        if cfg.plot_highfreq:
            axes["psd_high"].spines["bottom"].set_visible(False)

        # --- Event catalog markers ---
        if cfg.cat:
            mark_catalog_events(axes["lowfreq"], cfg.cat, tr.stats)

        # Save last spectrogram for return value
        f_out, t_out, s_out = f, t, s

    # ------------------------------------------------------------------
    # Finalise: x-axis ticks, colorbar, title, save
    # ------------------------------------------------------------------
    format_time_axes(axes, t0_global, t1_global, cfg.plot_highfreq)

    if last_mappable is not None:
        save_figure(
            fig, axes,
            psd_mappable=last_mappable,
            psd_label=psd_label_short,
            vmin=cfg.vmin, vmax=cfg.vmax,
            path_out=cfg.path_out,
            filename=output_filename,
            dpi=cfg.dpi,
            trace_id=tr0.id,
            t0_global=t0_global,
            t1_global=t1_global,
        )
        logger.info("Saved → %s/Spectrograms/%s", cfg.path_out, output_filename)
    else:
        logger.error("No spectrogram data was rendered — output file not saved.")

    return f_out, t_out, s_out
