"""
Make a bar plot to visualize the prevalence of involvement in each of the four
considered lymph node levels (LNLs), stratified by subsite (different bras) and by
location (different colors).
"""
import argparse
from pathlib import Path
from typing import Generator
import yaml

import matplotlib.pyplot as plt
from matplotlib.colors import to_rgba
from tueplots import figsizes, fontsizes
from lyscripts.utils import load_patient_data
from lyscripts.plot.utils import COLORS as USZ


SUBSITE = ("tumor", "1", "subsite")
LOCATION = ("tumor", "1", "location")
LNL_I = ("max_llh", "ipsi", "I")
LNL_II = ("max_llh", "ipsi", "II")
LNL_III = ("max_llh", "ipsi", "III")
LNL_IV = ("max_llh", "ipsi", "IV")
OROPHARYNX_ICDS = ["C01", "C09", "C10"]


def create_parser() -> argparse.ArgumentParser:
    """Assemble the parser for the command line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "-i", "--input", type=Path, default="data/enhanced.csv",
        help="Path to the patient data file.",
    )
    parser.add_argument(
        "-o", "--output", type=Path, default="figures/prevalence_by_subsite.png",
        help="Path to the output file.",
    )
    parser.add_argument(
        "-p", "--params", type=Path, default="params.yaml",
        help="Path to the parameter file. Looks for a key `barplot_kwargs`.",
    )
    return parser


def simplify_subsite(icd_code: str) -> str:
    """Only use the part of the ICD code before the decimal point."""
    return icd_code.split(".")[0]


def generate_location_colors(
    icd_codes: list[str],
    delta_alpha: float = 0.15,
) -> Generator[tuple[float, float, float, float], None, None]:
    """Make a list of colors for each location."""
    oropharynx_alpha = 1.0
    oral_cavity_alpha = 1.0
    colors, alphas = [], []
    for icd_code in icd_codes:
        if icd_code in OROPHARYNX_ICDS:
            colors.append(USZ["orange"])
            alphas.append(oropharynx_alpha)
            oropharynx_alpha -= delta_alpha
            yield to_rgba(USZ["orange"], oropharynx_alpha)
        else:
            colors.append(USZ["blue"])
            alphas.append(oral_cavity_alpha)
            oral_cavity_alpha -= delta_alpha
            yield to_rgba(USZ["blue"], oral_cavity_alpha)


def main():
    """Load data and create bar plot from it."""
    args = create_parser().parse_args()
    barplot_kwargs = {}
    if args.params.exists():
        with open(args.params) as f:
            params = yaml.safe_load(f)
        barplot_kwargs.update(params.get("barplot_kwargs", {}))
        icd_code_map = params.get("icd_code_map", {})

    patient_data = load_patient_data(args.input)
    patient_data[SUBSITE] = patient_data[SUBSITE].apply(simplify_subsite)
    pivot_table = patient_data.pivot_table(
        index=[SUBSITE],
        values=[LNL_I, LNL_II, LNL_III, LNL_IV]
    ).sort_values(by=LNL_II)
    colors = list(generate_location_colors(pivot_table.index))
    pivot_table.index = pivot_table.index.map(icd_code_map)

    plt.rcParams.update(figsizes.icml2022_half())
    plt.rcParams.update(fontsizes.icml2022())
    fig, ax = plt.subplots()
    ax = (100 * pivot_table.T).plot.bar(
        ax=ax,
        color=colors,
        **barplot_kwargs,
    )

    ax.grid(axis="y")
    ax.set_xlabel("Lymph node level")
    ax.set_xticklabels(["I", "II", "III", "IV"], rotation=0)
    ax.set_ylabel("Prevalence [%]")
    ax.legend(fontsize="x-small", labelspacing=0.3)
    ax.set_xlim(-0.46, 3.46)

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.output, bbox_inches="tight", dpi=300)


if __name__ == "__main__":
    main()
