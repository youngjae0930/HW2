from pydantic import BaseModel
from typing import List, Optional

class ElectricalInfo(BaseModel):
    korean_name: str
    description_template: str
    voltage_range: str
    typical_power: Optional[str] = None
    frequency: str = "50/60 Hz"
    is_variable: bool = False

class DetectionResult(BaseModel):
    object_name: str
    description: str
    electrical_info: Optional[ElectricalInfo] = None

class PredictionResponse(BaseModel):
    results: List[DetectionResult]
    ai_model_info: str
