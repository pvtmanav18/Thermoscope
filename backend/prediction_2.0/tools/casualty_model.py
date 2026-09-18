# tools/casualty_model.py

POPULATION_DENSITY = {
    "Industrial": 350,
    "Urban": 1800,
    "Rural": 250,
    "Forest": 30,
    "Agricultural": 120
}

BUILDING_DENSITY = {
    "Industrial": 25,
    "Urban": 70,
    "Rural": 18,
    "Forest": 2,
    "Agricultural": 8
}


def predict_casualties(data):
    """
    Estimate affected buildings and population.
    """

    land_cover = data["land_cover"]
    burn_area = float(data["burn_area"])
    nearby_buildings = int(data["nearby_buildings"])
    risk_level = data["risk_level"]
    fire_type = data["fire_type"]

    pop_density = POPULATION_DENSITY.get(
        land_cover,
        400
    )

    building_density = BUILDING_DENSITY.get(
        land_cover,
        20
    )

    affected_population = int(pop_density * burn_area)

    estimated_buildings = int(building_density * burn_area)

    affected_buildings = min(
        nearby_buildings,
        estimated_buildings
    )

    # Casualty Risk
    if risk_level == "Critical":
        casualty_risk = "High"

    elif risk_level == "High":
        casualty_risk = "Medium"

    else:
        casualty_risk = "Low"

    # Evacuation Priority
    if fire_type == "Industrial Fire" and risk_level == "Critical":
        evacuation = "Immediate"

    elif risk_level == "High":
        evacuation = "High Priority"

    elif risk_level == "Medium":
        evacuation = "Prepare Evacuation"

    else:
        evacuation = "Monitor Area"

    return {
        "affected_population": affected_population,
        "affected_buildings": affected_buildings,
        "casualty_risk": casualty_risk,
        "evacuation_priority": evacuation
    }