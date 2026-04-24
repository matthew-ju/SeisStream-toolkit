"""
spectrogram.analysis
====================

Spectral analysis algorithms used on top of the computed spectrogram:

* :func:`harmonic_product_spectrum` — fundamental frequency estimation via HPS.
* :func:`pick_spectrogram_peaks` — time-series of harmonic peak picks.
* :func:`pick_longperiod_windows` — detect elevated long-period noise windows.
* :func:`integrate_displacement` — integrate spectral power to estimate displacement.

This module consolidates the legacy ``harmonics.py`` and the analysis helpers
scattered throughout ``calc_spec_utils.py``.

.. note::
    The deprecated ``scipy.fftpack.convolve`` import used in the original
    ``harmonics.py`` has been replaced with the modern ``scipy.signal.convolve``.
"""

from __future__ import annotations

from typing import Optional

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
from obspy.signal.util import next_pow_2
from scipy.signal import decimate, detrend, convolve   # scipy.signal — not deprecated fftpack
from scipy.optimize import minimize


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _gaussian(
    x: np.ndarray,
    center: float,
    amplitude: float,
    sigma: float,
) -> np.ndarray:
    """Evaluate a Gaussian with the given centre, amplitude, and width."""
    return amplitude * np.exp(-((x - center) ** 2) / (2 * sigma) ** 2)


def _gaussian_misfit(params: np.ndarray, f: np.ndarray, s: np.ndarray) -> float:
    """L2 norm of the residual between a Gaussian model and spectral data."""
    return float(np.sqrt(np.sum((_gaussian(f, *params) - s) ** 2)))


# ---------------------------------------------------------------------------
# Harmonic Product Spectrum
# ---------------------------------------------------------------------------

