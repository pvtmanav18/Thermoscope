# tools/weather_tool.py

import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_URL = "https://api.weatherstack.com/current"
API_KEY = "68d14f75c15a1473bcdc23719f061342"


def get_weather_by_coordinates(lat, lon):
    """
    Fetch weather using latitude and longitude.

    Returns:
        {
            temperature,
            humidity,
            wind_speed,
            wind_direction,
            wind_degree
        }
    """

    params = {
        "access_key": API_KEY,
        "query": f"{lat},{lon}",
        "units": "m"
    }

    try:
        response = requests.get(API_URL, params=params, timeout=10)
        data = response.json()

        if "error" in data:
            print(f"Weather API Error ({lat}, {lon})")
            return None

        current = data["current"]

        return {
            "temperature": current["temperature"],
            "humidity": current["humidity"],
            "wind_speed": current["wind_speed"],
            "wind_direction": current["wind_dir"].upper(),
            "wind_degree": current["wind_degree"]
        }

    except Exception as e:
        print("Weather Fetch Error:", e)
        return None