# ==========================================
# api.py
# Unified FastAPI Backend — Agni Chakshu
# Serves classified fire data from the
# LangGraph classification agent to the
# React frontend map.
# ==========================================

import os
import sys
import pandas as pd
from typing import Optional
from datetime import datetime
from dotenv import load_dotenv
import requests

load_dotenv()

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==========================================
# App Setup
# ==========================================

app = FastAPI(
    title="Agni Chakshu — Fire Intelligence API",
    description="Serves AI-classified fire hotspot data from the LangGraph classification agent",
    version="2.0.0",
)

# Allow React Frontend (Vite on 5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://thermoscope-qaq0.onrender.com",
        "https://thermoscope.vercel.app",
        

    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# Path Resolution
# ==========================================

# Resolve the classified fires CSV relative to this file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CLASSIFIED_CSV = os.path.join(
    BASE_DIR,
    "fire_classification_agent",
    "outputs",
    "classified_fires.csv",
)
VIIRS_CSV = os.path.join(
    BASE_DIR,
    "..",
    "dataset",
    "J2_VIIRS_C2_South_Asia_24h.csv",
)


def load_classified_fires() -> pd.DataFrame:
    """
    Load the classified fire data from CSV.
    Returns an empty DataFrame if not found.
    """
    if not os.path.exists(CLASSIFIED_CSV):
        logger.warning(f"Classified fires CSV not found at: {CLASSIFIED_CSV}")
        return pd.DataFrame()

    try:
        df = pd.read_csv(CLASSIFIED_CSV)
        logger.info(f"Loaded {len(df)} classified fire records from {CLASSIFIED_CSV}")
        return df
    except Exception as e:
        logger.error(f"Error loading classified fires: {e}")
        return pd.DataFrame()

def load_raw_fires() -> pd.DataFrame:
    """
    Load the raw VIIRS fire data from CSV.
    Returns an empty DataFrame if not found.
    """
    if not os.path.exists(VIIRS_CSV):
        logger.warning(f"VIIRS fires CSV not found at: {VIIRS_CSV}")
        return pd.DataFrame()

    try:
        df = pd.read_csv(VIIRS_CSV)
        logger.info(f"Loaded {len(df)} VIIRS fire records from {VIIRS_CSV}")
        return df
    except Exception as e:
        logger.error(f"Error loading VIIRS fires: {e}")
        return pd.DataFrame()


# ==========================================
# Endpoints
# ==========================================


