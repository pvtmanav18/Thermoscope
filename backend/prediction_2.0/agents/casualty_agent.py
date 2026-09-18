# agents/casualty_agent.py

from langchain_core.messages import AIMessage
from tools.casualty_model import predict_casualties


def casualty_agent(state):
    """
    Estimate affected buildings and population.
    """

    casualty = predict_casualties({
        "land_cover": state["land_cover"],
        "burn_area": state["estimated_burn_area_km2"],
        "risk_level": state["risk_level"],
        "nearby_buildings": state["nearby_buildings"],
        "fire_type": state["fire_type"]
    })

    reasons = []

    reasons.append(
        f"Land cover is {state['land_cover']}."
    )

    reasons.append(
        f"Estimated burn area is {state['estimated_burn_area_km2']} km²."
    )

    reasons.append(
        f"Nearby buildings estimated: {state['nearby_buildings']}."
    )

    if state["risk_level"] == "Critical":
        reasons.append(
            "Critical risk level requires immediate evacuation planning."
        )

    elif state["risk_level"] == "High":
        reasons.append(
            "High-risk zone may affect nearby settlements."
        )

    if state["fire_type"] == "Industrial Fire":
        reasons.append(
            "Industrial workers and nearby industrial facilities may be affected first."
        )

    casualty_reason = " ".join(reasons)

    return {
        "affected_buildings": casualty["affected_buildings"],
        "affected_population": casualty["affected_population"],
        "evacuation_priority": casualty["evacuation_priority"],
        "casualty_risk": casualty["casualty_risk"],
        "casualty_reason": casualty_reason,

        "messages": [
            AIMessage(
                content=(
                    f"Estimated affected population: "
                    f"{casualty['affected_population']}."
                )
            )
        ]
    }