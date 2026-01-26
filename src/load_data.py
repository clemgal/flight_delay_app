from pathlib import Path
import pandas as pd
import kagglehub


def load_dataset() -> pd.DataFrame:
    """
    Download (if needed) and load the airline delay dataset from Kaggle.
    Uses KaggleHub caching automatically.
    """
    # 1. Download / get cached dataset folder
    dataset_dir = Path(
        kagglehub.dataset_download("sriharshaeedala/airline-delay")
    )

    # 2. Find CSV files inside (recursively)
    csv_files = list(dataset_dir.rglob("*.csv"))

    if not csv_files:
        raise FileNotFoundError(
            f"No CSV files found in Kaggle dataset folder: {dataset_dir}"
        )

    if len(csv_files) > 1:
        raise ValueError(
            "Multiple CSV files found. Be explicit.\n"
            + "\n".join(str(p.relative_to(dataset_dir)) for p in csv_files)
        )

    # 3. Load the only CSV
    return pd.read_csv(csv_files[0])
