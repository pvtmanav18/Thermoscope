# ==========================================
# agents/classification_agent.py
# Geoapify + Groq Classification Agent
# ==========================================

import json

from tools.geoapify_tool import get_geo_context
from tools.groq_classifier import classify_with_groq
from config import config


# ----------------------------------------------------
# Rule-Based Classification
# ----------------------------------------------------
def rule_based_fire_type(geo):
    """
    Fast classification using Geoapify landuse/categories.
    """

    landuse = str(geo.get("landuse", "")).lower()

    categories = " ".join(
        [str(c).lower() for c in geo.get("categories", [])]
    )

    formatted = str(geo.get("formatted", "")).lower()

    text = f"{landuse} {categories} {formatted}"

    # Industrial
    industrial_keywords = [
        "industrial",
        "factory",
        "warehouse",
        "manufacturing",
        "refinery",
        "power",
        "plant",
    ]

    # Commercial
    commercial_keywords = [
        "commercial",
        "mall",
        "market",
        "office",
        "hotel",
        "shop",
        "business",
        "retail",
    ]

    # Forest
    forest_keywords = [
        "forest",
        "woodland",
        "park",
        "wildlife",
        "nature",
        "reserve",
        "jungle",
    ]

    # Agriculture
    agricultural_keywords = [
        "farmland",
        "farm",
        "cropland",
        "agriculture",
        "field",
        "plantation",
        "orchard",
    ]

    # Residential
    residential_keywords = [
        "residential",
        "apartment",
        "housing",
        "village",
        "society",
        "home",
        "building",
    ]

    if any(word in text for word in industrial_keywords):
        return "Industrial Fire"

    if any(word in text for word in commercial_keywords):
        return "Commercial Fire"

    if any(word in text for word in forest_keywords):
        return "Forest Fire"

    if any(word in text for word in agricultural_keywords):
        return "Agricultural Fire"

    if any(word in text for word in residential_keywords):
        return "Residential Fire"

    return "Unknown"


# ----------------------------------------------------
# LangGraph Node
# ----------------------------------------------------
def classification_node(state):
    """
    Main AI classification node.
    """

    fire = state["fire_data"]

    latitude = float(fire["latitude"])
    longitude = float(fire["longitude"])

    # ---------------------------------------
    # Step 1 — Geoapify Context
    # ---------------------------------------
    geo_context = get_geo_context(latitude, longitude)

    state["geo_context"] = geo_context

    # ---------------------------------------
    # Step 2 — Rule-Based Classification
    # ---------------------------------------
    predicted_type = rule_based_fire_type(geo_context)

    # ---------------------------------------
    # Step 3 — Groq Verification
    # ---------------------------------------
    groq_result = classify_with_groq(
        fire_data=fire,
        geo_context=geo_context,
        predicted_type=predicted_type,
    )

    # ---------------------------------------
    # Step 4 — Store Result
    # ---------------------------------------
    state["classification"] = {
        "fire_type": groq_result.get("fire_type", predicted_type),
        "confidence": groq_result.get("confidence", 70),
        "reasoning": groq_result.get(
            "reasoning", "Classification generated using Geoapify context."
        ),
        "rule_prediction": predicted_type,
    }

    state["messages"].append(
        f"{latitude}, {longitude} classified as "
        f"{state['classification']['fire_type']}"
    )

    return state