# PTTEM: SNR pipeline and figures

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.17357409.svg)](https://doi.org/10.5281/zenodo.17357409)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.8475.svg)](https://doi.org/10.5281/zenodo.8475)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](./LICENSE)

## Overview
Minimal runner to compute LISA-band SNR from benchmark SGWB spectra and save diagnostic plots.

## Installation
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
pip install -r requirements.txt
Usage
bash
Copy code
# Conservative baseline
python src/snr_test.py --gcn on  --band standard
# Optimistic, wider band
python src/snr_test.py --gcn off --band wide
Artifacts:

JSON: output.json

Plots: figs/*.png

Expected results (sanity)
LISA single-TDI, 4 yr, R_Ω = 0.03.

Typical SNR ranges:

S1: ~5 (GCN ON, standard)

S2: ~16 (GCN ON, standard)

OFF+wide yields larger SNR as documented in the paper.
If values are far off, check Python/NumPy versions and that figs/ exists.

Reproducibility
Deterministic given the fixed grids. No random seeds used.
Integration uses NumPy trapezoid on a log-frequency grid.

Data and Code Availability
Preprint, data and figures: https://doi.org/10.5281/zenodo.17357409

Stand-alone script archive: https://doi.org/10.5281/zenodo.8475

How to Cite
Preprint
bibtex
Copy code
@misc{Ozyurt_PTTEM_2025_preprint,
  author = {Özyurt, Emre},
  title  = {Stochastic Gravitational-Wave Signatures of Dark-Matter Phase Transitions:
            A Thermodynamic Buffer Mechanism for Self-Regulating Cosmic Expansion},
  year   = {2025},
  doi    = {10.5281/zenodo.17357409}
}
Software
bibtex
Copy code
@software{Ozyurt_snrtest_2025,
  author = {Özyurt, Emre},
  title  = {PTTEM: snr_test.py},
  year   = {2025},
  doi    = {10.5281/zenodo.8475}
}
License
MIT; see LICENSE.

Figures


go
Copy code

`CITATION.cff` ve `LICENSE` If it is already ready, no changes are required.
