from fastapi import APIRouter, Depends, HTTPException
from app.schemas.analysis import AnalysisRequest, AnalysisResponse
from app.services.ai_service import ai_service

router = APIRouter()

@router.post("/", response_model=AnalysisResponse)
async def analyze_prices(request: AnalysisRequest):
    """
    Analyzes a list of prices and provides a recommendation.
    - **query**: The user's intent (e.g., "Find the best gaming laptop")
    - **items**: A list of items with their names, prices, and stores.
    """
    if not request.items:
        raise HTTPException(status_code=400, detail="Items list cannot be empty")
    
    analysis = await ai_service.analyze_prices(request)
    return analysis
