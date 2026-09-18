# ==========================================
# state.py
# LangGraph State for Fire Classification
# ==========================================

from typing import TypedDict, Dict, List, Any
from typing_extensions import Annotated
import operator


class FireState(TypedDict):
    """
    Shared state passed between LangGraph nodes.
    """

    # Raw NASA FIRMS hotspot row
    fire_data: Dict[str, Any]

    # Geoapify reverse geocoding result
    geo_context: Dict[str, Any]

    # AI classification result
    classification: Dict[str, Any]

    # Fire intensity result
    intensity: Dict[str, Any]

    # Optional conversation / debugging logs
    messages: Annotated[List[Any], operator.add]    