def harmonic_product_spectrum(
    f: np.ndarray,
    power: np.ndarray,
    fwin_pick: tuple[float, float],
    nharms: int = 6,
    f_prop: float = -1.0,
    plot: bool = False,
) -> tuple[float, float, float]:
    """
    Estimate the fundamental frequency using the Harmonic Product Spectrum (HPS).

    The HPS enhances harmonic structures by accumulating decimated copies of
    the power spectrum.  A Gaussian is then fitted around the resulting peak
    to refine the frequency estimate and measure peak width.

    Parameters
    ----------
    f : np.ndarray, shape (n_freq,)
        Frequency axis in Hz.
    power : np.ndarray, shape (n_freq,)
        Power spectral density in dB.
    fwin_pick : tuple of (float, float)
        Frequency search window ``(fmin, fmax)`` in Hz.
    nharms : int
        Number of harmonics to accumulate (minimum 2).
    f_prop : float
        Propagated frequency estimate from the previous time window.
        If it falls within *fwin_pick*, it seeds the Gaussian fit instead
        of the spectral maximum.
    plot : bool
        Open a diagnostic matplotlib figure.

    Returns
    -------
    f_peak : float
        Estimated fundamental frequency (Hz).
    p_peak : float
        Gaussian amplitude at the peak (dB above the detrended baseline).
    sigma : float
        Gaussian width parameter (Hz).
    """
    # Build product spectrum up to (1/nharms) of the full frequency range
    c_prod = np.copy(power[: len(power) // nharms])
    c_prod = convolve(c_prod, [0.25, 0.5, 0.25], mode="same") * 2  # light smoothing

    if plot:
        fig, ax = plt.subplots()
        ax.plot(f, power, label="Spectrum")

    for harm in range(2, nharms + 1):
        downsampled = decimate(power, harm)
        c_prod += downsampled[: len(c_prod)]

    f_red = f[: len(c_prod)]
    in_window = (f_red > fwin_pick[0]) & (f_red < fwin_pick[1])
    f_prod = f_red[in_window]
    c_prod = c_prod[in_window]
    c_prod_det = detrend(c_prod)

    # Initial peak location
    i_max = int(np.argmax(c_prod_det))
    f0_init = f_prop if (fwin_pick[0] < f_prop < fwin_pick[1]) else f_prod[i_max]
    p0_init = float(c_prod_det[i_max])

    # Refine with Gaussian fit
    result = minimize(
        fun=_gaussian_misfit,
        x0=np.array([f0_init, p0_init, 0.004]),
        args=(f_prod, c_prod_det),
        bounds=((0, None), (None, None), (0, None)),
    )
    f_peak, p_peak, sigma = result["x"]

    if plot:
        ax.plot(f_prod, c_prod_det, "k", label="HPS (detrended)")
        ax.plot(f_prod, _gaussian(f_prod, *result["x"]), "r--", label="Gaussian fit")
        ax.vlines(fwin_pick, c_prod_det.min(), c_prod_det.max(), colors="r", linestyles="--")
        ax.set_xlabel("Frequency (Hz)")
        ax.legend()
        plt.show()

    return float(f_peak), float(p_peak), float(sigma)


# ---------------------------------------------------------------------------
# Spectrogram peak picker
# ---------------------------------------------------------------------------

def pick_spectrogram_peaks(
    f: np.ndarray,
    t: np.ndarray,
    s: np.ndarray,
    fwin: tuple[float, float] = (0.4, 1.1),
    winlen: float = 150.0,
    sigma_min: float = 0.005,
    p_peak_min: float = 10.0,
    s_threshold: float = -150.0,
    nharms: int = 4,
    plot: bool = False,
    verbose: bool = False,
) -> tuple[list[float], list[float], list[float], list[float]]:
    """
    Pick harmonic peaks across all time windows of a spectrogram.

    For each time step the function checks whether the background energy
    exceeds *s_threshold*, then calls :func:`harmonic_product_spectrum` to
    locate the fundamental frequency.  A sub-harmonic check is applied when
    the initial pick is near the upper edge of the search window.

    Parameters
    ----------
    f : np.ndarray, shape (n_freq,)
        Frequency axis (Hz).
    t : np.ndarray, shape (n_time,)
        Time axis (seconds from trace start).
    s : np.ndarray, shape (n_freq, n_time)
        Spectrogram power in dB.
    fwin : tuple of (float, float)
        Frequency search window ``(fmin, fmax)`` in Hz.
    winlen : float
        Window length used during spectrogram computation (seconds).
    sigma_min : float
        Minimum acceptable Gaussian width; narrower peaks are rejected.
    p_peak_min : float
        Minimum peak amplitude (dB) above the detrended baseline.
    s_threshold : float
        Minimum mean power in ``[fwin[1], 3·fwin[1]]`` to attempt picking.
    nharms : int
        Number of harmonics for the HPS algorithm.
    plot : bool
        Open a diagnostic figure for each time window (slow).
    verbose : bool
        Print per-window summary to stdout.

    Returns
    -------
    times : list of float
        Times of accepted picks (seconds from trace start).
    freqs : list of float
        Picked fundamental frequencies (Hz).
    peak_values : list of float
        Gaussian amplitudes at accepted picks (dB).
    fmax_used : list of float
        Upper frequency bound used for each time window.
    """
    times, freqs, peak_values, fmax_used = [], [], [], []
    f_prop = -1.0

    # Background energy check — band above the search window
    background_mask = (f > fwin[1]) & (f < fwin[1] * 3)
    s_mean = np.mean(s[background_mask, :], axis=0)

    for i, ti in enumerate(t):
        fmax_used.append(fwin[1])

        if s_mean[i] <= s_threshold:
            continue

        f_peak, p_peak, sigma = harmonic_product_spectrum(
            f, s[:, i], fwin_pick=fwin, nharms=nharms, f_prop=f_prop, plot=plot
        )

        # Sub-harmonic check: if near the upper edge, try the half frequency
        if f_peak > (fwin[1] - fwin[0]) / 2:
            f2, p2, sig2 = harmonic_product_spectrum(
                f, s[:, i], fwin_pick=fwin, nharms=1, f_prop=f_peak / 2, plot=plot
            )
            if sig2 > sigma_min and p2 > p_peak * 0.8 and f2 < f_peak * 0.75:
                f_peak, p_peak, sigma = f2, p2, sig2

        accepted = (
            sigma > sigma_min
            and fwin[0] < f_peak < fwin[1]
            and p_peak > p_peak_min
        )

        if verbose:
            print(
                f"t={ti:8.1f}s  f={f_peak:.4f} Hz  p={p_peak:.2f} dB  "
                f"σ={sigma:.4f}  accepted={accepted}"
            )

        if accepted:
            times.append(ti)
            freqs.append(f_peak)
            peak_values.append(p_peak)
            f_prop = f_peak
        else:
            f_prop = -1.0

    return times, freqs, peak_values, fmax_used


# ---------------------------------------------------------------------------
# Long-period noise detection
# ---------------------------------------------------------------------------

def pick_longperiod_windows(
    t: np.ndarray,
    f: np.ndarray,
    s: np.ndarray,
    fmin: float = 0.01,
    fmax: float = 0.1,
) -> tuple[list[float], list[float]]:
    """
    Identify time windows with elevated long-period noise.

    Fits a linear trend to the power spectrum in the band ``[fmin, fmax]``
    for every time window.  Windows where the fitted intercept exceeds the
    median by more than 5 dB are flagged as "noisy".

    Parameters
    ----------
    t : np.ndarray
        Time axis (seconds from trace start).
    f : np.ndarray
        Frequency axis (Hz).
    s : np.ndarray, shape (n_freq, n_time)
        Spectrogram power in linear (not dB) units.
    fmin, fmax : float
        Frequency band defining "long-period" (Hz).

    Returns
    -------
    times : list of float
        Times of elevated long-period windows (seconds from trace start).
    levels : list of float
        Corresponding intercept values (proxy for noise level).
    """
    intercepts = []
    for i in range(len(t)):
        mask = f > fmin
        x = 1.0 / f[mask]
        y = s[mask, i]
        y = y[x < 1.0 / fmax]
        x = x[x < 1.0 / fmax]
        _, b = np.polyfit(x, y, deg=1)
        intercepts.append(float(b))

    threshold = float(np.median(intercepts)) + 5.0
    times = [float(t[i]) for i, b in enumerate(intercepts) if b > threshold]
    levels = [b for b in intercepts if b > threshold]
    return times, levels


# ---------------------------------------------------------------------------
# Displacement integration
# ---------------------------------------------------------------------------

def integrate_displacement(
    t: np.ndarray,
    f: np.ndarray,
    s: np.ndarray,
    peak_periods: np.ndarray,
    fmin: float = 0.01,
    fmax: float = 10.0,
    width: Optional[float] = None,
) -> np.ndarray:
    """
    Estimate displacement by integrating spectral power over a frequency band.

    Parameters
    ----------
    t : np.ndarray
        Time axis (seconds).
    f : np.ndarray
        Frequency axis (Hz).
    s : np.ndarray, shape (n_freq, n_time)
        Power spectral density in m²/Hz.
    peak_periods : np.ndarray, shape (n_time,)
        Dominant period at each time step (seconds).  Used only when
        *width* is not ``None``.
    fmin, fmax : float
        Default integration band (Hz) when *width* is ``None``.
    width : float or None
        If provided, integrate over a window of this width (seconds in period
        space) centred on ``1 / peak_periods[i]`` instead of the fixed band.

    Returns
    -------
    np.ndarray, shape (n_time,)
        Displacement estimate at each time step (m).
    """
    displacement = np.zeros(len(t))
    df = f[2] - f[1]

    for i in range(len(t)):
        if width is None:
            f_lo, f_hi = fmin, fmax
        else:
            f_lo = 1.0 / (peak_periods[i] + width / 2)
            f_hi = 1.0 / (peak_periods[i] - width / 2)

        in_band = (f > f_lo) & (f < f_hi)
        displacement[i] = float(np.sum(np.sqrt(s[in_band, i])) * df)

    return displacement
