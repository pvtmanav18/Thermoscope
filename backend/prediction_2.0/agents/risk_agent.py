# agents/risk_agent.py

from langchain_core.messages import AIMessage
from tools.risk_model import predict_risk


def risk_agent(state):
    """
    Analyze risk level based on damage, fire type,
    spread prediction and nearby infrastructure.
    """

    risk = predict_risk({
        "fire_type": state["fire_type"],
        "fire_intensity": state["fire_intensity"],
        "damage_score": state["damage_score"],
        "burn_area": state["estimated_burn_area_km2"],
        "land_cover": state["land_cover"],
        "wind_speed": state["wind_speed"],
        "nearby_refinery": state["nearby_refinery"],
        "nearby_pipeline": state["nearby_pipeline"],
        "nearby_hospital": state["nearby_hospital"],
        "nearby_school": state["nearby_school"]
    })

    reasons = []

    if state["fire_type"] == "Industrial Fire":
        reasons.append(
            "Industrial fires have a higher probability of affecting hazardous infrastructure."
        )

    if state["damage_score"] >= 75:
        reasons.append(
            f"Damage score ({state['damage_score']}) indicates severe fire intensity."
        )

    if state["estimated_burn_area_km2"] > 3:
        reasons.append(
            f"Estimated burn area ({state['estimated_burn_area_km2']} km²) increases surrounding exposure."
        )

    if state["wind_speed"] > 15:
        reasons.append(
            f"Wind speed ({state['wind_speed']} km/h) increases risk of rapid spread."
        )

    if state["nearby_refinery"] < 1000:
        reasons.append(
            f"Nearby refinery detected within {state['nearby_refinery']} meters."
        )

    if state["nearby_pipeline"] < 1000:
        reasons.append(
            f"Pipeline infrastructure detected within {state['nearby_pipeline']} meters."
        )

    reasons.append(
        f"Land cover is classified as {state['land_cover']}."
    )

    risk_reason = " ".join(reasons)

    return {
        "risk_score": risk["risk_score"],
        "risk_level": risk["risk_level"],
        "critical_radius_km": risk["critical_radius_km"],
        "high_radius_km": risk["high_radius_km"],
        "infrastructure_risk": risk["infrastructure_risk"],
        "risk_reason": risk_reason,

        "messages": [
            AIMessage(
                content=(
                    f"Risk assessed as {risk['risk_level']} "
                    f"(Score: {risk['risk_score']})."
                )
            )
        ]
    }