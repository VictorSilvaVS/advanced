"""
Utilitários compartilhados entre microsserviços
"""
import json
import logging
from typing import Any, Dict, Optional
from datetime import datetime
from pythonjsonlogger import jsonlogger


def setup_json_logger(name: str, level: str = "INFO") -> logging.Logger:
    """Configura logger em formato JSON para observabilidade"""
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level))
    
    handler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter(
        '%(timestamp)s %(level)s %(name)s %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger


class KafkaMessage:
    """Wrapper para mensagens Kafka com schema padrão"""
    
    def __init__(
        self,
        event_type: str,
        data: Dict[str, Any],
        timestamp: Optional[datetime] = None,
        metadata: Optional[Dict] = None
    ):
        self.event_type = event_type
        self.data = data
        self.timestamp = timestamp or datetime.utcnow()
        self.metadata = metadata or {}

    def to_json(self) -> str:
        """Serializa para JSON"""
        return json.dumps({
            "event_type": self.event_type,
            "timestamp": self.timestamp.isoformat(),
            "data": self.data,
            "metadata": self.metadata
        })

    @staticmethod
    def from_json(json_str: str) -> "KafkaMessage":
        """Desserializa do JSON"""
        data = json.loads(json_str)
        return KafkaMessage(
            event_type=data["event_type"],
            data=data["data"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            metadata=data.get("metadata", {})
        )


class PricingDecision:
    """Decisão de preço com rastreabilidade"""
    
    def __init__(
        self,
        sku: str,
        current_price: float,
        recommended_price: float,
        margin_pct: float,
        confidence: float,
        reason: str,
        competitor_prices: Optional[list] = None
    ):
        self.sku = sku
        self.current_price = current_price
        self.recommended_price = recommended_price
        self.margin_pct = margin_pct
        self.confidence = confidence
        self.reason = reason
        self.competitor_prices = competitor_prices or []
        self.created_at = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            "sku": self.sku,
            "current_price": self.current_price,
            "recommended_price": self.recommended_price,
            "margin_pct": self.margin_pct,
            "confidence": self.confidence,
            "reason": self.reason,
            "competitor_prices": self.competitor_prices,
            "created_at": self.created_at.isoformat()
        }
