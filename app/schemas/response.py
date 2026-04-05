from pydantic import BaseModel
from typing import List, Optional

class ElectricalInfo(BaseModel):
    korean_name: str
    description_template: str
    voltage_range: str
    typical_power: Optional[str] = None
    frequency: str = "50/60 Hz"
    is_variable: bool = False

class FurnitureInfo(BaseModel):
    korean_name: str
    description_template: str
    material: Optional[str] = "확인 중"
    care_tip: str

class DetectionResult(BaseModel):
    object_name: str
    description: str
    is_electronic: bool = False
    is_furniture: bool = False
    is_ai_generated: bool = False
    electrical_info: Optional[ElectricalInfo] = None
    furniture_info: Optional[FurnitureInfo] = None

class PredictionResponse(BaseModel):
    results: List[DetectionResult]
    ai_model_info: str
