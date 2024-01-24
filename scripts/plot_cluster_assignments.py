"""
Visualize the cluster assignments of the trained mixture model.
"""
import argparse
from pathlib import Path
import yaml

import h5py
import matplotlib.pyplot as plt
from matplotlib.colors import to_rgba
from tueplots import figsizes, fontsizes
from lyscripts.plot.utils import COLORS as USZ

from helpers import OROPHARYNX_ICDS


def create_parser() -> argparse.ArgumentParser:
    """Assemble the parser for the command line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "-m", "--model", type=Path, default="models/mixture.hdf5",
        help=(
            "Path to the model HDF5 file. Needs to contain a dataset called "
            "``em/cluster_assignments``."
        )
    )
    parser.add_argument(
        "-o", "--output", type=Path, default="figures/cluster_assignments.png",
        help="Path to the output file.",
    )
    parser.add_argument(
        "-p", "--params", type=Path, default="_variables.yml",
        help="Path to the parameter file..",
    )
    return parser


def main():
    """Execute the main routine."""
    args = create_parser().parse_args()
    with open(args.params) as file:
        params = yaml.safe_load(file)
        num_patients = params["num_patients"]
        num_patients.pop("total")

    with h5py.File(args.model, mode="r") as h5_file:
        cluster_components = h5_file["em/cluster_components"][...]

    plt.rcParams.update(figsizes.icml2022_half())
    plt.rcParams.update(fontsizes.icml2022())

    _, bottom_ax = plt.subplots()
    bottom_ax.scatter(
        [cluster_components[i] for i, _ in enumerate(num_patients.keys())],
        [0. for _ in num_patients.keys()],
        s=[num for num in num_patients.values()],
        c=[
            to_rgba(USZ["orange"] if i in OROPHARYNX_ICDS else USZ["blue"], alpha=0.7)
            for i in num_patients.keys()
        ],
        alpha=0.7,
        linewidths=0.,
    )
    bottom_ax.set_xlabel("assignment to cluster A [%]")
    bottom_ax.set_xticklabels([f"{int(tick):.2%}" for tick in bottom_ax.get_xticks()])
    top_ax = bottom_ax.secondary_xaxis(
        location="top",
        functions=(lambda x: 1. - x, lambda x: 1. - x),
    )
    top_ax.set_xlabel("assignment to cluster B [%]")
    plt.savefig(args.output, bbox_inches="tight", dpi=300)


if __name__ == "__main__":
    main()
