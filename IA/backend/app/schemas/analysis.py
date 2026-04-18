from typing import List, Optional
from pydantic import BaseModel, Field

class PriceItem(BaseModel):
    name: str = Field(..., example="iPhone 15 Pro")
    price: float = Field(..., example=999.0)
    currency: str = Field(default="USD", example="USD")
    store: Optional[str] = Field(None, example="Amazon")

class AnalysisRequest(BaseModel):
    query: str = Field(..., example="Compare prices for high-end smartphones")
    items: List[PriceItem]

class AnalysisResponse(BaseModel):
    summary: str
    recommendation: str
    best_value_item: Optional[str]
    savings_potential: Optional[str]
    confidence_score: float
