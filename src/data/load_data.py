import pandas as pd

from src.config import RAW_FILE


def load_raw_data() -> pd.DataFrame:
    """Load the raw Ames housing data.

    In this dataset the text "NA" and "None" mean the house does not have
    that feature. So only truly blank cells are treated as missing values.
    """
    return pd.read_csv(RAW_FILE, keep_default_na=False, na_values=[""])