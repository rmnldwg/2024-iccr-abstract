"""
Helper functions for the scripts.
"""
from typing import Generator
import argparse

from lyscripts.plot.utils import COLORS as USZ
from matplotlib.colors import to_rgba


OROPHARYNX_ICDS = ["C01", "C09", "C10"]
SUBSITE = ("tumor", "1", "subsite")
SIMPLE_SUBSITE = ("tumor", "1", "simple_subsite")
LOCATION = ("tumor", "1", "location")
T_STAGE = ("tumor", "1", "t_stage")
LNLS = ["I", "II", "III", "IV"]
LNL_I = ("max_llh", "ipsi", "I")
LNL_II = ("max_llh", "ipsi", "II")
LNL_III = ("max_llh", "ipsi", "III")
LNL_IV = ("max_llh", "ipsi", "IV")


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


def str2bool(v: str) -> bool | None:
    """Transform a string to a boolean or ``None``."""
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    elif v.lower() in ('none', 'null', ''):
        return None
    else:
        raise argparse.ArgumentTypeError('Boolean or None value expected.')
