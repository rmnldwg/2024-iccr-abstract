"""
Helper functions for the scripts.
"""
OROPHARYNX_ICDS = ["C01", "C09", "C10"]

def simplify_subsite(icd_code: str) -> str:
    """Only use the part of the ICD code before the decimal point."""
    return icd_code.split(".")[0]
