# backend/tools/classifier_tool.py

def calculate_fire_intensity(brightness, frp):

    score = brightness * 0.65 + frp * 0.35

    if score >= 340:
        return "Extreme", "Very High", score

    elif score >= 300:
        return "High", "High", score

    elif score >= 250:
        return "Medium", "Moderate", score

    else:
        return "Low", "Low", score