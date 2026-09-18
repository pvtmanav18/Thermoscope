# agents/classification_agent.py

import pandas as pd
from langchain_core.messages import AIMessage

CLASSIFIED_DATASET = "dataset/intermediate/classified_fire_dataset.csv"


def classification_agent(state):
    """
    Match the current hotspot with the classification dataset.
    """

    try:
        df = pd.read_csv(CLASSIFIED_DATASET)

        # Round coordinates for matching
        df["latitude"] = df["latitude"].round(4)
        df["longitude"] = df["longitude"].round(4)

        lat = round(state["latitude"], 4)
        lon = round(state["longitude"], 4)

        hotspot = df[
            (df["latitude"] == lat) &
            (df["longitude"] == lon)
        ]

        if not hotspot.empty:
            row = hotspot.iloc[0]

            fire_type = row["fire_type"]
            fire_intensity = row["fire_intensity"]
            heat_level = row["heat_level"]
            confidence = float(row["classification_confidence"])

        else:
            fire_type = "Unknown Fire"
            fire_intensity = "Medium"
            heat_level = "Moderate"
            confidence = 50.0

    except Exception as e:
        print("Classification Error:", e)

        fire_type = "Unknown Fire"
        fire_intensity = "Medium"
        heat_level = "Moderate"
        confidence = 50.0

    return {
        "fire_type": fire_type,
        "fire_intensity": fire_intensity,
        "heat_level": heat_level,
        "classification_confidence": confidence,

        "messages": [
            AIMessage(
                content=(
                    f"Fire classified as {fire_type} "
                    f"with {fire_intensity} intensity."
                )
            )
        ]
    }