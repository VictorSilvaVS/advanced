"""
API FastAPI do Serviço de Decisão de Preço
Endpoint de baixa latência para consultas de preço recomendado
"""
import logging
import sys
import os
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
import asyncio

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from config.settings import settings
from src.common import setup_json_logger
from .cache import RedisCache
from .service import PricingService


logger = setup_json_logger("pricing_api")

app = FastAPI(
    title="Pricing Decision API",
    description="API de baixa latência para decisões de preço",
    version="1.0.0"
)

# Inicializa serviços
redis_cache = RedisCache(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    ttl=settings.REDIS_TTL
)

pricing_service = PricingService(cache=redis_cache)


# Modelos Pydantic
class PriceRecommendationResponse(BaseModel):
    sku: str
    current_price: float
    recommended_price: float
    margin_pct: float
    confidence: float
    reason: str
    source: str
    retrieved_at: str


class BatchPriceRequest(BaseModel):
    skus: list[str]


@app.on_event("startup")
async def startup():
    """Inicialização da aplicação"""
    logger.info("Iniciando API de Decisão de Preço")
    logger.info(f"Redis: {settings.REDIS_HOST}:{settings.REDIS_PORT}")


@app.on_event("shutdown")
async def shutdown():
    """Encerramento da aplicação"""
    redis_cache.close()
    logger.info("API de Decisão de Preço encerrada")


@app.get("/health")
async def health():
    """Health check com status do cache"""
    return {
        "status": "ok",
        "service": "pricing_api",
        "cache_healthy": redis_cache.is_healthy(),
        "redis_url": f"{settings.REDIS_HOST}:{settings.REDIS_PORT}"
    }


@app.get("/api/v1/price/{sku}", response_model=PriceRecommendationResponse)
async def get_recommended_price(
    sku: str,
    include_metrics: Optional[bool] = Query(False, description="Incluir métricas de serviço")
) -> Dict[str, Any]:
    """
    Obtém preço recomendado para um SKU.
    
    Latência alvo: < 10ms (com cache)
    
    Args:
        sku: SKU do produto
        include_metrics: Se True, inclui métricas de cache hit/miss
    
    Returns:
        Decisão de preço com recomendação
    """
    try:
        # Operação crítica: deve ser muito rápida
        price_data = await pricing_service.get_recommended_price(sku)
        
        if not price_data:
            raise HTTPException(
                status_code=404,
                detail=f"Preço não disponível para SKU {sku}"
            )
        
        response = PriceRecommendationResponse(**price_data)
        
        # Adiciona métricas se solicitado
        if include_metrics:
            response.metrics = pricing_service.get_metrics()
        
        logger.info(f"Preço retornado para {sku}: {response.recommended_price}")
        
        return response
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao recuperar preço: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro ao processar requisição")


@app.post("/api/v1/prices/batch")
async def get_batch_prices(request: BatchPriceRequest) -> Dict[str, Any]:
    """
    Obtém preços recomendados para múltiplos SKUs.
    Executa requisições em paralelo.
    
    Args:
        request: Lista de SKUs
    
    Returns:
        Dicionário com preços por SKU
    """
    try:
        logger.info(f"Batch request para {len(request.skus)} SKUs")
        
        # Executa requisições em paralelo
        tasks = [
            pricing_service.get_recommended_price(sku)
            for sku in request.skus
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=False)
        
        response = {
            sku: result
            for sku, result in zip(request.skus, results)
            if result is not None
        }
        
        logger.info(f"Batch completo: {len(response)}/{len(request.skus)} SKUs")
        
        return {
            "prices": response,
            "total_requested": len(request.skus),
            "total_found": len(response)
        }
    
    except Exception as e:
        logger.error(f"Erro no batch de preços: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro ao processar batch")


@app.post("/api/v1/price/{sku}/update")
async def update_price_cache(sku: str, price_data: Dict[str, Any]):
    """
    Atualiza preço no cache.
    Usado pelo Pipeline de Regras para publicar decisões.
    """
    try:
        success = pricing_service.update_cache_price(sku, price_data)
        
        if success:
            logger.info(f"Cache atualizado para {sku}")
            return {"status": "updated", "sku": sku}
        else:
            logger.warning(f"Falha ao atualizar cache para {sku}")
            return {"status": "failed", "sku": sku}
    
    except Exception as e:
        logger.error(f"Erro ao atualizar cache: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro ao atualizar cache")


@app.get("/api/v1/metrics")
async def get_service_metrics():
    """Retorna métricas do serviço de preço"""
    return {
        "cache_metrics": pricing_service.get_metrics(),
        "service": "pricing_api"
    }


@app.delete("/api/v1/cache/clear")
async def clear_cache():
    """Limpa todo o cache (admin endpoint)"""
    try:
        redis_cache.redis_client.flushdb()
        logger.warning("Cache limpo")
        return {"status": "cache_cleared"}
    except Exception as e:
        logger.error(f"Erro ao limpar cache: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro ao limpar cache")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.PRICING_API_HOST,
        port=settings.PRICING_API_PORT,
        log_level="info"
    )
