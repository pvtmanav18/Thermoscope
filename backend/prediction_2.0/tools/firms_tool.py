# tools/firms_tool.py

import pandas as pd


REQUIRED_COLUMNS = [
    "latitude",
    "longitude",
    "bright_ti4",
    "bright_ti5",
    "frp",
    "confidence",
    "acq_date",
    "acq_time",
    "daynight"
]


def load_firms_dataset(csv_path):
    """
    Load NASA FIRMS CSV and validate columns.
    """

    df = pd.read_csv(csv_path)

    # Normalize column names
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
    )

    missing = [
        col for col in REQUIRED_COLUMNS
        if col not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Missing FIRMS columns: {missing}"
        )

    # Fill missing confidence
    df["confidence"] = df["confidence"].fillna(80)

    # Remove duplicates
    df = df.drop_duplicates()

    # Remove invalid coordinates
    df = df[
        (df.latitude.between(-90, 90)) &
        (df.longitude.between(-180, 180))
    ]

    return df.reset_index(drop=True)