# tools/geoapify_tool.py

import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GEOAPIFY_API_KEY")


def get_surroundings(lat, lon, radius=5000):
    """
    Fetch nearby infrastructure around fire hotspot.
    Radius is in meters.
    """

    categories = (
        "building,healthcare.hospital,"
        "education.school,"
        "industrial,"
        "service.fire_station"
    )

    url = (
        "https://api.geoapify.com/v2/places"
        f"?categories={categories}"
        f"&filter=circle:{lon},{lat},{radius}"
        "&limit=200"
        f"&apiKey={API_KEY}"
    )

    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()

        features = response.json().get("features", [])

        buildings = 0
        hospitals = 0
        schools = 0
        industries = 0
        firestations = 0

        nearest_refinery = 9999
        nearest_pipeline = 9999

        for place in features:

            category = ",".join(
                place["properties"].get("categories", [])
            )

            distance = place["properties"].get("distance", 9999)

            if "building" in category:
                buildings += 1

            if "healthcare.hospital" in category:
                hospitals += 1

            if "education.school" in category:
                schools += 1

            if "industrial" in category:
                industries += 1

                nearest_refinery = min(
                    nearest_refinery,
                    distance
                )

            if "fire_station" in category:
                firestations += 1

        return {
            "nearby_buildings": buildings,
            "nearby_hospitals": hospitals,
            "nearby_schools": schools,
            "nearby_industries": industries,
            "nearby_firestations": firestations,
            "nearest_refinery": nearest_refinery,
            "nearest_pipeline": nearest_pipeline,
            "land_cover": (
                "Industrial"
                if industries > 5
                else "Urban"
            )
        }

    except Exception as e:

        print("Geoapify Error:", e)

        return {
            "nearby_buildings": 0,
            "nearby_hospitals": 0,
            "nearby_schools": 0,
            "nearby_industries": 0,
            "nearby_firestations": 0,
            "nearest_refinery": 9999,
            "nearest_pipeline": 9999,
            "land_cover": "Unknown"
        }