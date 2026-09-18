# agents/damage_agent.py

from langchain_core.messages import AIMessage
from tools.damage_model import predict_damage


def damage_agent(state):
    """
    Estimate fire damage intelligence.
    """

    damage = predict_damage({
        "brightness": state["bright_ti4"],
        "frp": state["frp"],
        "temperature": state["temperature"],
        "humidity": state["humidity"],
        "wind_speed": state["wind_speed"],
        "fire_intensity": state["fire_intensity"],
        "land_cover": state["land_cover"],
        "spread_direction": state["predicted_spread_direction"]
    })

    reasons = []

    if state["frp"] > 50:
        reasons.append(
            f"FRP ({state['frp']} MW) indicates a high-energy fire."
        )

    if state["bright_ti4"] > 400:
        reasons.append(
            f"Brightness ({state['bright_ti4']} K) suggests extreme thermal intensity."
        )

    if state["fire_intensity"] == "Extreme":
        reasons.append(
            "Fire classification indicates Extreme intensity."
        )

    if state["wind_speed"] > 15:
        reasons.append(
            f"Wind speed ({state['wind_speed']} km/h) increases fire spread area."
        )

    if state["humidity"] < 35:
        reasons.append(
            f"Low humidity ({state['humidity']}%) slows natural suppression."
        )

    reasons.append(
        f"Land cover is {state['land_cover']}, increasing potential damage exposure."
    )

    damage_reason = " ".join(reasons)

    return {
        "damage_score": damage["damage_score"],
        "damage_category": damage["damage_category"],
        "estimated_burn_area_km2": damage["estimated_burn_area_km2"],
        "estimated_burnout_hours": damage["estimated_burnout_hours"],

        "damage_reason": damage_reason,

        "messages": [
            AIMessage(
                content=(
                    f"Damage score estimated as {damage['damage_score']}/100 "
                    f"({damage['damage_category']})."
                )
            )
        ]
    }