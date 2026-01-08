import pandas as pd

def load_dataset(path: str):
    """
    Load airline delay dataset from a CSV file.
    """
    return pd.read_csv(path)
