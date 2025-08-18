# backend/schemas/schemas.py
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class DiagnoseRequest(BaseModel):
    crop: Optional[str] = None
    image_b64: str = Field(..., description="Base64-encoded image")

class DiagnoseResult(BaseModel):
    disease: str
    confidence: float
    crop: Optional[str] = None

class RemedyPrice(BaseModel):
    product: str
    price_value: float
    price_text: str
    source: str
    url: Optional[str] = None
    seller: Optional[str] = None
    location: Optional[str] = None

class PriceCompareResponse(BaseModel):
    disease: str
    remedies: List[str]
    prices: List[RemedyPrice]
    cheapest: Optional[RemedyPrice] = None

class MarketQuery(BaseModel):
    commodity: str
    state: Optional[str] = None
    district: Optional[str] = None

class MarketInsight(BaseModel):
    commodity: str
    mandi_prices: List[Dict[str, Any]]

class WeatherQuery(BaseModel):
    lat: float
    lon: float

class SchemesQuery(BaseModel):
    query: str
    state: Optional[str] = None
    category: Optional[str] = None
    top_k: int = 5

class SchemeSearchQuery(BaseModel):
    query: str

class AgentResponse(BaseModel):
    status: str
    data: Dict[str, Any] = {}
    trend: Optional[Dict[str, Any]] = None
    recommendation: Optional[str] = None

class WeatherContext(BaseModel):
    lat: float
    lon: float

class WeatherAdvice(BaseModel):
    summary: str
    details: Dict[str, Any] = {}

class SchemeQuery(BaseModel):
    query: str
    lang: Optional[str] = "en-IN"

class SchemeAnswer(BaseModel):
    answer: str
    links: List[str] = []

class OrchestratedResponse(BaseModel):
    diagnose: Optional[DiagnoseResult]
    remedy_prices: Optional[PriceCompareResponse]
    market: Optional[MarketInsight]
    weather: Optional[WeatherAdvice]
    schemes: Optional[SchemeAnswer]
