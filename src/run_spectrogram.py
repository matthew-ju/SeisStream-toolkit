#!/usr/bin/env python3
"""
run_spectrogram.py
==================

Command-line interface for computing a seismic spectrogram from one or more
MiniSEED files.

Usage
-----
::

    python src/run_spectrogram.py doc/testdata.mseed
    python src/run_spectrogram.py "data/*.mseed" --winlen 600 --vmin -160 --vmax -60
    python src/run_spectrogram.py data.mseed --kind harmonic --fmin 0.4 --fmax 1.2

"""

import argparse
import glob
import os
import sys

# Allow running from the repo root without installing the package
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from tqdm import tqdm
except ImportError:
    def tqdm(iterable, **_):  # type: ignore[misc]
        return iterable

from spectrogram import calc_spec, SpectrogramConfig

_TIME_HELP = (
    "Any format ObsPy understands, e.g. '2026-01-01T06:00:00' "
    "or '2026-001' (year + day-of-year).  Defaults to the full file."
)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Plot spectrogram and optionally find spectral peaks in seismic data.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "smgr_path",
        help="Path (or glob pattern) to MiniSEED file(s) — anything ObsPy can read.",
    )
    parser.add_argument(
        "-k", "--kind",
        choices=["none", "peak", "harmonic"],
        default="none",
        help="Spectral feature to detect.",
    )
    parser.add_argument("--fmin",    type=float, default=0.4,   help="Min frequency for picking (Hz).")
    parser.add_argument("--fmax",    type=float, default=4.0,   help="Max frequency for picking (Hz).")
    parser.add_argument("--vmin",    type=float, default=-160.0, help="Colour-scale minimum (dB).")
    parser.add_argument("--vmax",    type=float, default=-60.0,  help="Colour-scale maximum (dB).")
    parser.add_argument("--winlen",  type=float, default=300.0,  help="Spectrogram window length (s).")
    parser.add_argument("--nharms",  type=int,   default=4,      help="Number of harmonics for HPS.")
    parser.add_argument("--skip_hf", action="store_true",        help="Hide the high-frequency panel.")
    parser.add_argument("--fmin_plot", type=float, default=None, help="High-pass display filter (Hz).")
    parser.add_argument("--fmax_plot", type=float, default=None, help="Low-pass display filter (Hz).")
    parser.add_argument("--dpi",     type=int,   default=150,    help="Output image resolution.")
    parser.add_argument("--out_path", default="output",          help="Root output directory.")
    parser.add_argument(
        "--start", default=None, metavar="TIME",
        help="Trim data to start at this time. " + _TIME_HELP,
    )
    parser.add_argument(
        "--end", default=None, metavar="TIME",
        help="Trim data to end at this time. " + _TIME_HELP,
    )

    return parser


def main() -> None:
    parser = _build_parser()
    args   = parser.parse_args()

    # Expand glob patterns and sort
    files = sorted(glob.glob(args.smgr_path))
    if not files:
        print(f"Error: no files matched '{args.smgr_path}'", file=sys.stderr)
        sys.exit(1)

    cfg = SpectrogramConfig(
        fmin_pick      = args.fmin,
        fmax_pick      = args.fmax,
        vmin           = args.vmin,
        vmax           = args.vmax,
        winlen         = args.winlen,
        nharms         = args.nharms,
        plot_highfreq  = not args.skip_hf,
        pick_harmonics = (args.kind == "harmonic"),
        pick_peak      = (args.kind == "peak"),
        fmin_plot      = args.fmin_plot,
        fmax_plot      = args.fmax_plot,
        t_start        = args.start,
        t_end          = args.end,
        dpi            = args.dpi,
        path_out       = args.out_path,
    )

    for fnam in tqdm(files, unit="file"):
        try:
            calc_spec(fnam, cfg=cfg)
        except Exception as exc:
            print(f"\nWarning: failed on {fnam}: {exc}", file=sys.stderr)


if __name__ == "__main__":
    main()
