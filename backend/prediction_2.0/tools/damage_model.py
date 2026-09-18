# tools/damage_model.py


INTENSITY_WEIGHT = {
    "Low": 10,
    "Medium": 20,
    "High": 30,
    "Extreme": 40
}


def predict_damage(data):
    """
    Estimate fire damage using FIRMS + Weather + Classification.
    """

    brightness = float(data["brightness"])
    frp = float(data["frp"])
    temperature = float(data["temperature"])
    humidity = float(data["humidity"])
    wind_speed = float(data["wind_speed"])
    intensity = data["fire_intensity"]
    land_cover = data["land_cover"]

    score = 0

    # Brightness contribution (30)
    score += min(brightness / 450 * 30, 30)

    # FRP contribution (25)
    score += min(frp / 100 * 25, 25)

    # Fire intensity contribution (20)
    score += min(INTENSITY_WEIGHT.get(intensity, 20), 20)

    # Wind contribution (15)
    score += min(wind_speed / 30 * 15, 15)

    # Temperature contribution (5)
    score += min(max(temperature - 20, 0) / 20 * 5, 5)

    # Humidity contribution (5)
    humidity_score = max(0, (60 - humidity) / 60 * 5)
    score += humidity_score

    score = round(min(score, 100), 1)

    # ----------------------------------
    # Burn Area Estimation
    # ----------------------------------

    burn_area = 0.2 + frp * 0.05

    if wind_speed > 15:
        burn_area *= 1.2

    if land_cover == "Industrial":
        burn_area *= 1.3

    burn_area = round(burn_area, 2)

    # ----------------------------------
    # Burnout Time Estimation
    # ----------------------------------

    burnout = 2

    burnout += frp / 20

    if wind_speed > 15:
        burnout += 2

    if humidity < 35:
        burnout += 2

    if intensity == "Extreme":
        burnout += 3

    burnout = round(burnout, 1)

    # ----------------------------------
    # Category
    # ----------------------------------

    if score < 30:
        category = "Localized Damage"

    elif score < 55:
        category = "Moderate Damage"

    elif score < 75:
        category = "Major Damage"

    else:
        category = "Severe Industrial Damage"

    return {
        "damage_score": score,
        "damage_category": category,
        "estimated_burn_area_km2": burn_area,
        "estimated_burnout_hours": burnout
    }