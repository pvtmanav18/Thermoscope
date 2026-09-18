# test_pipeline.py

import os
import pandas as pd

from graph import fire_graph
from tools.firms_tool import load_firms_dataset

# ---------------------------------------------------
# Dataset Paths
# ---------------------------------------------------

INPUT_CSV = "E:\\Manav\\DEVIL\\projects\\SIH2026\\prediction_2.0\\dataset\\input\\firms_data.csv"

INTERMEDIATE_WEATHER = "dataset/intermediate/firms_weather_dataset.csv"
INTERMEDIATE_CLASSIFIED = "dataset/intermediate/classified_fire_dataset.csv"

OUTPUT_CSV = "dataset/output/final_fire_intelligence_dataset.csv"

# Create folders automatically
os.makedirs("dataset/intermediate", exist_ok=True)
os.makedirs("dataset/output", exist_ok=True)

# ---------------------------------------------------
# Load FIRMS Dataset
# ---------------------------------------------------

df = load_firms_dataset(INPUT_CSV)

print("=" * 70)
print("🔥 NTRO SENTINEL FIRE INTELLIGENCE PIPELINE")
print("=" * 70)
print(f"Detected Hotspots : {len(df)}")
print("=" * 70)

results = []

# ---------------------------------------------------
# Run LangGraph For Every Hotspot
# ---------------------------------------------------

for index, row in df.iterrows():

    print(f"\n📍 Processing Hotspot {index+1}/{len(df)}")

    state = {

        "messages": [],

        # FIRMS
        "latitude": row["latitude"],
        "longitude": row["longitude"],
        "bright_ti4": row["bright_ti4"],
        "bright_ti5": row["bright_ti5"],
        "frp": row["frp"],
        "confidence": row["confidence"],
        "acq_date": row["acq_date"],
        "acq_time": row["acq_time"],
        "daynight": row["daynight"],

        # Weather
        "temperature": 0,
        "humidity": 0,
        "wind_speed": 0,
        "wind_direction": "",
        "wind_degree": 0,

        # Classification
        "fire_type": "",
        "fire_intensity": "",
        "heat_level": "",
        "classification_confidence": 0,

        # Spread
        "predicted_spread_direction": "",
        "spread_confidence": 0,

        # GIS
        "city": "",
        "district": "",
        "state_name": "",
        "land_cover": "",
        "nearby_refinery": 9999,
        "nearby_pipeline": 9999,
        "nearby_hospital": 9999,
        "nearby_school": 9999,
        "nearby_buildings": 0,

        # Damage
        "damage_score": 0,
        "damage_category": "",
        "estimated_burn_area_km2": 0,
        "estimated_burnout_hours": 0,

        # Risk
        "risk_score": 0,
        "risk_level": "",
        "critical_radius_km": 0,
        "high_radius_km": 0,
        "infrastructure_risk": "",

        # Casualty
        "affected_buildings": 0,
        "affected_population": 0,
        "evacuation_priority": "",
        "casualty_risk": "",

        # AI Reasoning
        "spread_reason": "",
        "damage_reason": "",
        "risk_reason": "",
        "casualty_reason": "",
        "explanation": "",

        "llm_calls": 0,
    }

    # Run complete LangGraph
    result = fire_graph.invoke(state)

    # Save output row
    results.append({

        # Original FIRMS Data
        **row.to_dict(),

        # Weather
        "temperature": result["temperature"],
        "humidity": result["humidity"],
        "wind_speed": result["wind_speed"],
        "wind_direction": result["wind_direction"],
        "wind_degree": result["wind_degree"],

        # Classification
        "fire_type": result["fire_type"],
        "fire_intensity": result["fire_intensity"],
        "heat_level": result["heat_level"],
        "classification_confidence": result["classification_confidence"],

        # Spread
        "predicted_spread_direction": result["predicted_spread_direction"],
        "spread_confidence": result["spread_confidence"],

        # GIS
        "city": result["city"],
        "district": result["district"],
        "state": result["state_name"],
        "land_cover": result["land_cover"],

        "nearby_refinery": result["nearby_refinery"],
        "nearby_pipeline": result["nearby_pipeline"],
        "nearby_hospital": result["nearby_hospital"],
        "nearby_school": result["nearby_school"],
        "nearby_buildings": result["nearby_buildings"],

        # Damage
        "damage_score": result["damage_score"],
        "damage_category": result["damage_category"],
        "estimated_burn_area_km2": result["estimated_burn_area_km2"],
        "estimated_burnout_hours": result["estimated_burnout_hours"],

        # Risk
        "risk_score": result["risk_score"],
        "risk_level": result["risk_level"],
        "critical_radius_km": result["critical_radius_km"],
        "high_radius_km": result["high_radius_km"],
        "infrastructure_risk": result["infrastructure_risk"],

        # Casualty
        "affected_buildings": result["affected_buildings"],
        "affected_population": result["affected_population"],
        "evacuation_priority": result["evacuation_priority"],
        "casualty_risk": result["casualty_risk"],

        # AI Reasons
        "spread_reason": result["spread_reason"],
        "damage_reason": result["damage_reason"],
        "risk_reason": result["risk_reason"],
        "casualty_reason": result["casualty_reason"],

        # Final AI Report
        "ai_explanation": result["explanation"]
    })

    # Console Summary
    print(
        f"   🌍 {result['city']}, {result['state_name']}"
    )
    print(
        f"   🔥 {result['fire_type']} | {result['fire_intensity']}"
    )
    print(
        f"   🧭 Spread : {result['predicted_spread_direction']} ({result['spread_confidence']}%)"
    )
    print(
        f"   💥 Damage : {result['damage_score']}/100"
    )
    print(
        f"   ⚠ Risk   : {result['risk_level']}"
    )
    print(
        f"   👥 Population : {result['affected_population']}"
    )

# ---------------------------------------------------
# Save Final Dataset
# ---------------------------------------------------

final_df = pd.DataFrame(results)

final_df.to_csv(OUTPUT_CSV, index=False)

print("\n" + "=" * 70)
print("✅ NTRO SENTINEL ANALYSIS COMPLETED")
print("=" * 70)
print(f"Processed Hotspots : {len(final_df)}")
print(f"Saved Dataset      : {OUTPUT_CSV}")
print("=" * 70)

print("\nPreview:\n")

print(
    final_df[
        [
            "city",
            "fire_type",
            "fire_intensity",
            "predicted_spread_direction",
            "damage_score",
            "risk_level",
            "affected_population"
        ]
    ].head()
)