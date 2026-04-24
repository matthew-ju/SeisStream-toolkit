#!/usr/bin/env python3
"""
run_batch.py
============

Batch-process a directory tree of MiniSEED files, producing one spectrogram
PNG per file.

Usage
-----
::

    python src/run_batch.py --data-dir /path/to/data --station DARS1
    python src/run_batch.py --data-dir /opt/DARS/Corrected --station RCANX \\
        --vmin -60 --vmax 40 --out-path output/

"""

import argparse
import glob
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from tqdm import tqdm
except ImportError:
    def tqdm(iterable, **_):  # type: ignore[misc]
        return iterable

from spectrogram import calc_spec, SpectrogramConfig


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Batch compute spectrograms for a directory of MiniSEED files.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--data-dir",  required=True,  help="Root data directory.")
    parser.add_argument("--station",   required=True,  help="Station code sub-directory.")
    parser.add_argument("--pattern",   default="*.seed", help="File glob pattern within the station directory.")
    parser.add_argument("--vmin",      type=float, default=-160.0)
    parser.add_argument("--vmax",      type=float, default=-60.0)
    parser.add_argument("--winlen",    type=float, default=300.0)
    parser.add_argument("--out-path",  default="output", help="Root output directory.")
    parser.add_argument("--dpi",       type=int,   default=150)
    return parser


def main() -> None:
    args = _build_parser().parse_args()

    search = os.path.join(args.data_dir, args.station, "**", args.pattern)
    files  = sorted(glob.glob(search, recursive=True))

    if not files:
        print(f"No files found matching: {search}", file=sys.stderr)
        sys.exit(1)

    print(f"Found {len(files)} file(s) in {search}")

    cfg = SpectrogramConfig(
        vmin     = args.vmin,
        vmax     = args.vmax,
        winlen   = args.winlen,
        dpi      = args.dpi,
        path_out = args.out_path,
    )

    for fnam in tqdm(files, unit="file"):
        try:
            calc_spec(fnam, cfg=cfg)
        except Exception as exc:
            print(f"\nWarning: failed on {fnam}: {exc}", file=sys.stderr)


if __name__ == "__main__":
    main()
