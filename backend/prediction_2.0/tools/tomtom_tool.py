# tools/tomtom_tool.py

import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("TOMTOM_API_KEY")


def reverse_geocode(lat, lon):
    """
    Reverse geocode coordinates into city/state.
    """

    url = (
        "https://api.tomtom.com/search/2/reverseGeocode/"
        f"{lat},{lon}.json"
    )

    params = {
        "key": API_KEY
    }

    try:
        response = requests.get(
            url,
            params=params,
            timeout=10
        )

        response.raise_for_status()

        addresses = response.json().get(
            "addresses",
            []
        )

        if not addresses:
            return {}

        address = addresses[0]["address"]

        return {
            "city": address.get(
                "municipality",
                "Unknown City"
            ),
            "district": address.get(
                "municipalitySubdivision",
                "Unknown District"
            ),
            "state_name": address.get(
                "countrySubdivision",
                "Unknown State"
            ),
            "country": address.get(
                "country",
                "Unknown Country"
            ),
            "formatted_address": address.get(
                "freeformAddress",
                ""
            )
        }

    except Exception as e:

        print("TomTom Error:", e)

        return {
            "city": "Unknown City",
            "district": "Unknown District",
            "state_name": "Unknown State",
            "country": "Unknown Country",
            "formatted_address": ""
        }