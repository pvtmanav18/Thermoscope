# agents/gis_context_agent.py

from langchain_core.messages import AIMessage


def gis_context_agent(state):
    """
    Estimate GIS context from latitude, longitude and fire type.
    Replace later with Geoapify + TomTom APIs.
    """

    lat = state["latitude"]
    lon = state["longitude"]

    # --------------------------------------
    # Dummy land-cover estimation
    # --------------------------------------

    fire_type = state["fire_type"]

    if "Industrial" in fire_type:
        land_cover = "Industrial"

    elif "Forest" in fire_type:
        land_cover = "Forest"

    elif "Agricultural" in fire_type:
        land_cover = "Agricultural"

    else:
        land_cover = "Urban"

    # --------------------------------------
    # Dummy infrastructure estimation
    # --------------------------------------

    nearby_refinery = round((lat * lon) % 800 + 200, 1)
    nearby_pipeline = round((lat + lon) % 1200 + 300, 1)
    nearby_hospital = round((lat * 10) % 3000 + 500, 1)
    nearby_school = round((lon * 10) % 2500 + 600, 1)
    nearby_buildings = int((lat + lon) % 120 + 20)

    city = "Unknown City"
    district = "Unknown District"
    state_name = "Unknown State"

    # Gujarat (Prototype)
    if 20 <= lat <= 25 and 68 <= lon <= 74:
        city = "Jamnagar"
        district = "Jamnagar"
        state_name = "Gujarat"

    return {
        "city": city,
        "district": district,
        "state_name": state_name,
        "land_cover": land_cover,

        "nearby_refinery": nearby_refinery,
        "nearby_pipeline": nearby_pipeline,
        "nearby_hospital": nearby_hospital,
        "nearby_school": nearby_school,
        "nearby_buildings": nearby_buildings,

        "messages": [
            AIMessage(
                content=f"GIS context generated for {city}, {state_name}."
            )
        ]
    }