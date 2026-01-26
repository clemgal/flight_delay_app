import pandas as pd
import kagglehub
from pathlib import Path


def load_dataset(
    dataset: str = "abdelazizel7or/airline-delay-cause",
    filename: str = "airline_delay_cause.csv",
    ) -> pd.DataFrame:
    """
    Download (if needed) and load the airline delay dataset.
    """
    download_path = Path(kagglehub.dataset_download(dataset))
    csv_path = download_path / filename
    return pd.read_csv(csv_path)


if __name__ == "__main__":
    print("Running load_data.py directly...")
    df = load_dataset()
    print(df.head())
