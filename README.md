# SeisStream Toolkit

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![ObsPy](https://img.shields.io/badge/Powered%20by-ObsPy-orange.svg)](https://docs.obspy.org/)
[![License: LGPL v3](https://img.shields.io/badge/License-LGPL_v3-blue.svg)](https://www.gnu.org/licenses/lgpl-3.0)

A professional-grade Python toolkit for processing, analyzing, and visualizing continuous seismic waveform data. This project refactors legacy seismological scripts into a modular, production-ready package capable of handling high-throughput MiniSEED data with scientific precision.

![Seismic Spectrogram Example](doc/DARS1.BHZ_2015_02_08_00.png)

## Key Features

*   **Gap-Aware Visualization**: Intelligently renders data gaps as whitespace, ensuring absolute time-accuracy without the artifacts introduced by zero-padding.
*   **Dual-Band Spectral Analysis**: Simultaneous generation of high-frequency (Hz) and long-period (seconds) spectrograms in a unified dashboard.
*   **Scientific Processing Pipeline**: 
    *   Automated instrument response removal via StationXML/FDSN inventories.
    *   Dynamic station aliasing (remapping hardware serials to canonical SEED codes).
    *   Zero-phase display filtering to preserve waveform timing.
*   **Automated Feature Extraction**: Implementation of the **Harmonic Product Spectrum (HPS)** algorithm for fundamental frequency detection in complex seismic signals.
*   **Production-Ready Codebase**: Fully modular architecture with type hints, NumPy-style docstrings, and automated unit tests.

---

## Quick Start

### 1. Installation

```bash
# Install core scientific dependencies
pip install obspy numpy matplotlib scipy tqdm
```

### 2. Generate Your First Spectrogram
Process a MiniSEED file using the optimized default configuration:

```bash
python src/run_spectrogram.py doc/testdata.mseed
```
*Results are saved to `output/Spectrograms/`.*

### 3. Advanced Analysis
Run the harmonic picker on a specific frequency band:

```bash
python src/run_spectrogram.py doc/testdata.mseed --kind harmonic --fmin 0.4 --fmax 1.2
```

---

## Project Architecture

The codebase follows a modular design pattern to separate concerns and improve maintainability:

```text
SeisStream-toolkit/
├── src/
│   ├── spectrogram/           # Core Package
│   │   ├── core.py            # Main orchestration logic
│   │   ├── preprocessing.py   # Instrument response & filtering
│   │   ├── analysis.py        # HPS picking & signal math
│   │   ├── plotting.py        # Matplotlib rendering engine
│   │   ├── config.py          # Static metadata & station aliases
│   │   └── io.py              # File handles & pick writing
│   ├── run_spectrogram.py     # CLI: Single-file/Glob processor
│   └── run_batch.py           # CLI: High-volume batch processor
├── tests/                     # Automated unit & smoke tests
├── legacy/                    # Archived legacy research scripts
├── doc/                       # Documentation & test fixtures
└── requirements.txt           # Dependency manifest
```

---

## Technical Implementation

### Instrument Response Handling
The toolkit implements a robust deconvolution pipeline. If a StationXML file is provided in `config.py`, the system automatically performs:
1.  Linear detrending & demeaning.
2.  Cosine tapering.
3.  Pre-filtering with frequency-dependent water levels.
4.  Deconvolution to physical units (Acceleration/Velocity/Displacement).

### Harmonic Picking
The `analysis` module utilizes a Gaussian-fitted Harmonic Product Spectrum. This allows for sub-bin frequency resolution, essential for tracking fine-scale changes in environmental or structural seismic resonance.

---

## Quality Assurance

This project includes a suite of tests to ensure processing consistency.

```bash
# Run the test suite
python -m pytest tests/ -v
```

---

## License
Distributed under the **GNU Lesser General Public License v3**. See `LICENSE` for more information.

---

**Developed for high-quality seismological research and production environments.**
