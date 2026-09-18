# backend/agents/classification_agent.py

import json
import pandas as pd

from tools.geoapify_tool import get_surroundings
from tools.groq_classifier_tool import classify_with_groq
from tools.classifier_tool import calculate_fire_intensity


def classification_agent(input_csv, output_csv):

    df = pd.read_csv(input_csv)

    classified_rows = []

    total = len(df)

    print(f"🔥 Classifying {total} hotspots...")

    for index, row in df.iterrows():

        print(f"{index+1}/{total}")

        # Geo Context
        surroundings = get_surroundings(
            row.latitude,
            row.longitude
        )

    from tools.weather_tool import get_weather_by_coordinates

    # Fetch weather for this hotspot
    weather = get_weather_by_coordinates(row.latitude, row.longitude)

    # Fallback values if Weather API fails
    if weather is None:
        weather = {
            "temperature": 35,
            "humidity": 45,
            "wind_speed": 10,
            "wind_direction": "N"
        }

    fire_data = {
        "bright_ti4": float(row["bright_ti4"]),
        "bright_ti5": float(row["bright_ti5"]),
        "frp": float(row["frp"]),
        "confidence": row["confidence"],
        "temperature": weather["temperature"],
        "humidity": weather["humidity"],
        "wind_speed": weather["wind_speed"],
        "wind_direction": weather["wind_direction"]
    }

    groq_response = classify_with_groq(
        fire_data,
            surroundings
    )

    result = json.loads(groq_response)

    intensity, heat, score = calculate_fire_intensity(
        row.bright_ti4,
        row.frp
    )

    classified_rows.append({
        **row.to_dict(),
        "fire_type": result["fire_type"],
        "classification_reason": result["reason"],
        "fire_intensity": intensity,
        "heat_level": heat,
        "intensity_score": round(score,2),
        "surroundings": json.dumps(surroundings)
    })

    final = pd.DataFrame(classified_rows)

    final.to_csv(output_csv, index=False)

    print("✅ Classification Completed")

    return final

classification_agent("E:\\Manav\\DEVIL\\projects\\SIH2026\\prediction_0.0\\dataset\\dwl_sample.csv", "E:\\Manav\\DEVIL\\projects\\SIH2026\\prediction_3.0\\dataset\\intermediate\\classified_fire_dataset.csv")