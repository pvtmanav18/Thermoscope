# ==========================================
# tools/groq_classifier.py
# Groq Fire Classification Agent
# ==========================================

import json
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage

from config import config

llm = ChatGroq(
    model="openai/gpt-oss-120b",
    api_key="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",
    temperature=0.1
)


def build_prompt(fire_data, geo_context, predicted_type):

    return f"""
You are a satellite wildfire classification expert.

Your job is to classify ONE fire hotspot into exactly ONE category.

Possible Categories:
1. Industrial Fire
2. Commercial Fire
3. Forest Fire
4. Agricultural Fire
5. Residential Fire

-----------------------------
NASA FIRMS DATA

Latitude: {fire_data.get("latitude")}
Longitude: {fire_data.get("longitude")}

Brightness: {fire_data.get("bright_ti4")}
FRP: {fire_data.get("frp")}
Satellite Confidence: {fire_data.get("confidence")}

-----------------------------
GEOAPIFY CONTEXT

Country:
{geo_context.get("country")}

City:
{geo_context.get("city")}



-----------------------------
Rule-Based Prediction

{predicted_type}

-----------------------------

Return ONLY valid JSON.

{{
    "fire_type":"Industrial Fire",
    "confidence":96,
    "reasoning":"Reason within 40 words."
}}
"""


def classify_with_groq(fire_data, geo_context, predicted_type):
    """
    Returns structured classification JSON.
    """

    prompt = build_prompt(
        fire_data,
        geo_context,
        predicted_type
    )

    try:

        response = llm.invoke(
            [HumanMessage(content=prompt)]
        )

        content = response.content.strip()

        if "```json" in content:
            content = (
                content.replace("```json", "")
                .replace("```", "")
                .strip()
            )

        result = json.loads(content)

        return result

    except Exception as e:

        print("Groq Error:", e)

        return {
            "fire_type": predicted_type,
            "confidence": 70,
            "reasoning": "Fallback classification because Groq parsing failed."
        }