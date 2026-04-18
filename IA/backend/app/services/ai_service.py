import google.generativeai as genai
from app.core.config import settings
from app.schemas.analysis import AnalysisRequest, AnalysisResponse
import json

class AIService:
    def __init__(self):
        if settings.GEMINI_API_KEY:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.model = genai.GenerativeModel('gemini-1.5-pro')
        else:
            self.model = None

    async def analyze_prices(self, data: AnalysisRequest) -> AnalysisResponse:
        if not self.model:
            # Mock implementation if no API key is provided
            return AnalysisResponse(
                summary="API key not configured. This is a placeholder analysis.",
                recommendation="Please configure your Gemini API Key in the settings.",
                best_value_item=data.items[0].name if data.items else "None",
                savings_potential="Unknown",
                confidence_score=0.5
            )

        items_str = "\n".join([f"- {item.name}: {item.price} {item.currency} at {item.store or 'Unknown'}" for item in data.items])
        
        prompt = f"""
        Analyze the following price data for the query: "{data.query}"
        
        Data:
        {items_str}
        
        Provide a detailed analysis in JSON format with the following fields:
        - summary: A brief overview of the price landscape.
        - recommendation: Which item should I buy and why?
        - best_value_item: The name of the item with the best price/performance ratio.
        - savings_potential: Estimated savings possible if choosing the best option.
        - confidence_score: A float between 0 and 1 representing the AI's confidence in the analysis.
        
        Return ONLY the JSON.
        """

        try:
            response = self.model.generate_content(prompt)
            result = json.loads(response.text.strip('`json\n'))
            return AnalysisResponse(**result)
        except Exception as e:
            # Fallback
            return AnalysisResponse(
                summary=f"Analysis failed: {str(e)}",
                recommendation="Error processing the request.",
                best_value_item=None,
                savings_potential=None,
                confidence_score=0.0
            )

ai_service = AIService()
