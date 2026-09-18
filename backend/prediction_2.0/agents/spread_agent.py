# agents/spread_agent.py

from langchain_core.messages import AIMessage
from tools.spread_model import predict_spread


def fire_spread_agent(state):
    """
    Predict fire spread direction using
    NASA FIRMS + Weather information.
    """

    prediction = predict_spread({
        "brightness": state["bright_ti4"],
        "frp": state["frp"],
        "temperature": state["temperature"],
        "humidity": state["humidity"],
        "wind_speed": state["wind_speed"],
        "wind_direction": state["wind_direction"]
    })

    direction = prediction["predicted_spread_direction"]
    confidence = prediction["confidence"]

    # -----------------------------
    # Reasoning
    # -----------------------------
    reasons = []

    if state["wind_speed"] > 15:
        reasons.append(
            f"Strong wind ({state['wind_speed']} km/h) is pushing flames toward {direction}."
        )
    else:
        reasons.append(
            f"Wind direction favors spread toward {direction}."
        )

    if state["humidity"] < 35:
        reasons.append(
            f"Low humidity ({state['humidity']}%) increases fire spread potential."
        )

    if state["temperature"] > 35:
        reasons.append(
            f"High temperature ({state['temperature']}°C) increases fuel dryness."
        )

    if state["frp"] > 50:
        reasons.append(
            f"High Fire Radiative Power ({state['frp']} MW) indicates an active high-energy fire."
        )

    spread_reason = " ".join(reasons)

    return {
        "predicted_spread_direction": direction,
        "spread_confidence": confidence,
        "spread_reason": spread_reason,

        "messages": [
            AIMessage(
                content=f"Predicted fire spread toward {direction} ({confidence}% confidence)."
            )
        ]
    }