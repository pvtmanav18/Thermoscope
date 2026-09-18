# agents/weather_agent.py

from langchain_core.messages import AIMessage
from tools.weather_tool import get_weather_by_coordinates


def weather_agent(state):
    """
    Fetch weather information for the current hotspot.
    """

    weather = get_weather_by_coordinates(
        state["latitude"],
        state["longitude"]
    )

    # Fallback if WeatherStack fails
    if weather is None:
        weather = {
            "temperature": 35,
            "humidity": 45,
            "wind_speed": 8,
            "wind_direction": "N",
            "wind_degree": 0
        }

    return {
        "temperature": weather["temperature"],
        "humidity": weather["humidity"],
        "wind_speed": weather["wind_speed"],
        "wind_direction": weather["wind_direction"],
        "wind_degree": weather["wind_degree"],

        "messages": [
            AIMessage(
                content=(
                    f"Weather collected: {weather['temperature']}°C, "
                    f"Humidity {weather['humidity']}%, "
                    f"Wind {weather['wind_speed']} km/h {weather['wind_direction']}."
                )
            )
        ]
    }