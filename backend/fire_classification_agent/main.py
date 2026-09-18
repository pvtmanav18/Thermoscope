# ==========================
# main.py
# AI Fire Classification Agent
# NASA FIRMS + Geoapify + Groq + LangGraph
# ==========================

import os
import pandas as pd
from dotenv import load_dotenv

from graph import build_graph
from state import FireState

# Load environment variables
load_dotenv()

INPUT_CSV = "E:\\Manav\\DEVIL\\projects\\SIH2026\\fire_classification_agent\\data\\dwl_firms_weather_dataset.csv"
OUTPUT_CSV = "E:\\Manav\\DEVIL\\projects\\SIH2026\\fire_classification_agent\\outputs\\classified_fires.csv"


def load_fire_data(csv_path: str) -> pd.DataFrame:
    """Load NASA FIRMS fire hotspot dataset."""
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Input CSV not found: {csv_path}")

    df = pd.read_csv(csv_path)
    print(f"Loaded {len(df)} fire hotspots.")
    return df


def classify_dataset(df: pd.DataFrame):
    """Run LangGraph classification for each hotspot."""

    graph = build_graph()
    results = []

    for idx, row in df.iterrows():

        print(f"Processing Fire {idx + 1}/{len(df)}")

        state: FireState = {
            "fire_data": row.to_dict(),
            "geo_context": {},
            "classification": {},
            "intensity": {},
            "messages": []
        }

        result = graph.invoke(state)

        output = {
            **row.to_dict(),
            **result["geo_context"],
            **result["classification"],
            **result["intensity"]
        }

        results.append(output)

    return pd.DataFrame(results)


def save_results(df):
    os.makedirs("outputs", exist_ok=True)
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"\n Classified fires saved to {OUTPUT_CSV}")


def main():

    df = load_fire_data(INPUT_CSV)

    classified_df = classify_dataset(df)

    save_results(classified_df)

    print("\n Classification Complete.")


if __name__ == "__main__":
    main()