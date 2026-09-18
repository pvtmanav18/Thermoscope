# ==========================================
# tools/firms_tool.py
# NASA FIRMS Downloader
# ==========================================

import os
import pandas as pd
import requests
from config import config


def firms_url(days=7):
    """
    NASA FIRMS VIIRS NRT API URL
    """

    return (
        "https://firms.modaps.eosdis.nasa.gov/api/area/csv/"
        f"{config.NASA_API_KEY}/VIIRS_NOAA21_NRT/world/{days}"
    )


def fetch_firms_data(days=7):
    """
    Download NASA FIRMS CSV.
    """

    url = firms_url(days)

    response = requests.get(url, timeout=60)

    response.raise_for_status()

    return pd.read_csv(
        pd.io.common.StringIO(response.text)
    )


def save_dataset(df, path=None):
    """
    Save downloaded dataset.
    """

    if path is None:
        path = config.INPUT_CSV

    os.makedirs(os.path.dirname(path), exist_ok=True)

    df.to_csv(path, index=False)

    print(f"Saved {len(df)} records to {path}")


def get_latest_fires(days=7, limit=50):
    """
    Fetch latest fire hotspots.
    """

    df = fetch_firms_data(days)

    df = df.head(limit)

    save_dataset(df)

    return df


if __name__ == "__main__":

    fires = get_latest_fires(
        days=config.DAYS,
        limit=config.MAX_FIRE_RECORDS
    )

    print(fires.head())