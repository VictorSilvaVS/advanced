"""
API FastAPI do Scraper Service
Endpoints para coleta e consulta de preços de concorrência
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
import asyncio
import logging
import sys
import os

# Adiciona caminho ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from config.settings import settings
from src.common import setup_json_logger, KafkaMessage
from .scraper import AsyncScraper, CompetitorPrice


logger = setup_json_logger("scraper_service")

app = FastAPI(
    title="Scraper Service",
    description="Coleta de preços de concorrência em tempo real",
    version="1.0.0"
)

scraper = AsyncScraper(max_concurrent_requests=100)


# Modelos Pydantic
class ScrapePriceRequest(BaseModel):
    sku: str
    competitor_ids: Optional[List[str]] = None


class ScrapePricesRequest(BaseModel):
    skus: List[str]
    competitor_ids: Optional[List[str]] = None


class CompetitorPriceResponse(BaseModel):
    product_sku: str
    competitor_id: str
    price: float
    availability: bool
    source_url: Optional[str] = None


class PriceScrapeResponse(BaseModel):
    sku: str
    prices: List[CompetitorPriceResponse]
    scrape_count: int


@app.get("/health")
async def health():
    """Health check do serviço"""
    return {"status": "ok", "service": "scraper"}


@app.post("/api/v1/scrape/single")
async def scrape_single_price(request: ScrapePriceRequest) -> PriceScrapeResponse:
    """
    Scrape de preço para um SKU individual.
    Retorna preços de todos os concorrentes de forma assíncrona.
    """
    try:
        logger.info(f"Iniciando scrape para SKU: {request.sku}")
        
        prices = await scraper.scrape_prices_for_sku(
            request.sku,
            request.competitor_ids
        )
        
        if not prices:
            raise HTTPException(
                status_code=404,
                detail=f"Nenhum preço encontrado para SKU {request.sku}"
            )
        
        response_prices = [
            CompetitorPriceResponse(
                product_sku=p.product_sku,
                competitor_id=p.competitor_id,
                price=p.price,
                availability=p.availability,
                source_url=p.source_url
            )
            for p in prices
        ]
        
        logger.info(f"Scrape concluído para {request.sku}: {len(prices)} preços coletados")
        
        return PriceScrapeResponse(
            sku=request.sku,
            prices=response_prices,
            scrape_count=len(prices)
        )
        
    except Exception as e:
        logger.error(f"Erro no scrape: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/scrape/batch")
async def scrape_batch_prices(request: ScrapePricesRequest) -> Dict[str, PriceScrapeResponse]:
    """
    Scrape em lote para múltiplos SKUs.
    Demonstra paralelismo de alta concorrência.
    """
    try:
        logger.info(f"Iniciando scrape em lote para {len(request.skus)} SKUs")
        
        batch_results = await scraper.scrape_prices_batch(
            request.skus,
            request.competitor_ids
        )
        
        response = {
            sku: PriceScrapeResponse(
                sku=sku,
                prices=[
                    CompetitorPriceResponse(
                        product_sku=p.product_sku,
                        competitor_id=p.competitor_id,
                        price=p.price,
                        availability=p.availability,
                        source_url=p.source_url
                    )
                    for p in prices
                ],
                scrape_count=len(prices)
            )
            for sku, prices in batch_results.items()
        }
        
        logger.info(f"Scrape em lote concluído: {len(response)} SKUs processados")
        return response
        
    except Exception as e:
        logger.error(f"Erro no scrape em lote: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/competitors")
async def list_competitors():
    """Lista concorrentes monitorados"""
    return {
        "competitors": list(scraper.competitors.keys()),
        "total": len(scraper.competitors)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.SCRAPER_HOST,
        port=settings.SCRAPER_PORT,
        log_level="info"
    )
