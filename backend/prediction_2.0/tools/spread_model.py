# tools/spread_model.py

# Wind direction → fire spread direction
WIND_DESTINATION = {
    "N": "S",
    "NNE": "SSW",
    "NE": "SW",
    "ENE": "WSW",
    "E": "W",
    "ESE": "WNW",
    "SE": "NW",
    "SSE": "NNW",
    "S": "N",
    "SSW": "NNE",
    "SW": "NE",
    "WSW": "ENE",
    "W": "E",
    "WNW": "ESE",
    "NW": "SE",
    "NNW": "SSE"
}

SECONDARY_DIRECTION = {
    "N": "SE",
    "NE": "E",
    "E": "NE",
    "SE": "S",
    "S": "SW",
    "SW": "W",
    "W": "NW",
    "NW": "N"
}


def predict_spread(data):
    """
    Prototype Fire Spread Prediction Model.

    Input:
        brightness
        frp
        temperature
        humidity
        wind_speed
        wind_direction
    """

    brightness = float(data["brightness"])
    frp = float(data["frp"])
    temperature = float(data["temperature"])
    humidity = float(data["humidity"])
    wind_speed = float(data["wind_speed"])
    wind = str(data["wind_direction"]).upper().strip()

    spread_direction = WIND_DESTINATION.get(wind, "UNKNOWN")

    confidence = 45

    # Fire intensity
    if brightness > 400:
        confidence += 15
    elif brightness > 360:
        confidence += 8

    if frp > 60:
        confidence += 15
    elif frp > 30:
        confidence += 8

    # Weather contribution
    if wind_speed > 20:
        confidence += 12
    elif wind_speed > 10:
        confidence += 8

    if humidity < 30:
        confidence += 8
    elif humidity < 40:
        confidence += 4

    if temperature > 35:
        confidence += 5

    confidence = min(95, confidence)

    secondary = SECONDARY_DIRECTION.get(
        spread_direction,
        "UNKNOWN"
    )

    return {
        "predicted_spread_direction": spread_direction,
        "confidence": confidence,

        "top_predictions": [
            {
                "direction": spread_direction,
                "probability": confidence
            },
            {
                "direction": secondary,
                "probability": 100 - confidence
            }
        ]
    }