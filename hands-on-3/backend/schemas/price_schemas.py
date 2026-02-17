# schemas/price_schemas.py
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class PriceData(BaseModel):
    date: str = Field(..., description="วันที่ในรูปแบบ YYYY-MM-DD")
    diesel: Optional[float] = Field(None, ge=0, description="ราคาดีเซล")
    gasohol_95: Optional[float] = Field(None, ge=0, description="ราคาแก๊สโซฮอล์ 95")
    gasohol_91: Optional[float] = Field(None, ge=0, description="ราคาแก๊สโซฮอล์ 91")
    gasohol_e20: Optional[float] = Field(None, ge=0, description="ราคาแก๊สโซฮอล์ E20")
    diesel_b7: Optional[float] = Field(None, ge=0, description="ราคาดีเซล B7")
    lpg: Optional[float] = Field(None, ge=0, description="ราคา LPG")

    class Config:
        json_schema_extra = {
            "example": {
                "date": "2026-02-17",
                "diesel": 32.50,
                "gasohol_95": 42.80,
                "gasohol_91": 40.50
            }
        }

class PredictionRequest(BaseModel):
    fuel_type: str = Field(default="diesel", description="ประเภทเชื้อเพลิง")
    horizon: int = Field(default=7, ge=1, le=30, description="จำนวนวันที่ต้องการทำนาย")

class PredictionResult(BaseModel):
    day: int
    date: str
    predicted_price: float
    lower_bound: float
    upper_bound: float

class PredictionResponse(BaseModel):
    fuel_type: str
    current_price: float
    predictions: List[PredictionResult]
    model_info: Dict[str, Any]

class TrainingRequest(BaseModel):
    fuel_type: str = Field(default="diesel")
    retrain: bool = Field(default=False, description="บังคับ retrain ถึงแม้มี model อยู่แล้ว")

class UploadResponse(BaseModel):
    status: str
    records_added: int
    date_range: Dict[str, str]
