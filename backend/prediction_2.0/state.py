# state.py

from typing import TypedDict, Annotated
from langchain_core.messages import AnyMessage
import operator


class FireState(TypedDict):
    # LangGraph Messages
    messages: Annotated[list[AnyMessage], operator.add]

    # NASA FIRMS Data
    latitude: float
    longitude: float
    bright_ti4: float
    bright_ti5: float
    frp: float
    confidence: int
    acq_date: str
    acq_time: int
    daynight: str

    # Weather Data
    temperature: float
    humidity: float
    wind_speed: float
    wind_direction: str
    wind_degree: float

    # Classification Output
    fire_type: str
    fire_intensity: str
    heat_level: str
    classification_confidence: float

    # Fire Spread Prediction
    predicted_spread_direction: str
    spread_confidence: float

    # GIS Context
    city: str
    district: str
    state_name: str
    land_cover: str
    nearby_refinery: float
    nearby_pipeline: float
    nearby_hospital: float
    nearby_school: float
    nearby_buildings: int

    # Damage Analysis
    damage_score: float
    damage_category: str
    estimated_burn_area_km2: float
    estimated_burnout_hours: float

    # Risk Analysis
    risk_score: float
    risk_level: str
    critical_radius_km: float
    high_radius_km: float
    infrastructure_risk: str

    # Casualty Estimation
    affected_buildings: int
    affected_population: int
    evacuation_priority: str
    casualty_risk: str

    # AI Reasoning
    spread_reason: str
    damage_reason: str
    risk_reason: str
    casualty_reason: str
    explanation: str

    llm_calls: int