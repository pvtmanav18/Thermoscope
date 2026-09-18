# backend/tools/geoapify_tool.py

import requests

BASE_URL = "https://api.geoapify.com/v2/places"

CATEGORIES = [
    "building",
    "industrial",
    "commercial",
    "forest",
    "natural",
    "agriculture",
    "park",
    "landuse",
    "power",
    "fuel"
]

def get_surroundings(lat, lon, radius=1000):

    categories = ",".join(CATEGORIES)

    params = {
        "categories": categories,
        "filter": f"circle:{lon},{lat},{radius}",
        "limit": 100,
        "apiKey": "ceaf5fcfaf6043c6bd74c47e8eb10cf0"
    }

    response = requests.get(BASE_URL, params=params, timeout=20)

    if response.status_code != 200:
        return {}

    features = response.json().get("features", [])

    summary = {
        "buildings": 0,
        "industrial": 0,
        "commercial": 0,
        "forest": 0,
        "agriculture": 0,
        "power": 0,
        "fuel": 0
    }

    for place in features:

        cats = place["properties"].get("categories", [])

        for c in cats:

            if "building" in c:
                summary["buildings"] += 1

            if "industrial" in c:
                summary["industrial"] += 1

            if "commercial" in c:
                summary["commercial"] += 1

            if "forest" in c or "natural" in c:
                summary["forest"] += 1

            if "agriculture" in c or "farm" in c:
                summary["agriculture"] += 1

            if "power" in c:
                summary["power"] += 1

            if "fuel" in c:
                summary["fuel"] += 1

    return summary