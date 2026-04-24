"""
tests/test_core.py
==================

Smoke tests for the spectrogram package.

Run with::

    python -m pytest tests/ -v

"""

import os
import sys

import pytest

# Ensure the src directory is on sys.path when running tests directly
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from spectrogram import calc_spec, SpectrogramConfig

TESTDATA = os.path.join(os.path.dirname(__file__), "..", "doc", "testdata.mseed")


@pytest.fixture(scope="session")
def output_dir(tmp_path_factory):
    """Temporary output directory shared across all tests in the session."""
    return str(tmp_path_factory.mktemp("spectrograms"))


class TestBuildOutputFilename:
    """Unit tests for the filename helper."""

    def test_format(self):
        from obspy import UTCDateTime
        from spectrogram.io import build_output_filename

        name = build_output_filename("BB.DARS1.00.BHZ", UTCDateTime("2015-02-08T00:00:00"))
        assert name == "BB.DARS1.00.BHZ_2015_02_08_00.png"


class TestStationAliasResolution:
    """Unit tests for serial-number alias remapping."""

    def test_known_alias(self):
        import obspy
        from spectrogram.preprocessing import resolve_station_alias

        st = obspy.Stream([obspy.Trace()])
        st[0].stats.station = "12166"
        st[0].stats.network = "SS"
        st[0].stats.location = "00"

        tr = resolve_station_alias(st[0])
        assert tr.stats.station == "MB01"
        assert tr.stats.network == "1R"

    def test_unknown_alias_unchanged(self):
        import obspy
        from spectrogram.preprocessing import resolve_station_alias

        st = obspy.Stream([obspy.Trace()])
        st[0].stats.station = "DARS1"
        st[0].stats.network = "BB"

        tr = resolve_station_alias(st[0])
        assert tr.stats.station == "DARS1"
        assert tr.stats.network == "BB"


class TestCalcSpec:
    """Integration smoke test — runs calc_spec on the bundled test file."""

    def test_runs_without_error(self, output_dir):
        if not os.path.exists(TESTDATA):
            pytest.skip(f"Test data not found: {TESTDATA}")

        cfg = SpectrogramConfig(
            vmin=-180,
            vmax=-80,
            winlen=300,
            dpi=72,       # low DPI for speed in CI
            path_out=output_dir,
        )
        f, t, s = calc_spec(TESTDATA, cfg=cfg)

        assert f.shape[0] > 0, "Frequency axis is empty"
        assert t.shape[0] > 0, "Time axis is empty"
        assert s.shape == (f.shape[0], t.shape[0]), "Spectrogram shape mismatch"

    def test_output_file_created(self, output_dir):
        spec_dir = os.path.join(output_dir, "Spectrograms")
        pngs = [f for f in os.listdir(spec_dir) if f.endswith(".png")]
        assert len(pngs) >= 1, "No output PNG was created"
