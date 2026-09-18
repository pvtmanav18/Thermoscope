# backend/tools/groq_classifier_tool.py

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage

llm = ChatGroq(
    model="openai/gpt-oss-120b",
    api_key="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",
    temperature=0.2
)

def classify_with_groq(fire_data, surroundings):

    prompt = f"""
You are an NTRO wildfire intelligence classifier.

Fire Information

Brightness TI4 : {fire_data['bright_ti4']}
Brightness TI5 : {fire_data['bright_ti5']}
FRP : {fire_data['frp']}
Confidence : {fire_data['confidence']}

Weather

Temperature : {fire_data['temperature']}
Humidity : {fire_data['humidity']}
Wind Speed : {fire_data['wind_speed']}

Surroundings within 1 km

{surroundings}

Choose ONLY ONE category:

1. Forest Fire
2. Industrial Fire
3. Commercial Fire
4. Agricultural Fire
5. Energy/Mining Fire

Return JSON only:

{{
 "fire_type":"",
 "reason":""
}}
"""

    response = llm.invoke([HumanMessage(content=prompt)])

    return response.content