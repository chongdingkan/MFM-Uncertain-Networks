# Maximum-Flow Maintenance in Uncertain Networks

This repository contains the source code and datasets for our paper on defending uncertain networks against adversarial interdiction.

## Datasets
The dataset archives are stored in the repository root:
- Facebook Ego Network
- EU-Email Network

## Requirements
- Python 3.8+
- NetworkX
- Pandas
- NumPy

## Table V sensitivity and component ablation

[Download the source package](TableV_sensitivity_ablation_reconstructed.zip) and
read the [configuration and reproduction guide](TABLE_V_REPRODUCIBILITY.md).
The archive includes the executable workflow, configuration, pinned dependencies,
statistical aggregation, tests, and the EU-Email dataset. Extract it into a new
folder and follow the commands in the guide. It covers the 16 Table V settings
for HEU cost sensitivity and component ablation under RA and HA.

This is a reconstructed implementation, not the recovered historical scripts.
Historical run-level records and some implementation choices are unavailable.
Numerical agreement with the printed Table V has not been established; the full
experimental batch has not been run for this addition. The guide records the
newly documented defaults and the distinction between the public HEU selection
rule and Algorithm 2's backtracking description.
