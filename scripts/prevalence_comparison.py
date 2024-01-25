"""
Plot the prevalence for involvement, as predicted by the trained mixture model, and
compare it to the prevalence of involvement in the data.
"""
import argparse
from pathlib import Path
import yaml

import numpy as np
import matplotlib.pyplot as plt
import h5py
from emcee.backends import HDFBackend
from lyscripts.utils import load_patient_data, create_model_from_config
from lyscripts.predict.prevalences import (
    compute_observed_prevalence,
    generate_predicted_prevalences,
)

from helpers import str2bool, OROPHARYNX_ICDS


T_STAGE = ("tumor", "1", "t_stage")
LNLS = ["I", "II", "III", "IV"]


def create_parser() -> argparse.ArgumentParser:
    """Assemble the parser for the command line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "-d", "--data", type=Path, default="data/enhanced.csv",
        help="Path to the data file.",
    )
    parser.add_argument(
        "--mixture-model", type=Path, default="models/mixture.hdf5",
        help=(
            "Path to the mixture model HDF5 file. Needs to contain a dataset called "
            "``em/cluster_components``. Parent directory is assumed to also contain "
            "the HDF5 file of the independent model (either `oropharynx.hdf5` or "
            "`oral_cavity.hdf5`)."
        )
    )
    parser.add_argument(
        "-o", "--output", type=Path, default="figures/prevalence_comparison.png",
        help="Path to the output file.",
    )
    parser.add_argument(
        "-p", "--params", type=Path, default="_variables.yml",
        help="Path to the parameter file..",
    )
    parser.add_argument(
        "-i", "--involvement", nargs=4, type=str2bool, required=True,
        help="Involvement pattern to compare the prevalences for.",
    )
    parser.add_argument(
        "-s", "--subsite", type=str, default="C01",
        help="ICD code of the subsite to plot the prevalences for.",
    )
    parser.add_argument(
        "--thin-indie", type=int, default=10,
        help="Thinning factor for the independent model's chain.",
    )
    parser.add_argument(
        "--thin-mixture", type=int, default=1000,
        help="Thinning factor for the mixture model's chain.",
    )
    return parser


def main():
    args = create_parser().parse_args()

    with open(args.params) as file:
        params = yaml.safe_load(file)

    lymph_model = create_model_from_config(params)
    lymph_model.modalities = {"max_llh": [1., 1.]}

    pattern = {"ipsi": {lnl: val for lnl, val in zip(LNLS, args.involvement)}}
    patient_data = load_patient_data(args.data)
    patient_data[T_STAGE] = ["all"] * len(patient_data)

    if args.subsite in OROPHARYNX_ICDS:
        indie_chain = HDFBackend(
            args.mixture_model.parent / "oropharynx.hdf5",
            read_only=True,
        ).get_chain(flat=True, thin=args.thin_indie)
    else:
        indie_chain = HDFBackend(
            args.mixture_model.parent / "oral_cavity.hdf5",
            read_only=True,
        ).get_chain(flat=True, thin=args.thin_indie)

    mixture_chain = HDFBackend(
        args.mixture_model, read_only=True,
    ).get_chain(flat=True, thin=args.thin_mixture)
    with h5py.File(args.mixture_model, mode="r") as h5_file:
        cluster_assignments = h5_file["em/cluster_components"][...]

    matching, total = compute_observed_prevalence(
        pattern=pattern,
        data=patient_data,
        lnls=LNLS,
        t_stage="all",
        modality="max_llh",
        invert=False,
    )
    independent_prevs = np.array(list(generate_predicted_prevalences(
        pattern=pattern,
        model=lymph_model,
        samples=indie_chain,
        t_stage="all",
        modality_spsn=[1., 1.],
    )))
    cluster_A_prevs = np.array(list(generate_predicted_prevalences(
        pattern=pattern,
        model=lymph_model,
        samples=mixture_chain,
        t_stage="all",
        modality_spsn=[1., 1.],
    )))

    print(f"Observed prevalence: {matching} out of {total}")
    print(f"Predicted prevalence: {mixture_model_prevs.mean():.3f}")
    print(f"Independent model prevalence: {independent_prevs.mean():.3f}")

if __name__ == "__main__":
    main()
