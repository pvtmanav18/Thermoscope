# agents/firms_loader_agent.py

from langchain_core.messages import AIMessage


def normalize_confidence(value):
    """
    Convert NASA FIRMS confidence to numeric score.
    Works for both MODIS (0-100) and VIIRS (low/nominal/high).
    """

    if value is None:
        return 70

    # Already numeric
    if isinstance(value, (int, float)):
        return int(value)

    value = str(value).strip().lower()

    mapping = {
        "low": 40,
        "nominal": 70,
        "high": 95
    }

    if value in mapping:
        return mapping[value]

    # Numeric stored as string ("85")
    try:
        return int(float(value))
    except ValueError:
        return 70


def firms_loader_agent(state):

    hotspot = {
        "latitude": float(state["latitude"]),
        "longitude": float(state["longitude"]),
        "bright_ti4": float(state["bright_ti4"]),
        "bright_ti5": float(state["bright_ti5"]),
        "frp": float(state["frp"]),
        "confidence": normalize_confidence(state["confidence"]),
        "acq_date": str(state["acq_date"]),
        "acq_time": int(state["acq_time"]),
        "daynight": str(state["daynight"]).upper(),
    }

    return {
        **hotspot,
        "messages": [
            AIMessage(
                content=f"NASA FIRMS hotspot loaded at ({hotspot['latitude']}, {hotspot['longitude']})"
            )
        ]
    }