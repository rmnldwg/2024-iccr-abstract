"""
Perform an EM-like sampling round to infer parameters and mixture components of a
n-component mixture of lymphatic progression models for k different tumor subsites.
"""
import argparse
from pathlib import Path
import numpy as np
import yaml

from lyscripts.utils import (
    load_patient_data,
    create_model_from_config,
)

from helpers import simplify_subsite
from lymixture.mixture_model import LymphMixtureModel


SUBSITE = ("tumor", "1", "subsite")
SIMPLE_SUBSITE = ("tumor", "1", "simple_subsite")


def create_parser() -> argparse.ArgumentParser:
    """Assemble the parser for the command line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "-i", "--input", type=Path, default="data/enhanced.csv",
        help="Path to the patient data file.",
    )
    parser.add_argument(
        "-m", "--models", type=Path, default="models/",
        help="Directory for sampled models.",
    )
    parser.add_argument(
        "-p", "--params", type=Path, default="_variables.yml",
        help="Path to the parameter file. Looks for a key `barplot_kwargs`.",
    )
    return parser


def main():
    """Execute the main routine."""
    args = create_parser().parse_args()

    with open(args.params, mode="r", encoding="utf-8") as f:
        params = yaml.safe_load(f)

    patient_data = load_patient_data(args.input)
    patient_data[SIMPLE_SUBSITE] = patient_data[SUBSITE].apply(simplify_subsite)
    num_subsites = len(patient_data[SIMPLE_SUBSITE].unique())
    lymph_model = create_model_from_config(params)
    lymph_model.modalities = {"max_llh": [1., 1.]}
    lymph_model.diag_time_dists = {"all": lymph_model.diag_time_dists["early"]}

    mixture_model = LymphMixtureModel(
        lymph_model=lymph_model,
        n_clusters=params["mixture_model"]["num_clusters"],
        n_subpopulation=num_subsites,
        name="test",
    )
    mixture_model.load_data(
        patient_data=patient_data,
        split_by=SIMPLE_SUBSITE,
        mapping=lambda x: "all",
    )
    mixture_model.cluster_assignments = np.zeros(shape=(
        mixture_model.n_subpopulation * (mixture_model.n_clusters - 1)
    )) + 0.2
    mixture_model.cluster_parameters = np.random.uniform(
        size=mixture_model.n_cluster_parameters
    )
    print(mixture_model.mm_hmm_likelihood())


if __name__ == "__main__":
    main()
