# ==========================
# config.py
# ==========================

import os
from dotenv import load_dotenv

load_dotenv()


class Config:

    # -------------------------
    # API KEYS
    # -------------------------
    NASA_API_KEY = os.getenv("NASA_API_KEY")
    GEOAPIFY_API_KEY = os.getenv("GEOAPIFY_API_KEY")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")

    # -------------------------
    # Models
    # -------------------------
    GROQ_MODEL = "openai/gpt-oss-120b"

    # -------------------------
    # NASA FIRMS
    # -------------------------
    DAYS = 7
    MAX_FIRE_RECORDS = 50

    # -------------------------
    # File Paths
    # -------------------------
    INPUT_CSV = "data/nasa_fires.csv"
    OUTPUT_CSV = "outputs/classified_fires.csv"

    # -------------------------
    # Geoapify API URLs
    # -------------------------
    GEOAPIFY_REVERSE_URL = (
        "https://api.geoapify.com/v1/geocode/reverse"
    )

    GEOAPIFY_PLACES_URL = (
        "https://api.geoapify.com/v2/places"
    )

    # -------------------------
    # Classification Labels
    # -------------------------
    FIRE_TYPES = [
        "Industrial Fire",
        "Commercial Fire",
        "Forest Fire",
        "Agricultural Fire",
        "Residential Fire"
    ]

    # -------------------------
    # Intensity Thresholds
    # -------------------------
    LOW_BRIGHTNESS = 320
    MODERATE_BRIGHTNESS = 335
    HIGH_BRIGHTNESS = 345

    LOW_FRP = 2
    MODERATE_FRP = 8
    HIGH_FRP = 15


config = Config()



