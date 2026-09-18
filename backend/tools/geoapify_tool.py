# ==========================================
# tools/geoapify_tool.py
# Geoapify Reverse Geocoder + Places API
# ==========================================

import requests
from config import config

HEADERS = {
    "User-Agent": "SIH-Fire-Classification-Agent/1.0"
}


def reverse_geocode(latitude, longitude):
    """
    Reverse geocode coordinates using Geoapify.
    """

    params = {
        "lat": latitude,
        "lon": longitude,
        "apiKey": "ceaf5fcfaf6043c6bd74c47e8eb10cf0"
    }

    try:
        response = requests.get(
            config.GEOAPIFY_REVERSE_URL,
            params=params,
            headers=HEADERS,
            timeout=20
        )

        response.raise_for_status()

        data = response.json()

        if not data.get("features"):
            return {}

        props = data["features"][0]["properties"]

        return {
            "country": props.get("country", ""),
            "city": props.get("city", ""),
            "result_type": props.get("result_type", ""),
        }

    except Exception as e:
        print("Reverse Geocode Error:", e)
        return {}


def nearby_places(latitude, longitude):
    """
    Fetch nearby places within 500 meters.
    """

    categories = (
        "commercial,industrial,building,"
        "natural,park,forest,agriculture"
    )

    params = {
        "categories": categories,
        "filter": f"circle:{longitude},{latitude},500",
        "limit": 15,
        "apiKey": config.GEOAPIFY_API_KEY
    }

    try:

        response = requests.get(
            config.GEOAPIFY_PLACES_URL,
            params=params,
            headers=HEADERS,
            timeout=20
        )

        response.raise_for_status()

        data = response.json()

        places = []

        for feature in data.get("features", []):

            prop = feature["properties"]

            places.append({
                "name": prop.get("name", ""),
                "categories": prop.get("categories", []),
                "formatted": prop.get("formatted", "")
            })

        return places

    except Exception as e:
        print("Nearby Places Error:", e)
        return []


def detect_landuse_from_places(places):
    """
    Infer landuse from nearby place categories.
    """

    text = " ".join(
        [
            " ".join(p["categories"])
            for p in places
        ]
    ).lower()

    if "industrial" in text:
        return "industrial"

    if "commercial" in text:
        return "commercial"

    if "forest" in text or "park" in text:
        return "forest"

    if "agriculture" in text or "farm" in text:
        return "agriculture"

    if "building" in text or "residential" in text:
        return "residential"

    return "unknown"


def get_geo_context(latitude, longitude):
    """
    Combined Geoapify Context.
    """

    location = reverse_geocode(latitude, longitude)

    places = nearby_places(latitude, longitude)

    if not location.get("landuse"):
        location["landuse"] = detect_landuse_from_places(places)

    location["nearby_places"] = places

    location["nearby_place_names"] = [
        p["name"]
        for p in places
        if p["name"]
    ]

    return location