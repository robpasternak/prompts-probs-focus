# Prompts and probabilities in the linguistic assessment of language models: Evidence from semantic focus-sensitivity.

This repository contains code and data for the paper "Prompts and probabilities in the linguistic assessment of language model: Evidence from semantic focus-sensitivity". If using any datasets or code from this repository, please cite the paper accordingly (information below).

The `lmfocus` package used in this repository was created with `uv`; for installation instructions, see [here](https://docs.astral.sh/uv/getting-started/installation/). Upon installing `uv`, run `uv sync` to install required packages.

**Note:** What is referred to in the paper as a _background_ is marked in the datasets and code as a _context_. We made the terminological switch to "background" because "context" could be ambiguous in an NLP environment.

## Repo structure

- `/data/`: Datasets and results. See `/data/README.md` for more specific information.
- `/graphs/`: Graph images for sharing experiment results.
- `/lmfocus/`: Python package for running experiments (created with `uv`).
    - `/lmfocus/data/`: Code for manipulating datasets (e.g., creating datasets for specific focus markers using seed dataset).
    - `/lmfocus/llms/`: Code for running LMs.
    - `/lmfocus/prompts/`: Prommpts for forced choice and yes/no prompting.
    - `/lmfocus/results/`: Code for parsing/analyzing results and some descriptive statistics.
- `/notebooks/`: Jupyter notebooks for generating graphs and some descriptive statistics.
- `/scripts/`: Python scripts for running experiments.
- `/stats/`: R code and data CSVs for statistical analysis:
    - `/stats/01_exps_analysis_individual.r`: Runs logistic regression analysis for each of the two experiments.
    - `/stats/02_exps_analysis_across.r`: Runs linear regression analysis to compare across the two experiments.
    - `/stats/stats_exp_01.csv` and `/stats/stats_exp_02.csv`: Statistical results for Exps. 1 and 2, respectively.
    - `/stats/stats_exps_across.csv`: Results of comparison across experiments.
- `/01_run_method_comps.sh` and `/02_run_randoms.sh`: Bash code for running Exps. 1 and 2, respectively (see below).

## How to run experiments

- **Experiment 1** can be rerun with `./01_run_method_comps.sh MODEL`, where `MODEL` is one of the keys in `/scripts/models.json`. Some optional arguments:
    - `--focus-types`: Focus markers to run, as a string of comma-separated names (e.g. `all_caps,html_bold,html_emphasis`). Defaults to all non-randomly-generated focus markers.
    - `--batch-size`: Batch size. Defaults to full dataset for each focus marker.
    - `--quantize`: Whether to 8-bit quantize. Defaults to no quantization. This was not used in any of the experiments reported in the paper, and it was not tested, so it may not work.
    - `--device`: What device to run the model on. Defaults to `auto`.
- **Experiment 2** can be rerun with `./02_run_randoms.sh MODEL`, where `MODEL` is one of the keys in `/scripts/models.json`. Optional arguments are the same as for Experiment 1.

## How to cite

BibTeX will be added soon.

## Statement on AI usage

- **Planning:** No AI was used in the planning of the experiments.
- **Code:** Portions of the codebase used for running experiments and evaluation were LM-generated. All code was human-checked. The author takes full responsibility.
- **Dataset creation:** No AI was used in the creation of the datasets.
- **Writing:** No AI was used in the writing of the paper.