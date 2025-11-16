"""
API FastAPI do Audit Service para consultas e relatórios.
"""
import logging
import sys
import os
from datetime import timedelta
from typing import Optional, List

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from config.settings import settings
from src.common import setup_json_logger
from .models import DatabaseManager


logger = setup_json_logger("audit_api")

app = FastAPI(
    title="Audit Service API",
    description="API de auditoria e compliance de preços",
    version="1.0.0"
)

db_manager = DatabaseManager(settings.database_url)


# Modelos Pydantic
class PricingDecisionResponse(BaseModel):
    id: int
    sku: str
    current_price: float
    recommended_price: float
    margin_pct: float
    confidence: float
    reason: str
    created_at: str


class FailureLogResponse(BaseModel):
    id: int
    sku: Optional[str]
    error_message: str
    processing_service: str
    created_at: str


@app.get("/health")
async def health():
    """Health check"""
    return {
        "status": "ok",
        "service": "audit_service",
        "database": "postgresql"
    }


@app.get("/api/v1/decisions/sku/{sku}", response_model=List[PricingDecisionResponse])
async def get_sku_decisions(
    sku: str,
    limit: int = Query(100, ge=1, le=1000)
):
    """
    Recupera histórico de decisões de preço para um SKU.
    Útil para análise e troubleshooting.
    """
    try:
        decisions = db_manager.get_decisions_by_sku(sku, limit)
        
        if not decisions:
            raise HTTPException(
                status_code=404,
                detail=f"Nenhuma decisão encontrada para {sku}"
            )
        
        return [
            PricingDecisionResponse(
                id=d.id,
                sku=d.sku,
                current_price=d.current_price,
                recommended_price=d.recommended_price,
                margin_pct=d.margin_pct,
                confidence=d.confidence,
                reason=d.reason,
                created_at=d.created_at.isoformat()
            )
            for d in decisions
        ]
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao recuperar decisões: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro ao recuperar dados")


@app.get("/api/v1/failures", response_model=List[FailureLogResponse])
async def get_recent_failures(
    hours: int = Query(24, ge=1, le=720),
    limit: int = Query(100, ge=1, le=1000)
):
    """
    Recupera falhas recentes.
    Útil para monitoramento e alertas.
    """
    try:
        failures = db_manager.get_recent_failures(hours, limit)
        
        return [
            FailureLogResponse(
                id=f.id,
                sku=f.sku,
                error_message=f.error_message,
                processing_service=f.processing_service,
                created_at=f.created_at.isoformat()
            )
            for f in failures
        ]
    
    except Exception as e:
        logger.error(f"Erro ao recuperar falhas: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro ao recuperar dados")


@app.get("/api/v1/statistics")
async def get_statistics():
    """
    Retorna estatísticas gerais de auditoria.
    KPIs para monitoramento.
    """
    try:
        stats = db_manager.get_statistics()
        
        return {
            "statistics": stats,
            "timestamp": __import__('datetime').datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Erro ao recuperar estatísticas: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro ao recuperar estatísticas")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8003,
        log_level="info"
    )