@app.get("/")
def root():
    """Health check / root endpoint."""
    return {
        "service": "Agni Chakshu — Fire Intelligence API",
        "version": "2.0.0",
        "status": "operational",
        "csv_path": CLASSIFIED_CSV,
        "csv_exists": os.path.exists(CLASSIFIED_CSV),
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/health")
def health():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/raw-fires")
def get_raw_fires(limit: Optional[int] = Query(None, description="Max records to return")):
    """
    Returns unclassified (raw) fires from the dataset.
    """
    df = load_raw_fires()

    if limit is not None:
        df = df.head(limit)

    fires = df.to_dict(orient="records")
    return {"count": len(fires), "fires": fires}

@app.get("/dashboard-stats")
def get_dashboard_stats():
    """
    Fetches real-time data from NASA FIRMS if FIRMS_API_KEY is present,
    otherwise falls back to the local VIIRS_CSV dataset to compute live stats.
    """
    firms_key = os.getenv("FIRMS_API_KEY")
    df = pd.DataFrame()
    
    if firms_key:
        try:
            url = f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/{firms_key}/VIIRS_SNPP_NRT/world/1"
            logger.info(f"Fetching live NASA FIRMS data using API key...")
            df = pd.read_csv(url)
        except Exception as e:
            logger.error(f"Failed to fetch NASA FIRMS data: {e}")
            
    # Fallback to local dataset if API fetch failed or no key
    if df.empty:
        logger.info("Falling back to local VIIRS dataset for dashboard stats.")
        df = load_raw_fires()
        
    if df.empty:
        raise HTTPException(status_code=404, detail="No fire data available for dashboard")

    # ----- KPI Calculations -----
    active_fires = len(df)
    critical_alerts = len(df[df['frp'] > 50]) if 'frp' in df.columns else 0
    satellites = df['satellite'].nunique() if 'satellite' in df.columns else 1
    
    # Map string confidence to numeric for averaging
    ai_conf = 0
    if 'confidence' in df.columns:
        conf_map = {'l': 30, 'n': 60, 'h': 90, 'low': 30, 'nominal': 60, 'high': 90}
        mapped = df['confidence'].replace(conf_map)
        mapped = pd.to_numeric(mapped, errors='coerce').dropna()
        ai_conf = int(mapped.mean()) if not mapped.empty else 0

    # ----- Heat Trend (24h) -----
    # Group by acquisition time hour
    heat_trend = []
    if 'acq_time' in df.columns and 'frp' in df.columns:
        # acq_time is often something like 553 (05:53). We divide by 100 to get hours
        df['hour'] = (pd.to_numeric(df['acq_time'], errors='coerce') // 100).fillna(0).astype(int)
        hourly_frp = df.groupby('hour')['frp'].mean().reset_index()
        # Sort and take top few or just 6 representative points
        hourly_frp = hourly_frp.sort_values('hour')
        for _, row in hourly_frp.iterrows():
            time_str = f"{int(row['hour']):02d}:00"
            heat_trend.append({"time": time_str, "heat": int(row['frp'])})
            
    # Fallback default if empty
    if not heat_trend:
        heat_trend = [
            {"time": "00:00", "heat": 30}, {"time": "04:00", "heat": 45}, 
            {"time": "08:00", "heat": 85}, {"time": "12:00", "heat": 120},
            {"time": "16:00", "heat": 110}, {"time": "20:00", "heat": 75}
        ]

    # ----- Anomalies by Region -----
    # Using lat/lon quadrant to mock regions
    region_data = []
    if 'latitude' in df.columns and 'longitude' in df.columns:
        df['lat_bin'] = pd.cut(df['latitude'], bins=4, labels=["South", "Mid-South", "Mid-North", "North"])
        anomalies = df['lat_bin'].value_counts().reset_index()
        anomalies.columns = ['name', 'value']
        colors = ['#ef4444', '#f97316', '#3b82f6', '#22c55e']
        for idx, row in anomalies.iterrows():
            region_data.append({"name": str(row['name']), "value": int(row['value']), "color": colors[idx % len(colors)]})
    
    if not region_data:
        region_data = [
            { "name": "North", "value": 35, "color": "#ef4444" },
            { "name": "South", "value": 25, "color": "#f97316" }
        ]

    # ----- Source Types -----
    source_data = []
    if 'satellite' in df.columns:
        sources = df['satellite'].value_counts().reset_index()
        sources.columns = ['name', 'value']
        for _, row in sources.iterrows():
            source_data.append({"name": str(row['name']), "value": int(row['value'])})
            
    if not source_data:
        source_data = [
            { "name": "VIIRS (N21)", "value": 45 },
            { "name": "MODIS (Terra)", "value": 30 }
        ]

    return {
        "kpis": {
            "active_fires": active_fires,
            "critical_alerts": critical_alerts,
            "satellites": f"{satellites}/8",
            "ai_confidence": f"{ai_conf}%",
            "monitored_area": "4.2M",
            "persistent_sources": str(int(active_fires * 0.15))
        },
        "charts": {
            "heatTrend": heat_trend,
            "regionData": region_data,
            "sourceData": source_data
        }
    }


@app.get("/fires")
def get_fires():
    """
    Return classified fires in the format expected by MapMockup.jsx.
    Each fire has: id, latitude, longitude, country, city, fire_type,
    intensity, reasoning, confidence, brightness, frp, and more.
    """
    df = load_classified_fires()

    if df.empty:
        return {"count": 0, "fires": [], "source": "classified_fires.csv"}

    fires = []

    for idx, row in df.iterrows():
        fire = {
            "id": idx,
            # Core location
            "latitude": _safe_float(row.get("latitude")),
            "longitude": _safe_float(row.get("longitude")),
            "country": _safe_str(row.get("country", "")),
            "city": _safe_str(row.get("city", "")),
            # Classification (from LangGraph agent)
            "fire_type": _safe_str(row.get("fire_type", "Unknown")),
            "intensity": _safe_str(row.get("intensity_level", "Unknown")),
            "intensity_description": _safe_str(row.get("intensity_description", "")),
            "reasoning": _safe_str(row.get("reasoning", "")),
            "confidence": _safe_int(row.get("confidence", 70)),
            "rule_prediction": _safe_str(row.get("rule_prediction", "")),
            # FIRMS satellite data
            "brightness": _safe_float(row.get("bright_ti4", 0)),
            "bright_ti5": _safe_float(row.get("bright_ti5", 0)),
            "frp": _safe_float(row.get("frp", 0)),
            "scan": _safe_float(row.get("scan", 0)),
            "track": _safe_float(row.get("track", 0)),
            "acq_date": _safe_str(row.get("acq_date", "")),
            "acq_time": _safe_str(str(row.get("acq_time", ""))),
            "satellite": _safe_str(row.get("satellite", "")),
            "daynight": _safe_str(row.get("daynight", "")),
            # Weather data
            "temperature": _safe_float(row.get("temperature", 0)),
            "humidity": _safe_float(row.get("humidity", 0)),
            "wind_speed": _safe_float(row.get("wind_speed", 0)),
            "wind_direction": _safe_str(row.get("wind_direction", "")),
            "wind_degree": _safe_float(row.get("wind_degree", 0)),
            # Geo context
            "landuse": _safe_str(row.get("landuse", "")),
            "result_type": _safe_str(row.get("result_type", "")),
        }

        fires.append(fire)

    return {
        "count": len(fires),
        "fires": fires,
        "source": "classified_fires.csv",
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/api/classified-fires")
def get_classified_fires_geojson():
    """
    Return classified fires as a GeoJSON FeatureCollection.
    For direct use in mapping libraries (Leaflet, Mapbox, etc).
    """
    df = load_classified_fires()

    if df.empty:
        return {"type": "FeatureCollection", "features": [], "metadata": {"count": 0}}

    features = []

    for idx, row in df.iterrows():
        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [
                    _safe_float(row.get("longitude")),
                    _safe_float(row.get("latitude")),
                ],
            },
            "properties": {
                "id": idx,
                # Classification
                "fire_type": _safe_str(row.get("fire_type", "Unknown")),
                "intensity_level": _safe_str(row.get("intensity_level", "Unknown")),
                "intensity_description": _safe_str(row.get("intensity_description", "")),
                "reasoning": _safe_str(row.get("reasoning", "")),
                "confidence": _safe_int(row.get("confidence", 70)),
                "rule_prediction": _safe_str(row.get("rule_prediction", "")),
                # Location
                "country": _safe_str(row.get("country", "")),
                "city": _safe_str(row.get("city", "")),
                "landuse": _safe_str(row.get("landuse", "")),
                # FIRMS data
                "brightness": _safe_float(row.get("bright_ti4", 0)),
                "frp": _safe_float(row.get("frp", 0)),
                "satellite": _safe_str(row.get("satellite", "")),
                "acq_date": _safe_str(row.get("acq_date", "")),
                "acq_time": _safe_str(str(row.get("acq_time", ""))),
                "daynight": _safe_str(row.get("daynight", "")),
                # Weather
                "temperature": _safe_float(row.get("temperature", 0)),
                "humidity": _safe_float(row.get("humidity", 0)),
                "wind_speed": _safe_float(row.get("wind_speed", 0)),
                "wind_direction": _safe_str(row.get("wind_direction", "")),
                "wind_degree": _safe_float(row.get("wind_degree", 0)),
            },
        }
        features.append(feature)

    return {
        "type": "FeatureCollection",
        "features": features,
        "metadata": {
            "count": len(features),
            "timestamp": datetime.now().isoformat(),
            "source": "fire_classification_agent",
        },
    }


@app.get("/api/stats")
def get_fire_stats():
    """
    Return fire type distribution and summary statistics.
    """
    df = load_classified_fires()

    if df.empty:
        return {"total": 0, "by_type": {}, "by_intensity": {}}

    # Fire type distribution
    type_counts = {}
    if "fire_type" in df.columns:
        type_counts = df["fire_type"].value_counts().to_dict()

    # Intensity distribution
    intensity_counts = {}
    if "intensity_level" in df.columns:
        intensity_counts = df["intensity_level"].value_counts().to_dict()

    # Country distribution
    country_counts = {}
    if "country" in df.columns:
        country_counts = df["country"].value_counts().to_dict()

    return {
        "total": len(df),
        "by_type": type_counts,
        "by_intensity": intensity_counts,
        "by_country": country_counts,
        "timestamp": datetime.now().isoformat(),
    }


# ==========================================
# Helpers
# ==========================================


def _safe_float(val, default=0.0) -> float:
    """Safely convert to float."""
    try:
        if pd.isna(val):
            return default
        return float(val)
    except (ValueError, TypeError):
        return default


def _safe_int(val, default=0) -> int:
    """Safely convert to int."""
    try:
        if pd.isna(val):
            return default
        return int(float(val))
    except (ValueError, TypeError):
        return default


def _safe_str(val, default="") -> str:
    """Safely convert to string, handling NaN."""
    try:
        if pd.isna(val):
            return default
        return str(val).strip()
    except (ValueError, TypeError):
        return default


# ==========================================
# Entry Point
# ==========================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)