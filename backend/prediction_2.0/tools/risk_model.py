# tools/risk_model.py

def predict_risk(data):
    """
    Estimate fire risk using damage score, fire type,
    burn area, wind speed and nearby infrastructure.
    """

    fire_type = data["fire_type"]
    intensity = data["fire_intensity"]
    damage_score = float(data["damage_score"])
    burn_area = float(data["burn_area"])
    land_cover = data["land_cover"]
    wind_speed = float(data["wind_speed"])

    refinery = float(data["nearby_refinery"])
    pipeline = float(data["nearby_pipeline"])
    hospital = float(data["nearby_hospital"])
    school = float(data["nearby_school"])

    risk_score = damage_score * 0.55

    # Fire Type
    FIRE_WEIGHT = {
        "Industrial Fire": 18,
        "Forest Fire": 12,
        "Gas Flare": 15,
        "Agricultural Fire": 5,
        "Mining Fire": 10
    }

    risk_score += FIRE_WEIGHT.get(fire_type, 8)

    # Fire Intensity
    INTENSITY_WEIGHT = {
        "Low": 2,
        "Medium": 5,
        "High": 10,
        "Extreme": 15
    }

    risk_score += INTENSITY_WEIGHT.get(intensity, 5)

    # Burn Area
    if burn_area > 4:
        risk_score += 12
    elif burn_area > 2:
        risk_score += 8
    elif burn_area > 1:
        risk_score += 4

    # Wind
    if wind_speed > 20:
        risk_score += 8
    elif wind_speed > 15:
        risk_score += 5

    # Industrial surroundings
    infra_risk = "Low"

    if refinery < 500:
        risk_score += 10
        infra_risk = "Critical"

    elif refinery < 1000:
        risk_score += 7
        infra_risk = "High"

    if pipeline < 500:
        risk_score += 8
        infra_risk = "Critical"

    elif pipeline < 1000:
        risk_score += 5
        infra_risk = "High"

    if hospital < 1000:
        risk_score += 3

    if school < 1000:
        risk_score += 3

    # Land Cover
    LAND_WEIGHT = {
        "Industrial": 10,
        "Urban": 8,
        "Forest": 6,
        "Agricultural": 3,
        "Rural": 2
    }

    risk_score += LAND_WEIGHT.get(land_cover, 4)

    risk_score = min(round(risk_score, 1), 100)

    # Risk Level
    if risk_score >= 80:
        level = "Critical"
        critical_radius = 5
        high_radius = 8

    elif risk_score >= 60:
        level = "High"
        critical_radius = 3
        high_radius = 5

    elif risk_score >= 35:
        level = "Medium"
        critical_radius = 2
        high_radius = 3

    else:
        level = "Low"
        critical_radius = 1
        high_radius = 2

    return {
        "risk_score": risk_score,
        "risk_level": level,
        "critical_radius_km": critical_radius,
        "high_radius_km": high_radius,
        "infrastructure_risk": infra_risk
    }