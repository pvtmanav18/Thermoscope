# ==========================================
# agents/intensity_agent.py
# Fire Intensity Classification
# ==========================================

from config import config


def calculate_intensity(brightness: float, frp: float):
    """
    Calculate fire intensity using Brightness + FRP.
    """

    if brightness >= config.HIGH_BRIGHTNESS or frp >= config.HIGH_FRP:
        return "Extreme", "Very intense fire requiring immediate response."

    if brightness >= config.MODERATE_BRIGHTNESS or frp >= config.MODERATE_FRP:
        return "High", "High energy fire with significant spread potential."

    if brightness >= config.LOW_BRIGHTNESS or frp >= config.LOW_FRP:
        return "Moderate", "Active fire with moderate thermal output."

    return "Low", "Low intensity hotspot or early-stage fire."


def intensity_node(state):
    """
    LangGraph node for fire intensity classification.
    """

    fire = state["fire_data"]

    brightness = float(fire.get("bright_ti4", 0))
    frp = float(fire.get("frp", 0))

    intensity, description = calculate_intensity(brightness, frp)

    state["intensity"] = {
        "intensity_level": intensity,
        "intensity_description": description,
        "brightness": brightness,
        "frp": frp,
    }

    state["messages"].append(
        f"Intensity classified as {intensity} "
        f"(Brightness={brightness}, FRP={frp})"
    )

    return state