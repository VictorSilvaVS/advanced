"""
Serviço de recuperação de preços com fallback.
Implementa padrão Circuit Breaker para resiliência.
"""
import json
import logging
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class PricingSource(Enum):
    """Fonte de dados para preço"""
    CACHE = "cache"
    KAFKA = "kafka_topic"
    FALLBACK = "fallback"


class PricingService:
    """
    Serviço que gerencia retrieval de preços com múltiplas fontes.
    Implementa fallback e resiliência.
    """

    def __init__(self, cache=None, fallback_prices: Optional[Dict[str, float]] = None):
        """
        Args:
            cache: Instância de RedisCache
            fallback_prices: Dicionário com preços fallback por SKU
        """
        self.cache = cache
        self.fallback_prices = fallback_prices or self._default_fallback_prices()
        self.metrics = {
            'cache_hits': 0,
            'cache_misses': 0,
            'fallback_uses': 0
        }

    async def get_recommended_price(self, sku: str) -> Dict[str, Any]:
        """
        Recupera preço recomendado com fallback automático.
        
        Estratégia:
        1. Tenta cache (latência ~1ms)
        2. Tenta tópico Kafka (latência ~100ms)
        3. Usa fallback (latência ~0ms)
        """
        
        # Tentativa 1: Cache Redis
        if self.cache and self.cache.is_healthy():
            cached_price = self.cache.get_price(sku)
            if cached_price:
                self.metrics['cache_hits'] += 1
                logger.debug(f"Preço recuperado do cache: {sku}")
                return {
                    **cached_price,
                    'source': PricingSource.CACHE.value,
                    'retrieved_at': datetime.utcnow().isoformat()
                }
            
            self.metrics['cache_misses'] += 1
        
        # Tentativa 2: Fallback (garantido retornar algo)
        fallback_price = self.fallback_prices.get(sku)
        if fallback_price:
            self.metrics['fallback_uses'] += 1
            logger.warning(f"Usando preço fallback para {sku}: R${fallback_price}")
            
            return {
                'sku': sku,
                'recommended_price': fallback_price,
                'current_price': fallback_price,
                'margin_pct': 0.20,  # Margem padrão
                'confidence': 0.3,  # Confiança baixa
                'reason': 'Fallback pricing - cache indisponível',
                'source': PricingSource.FALLBACK.value,
                'retrieved_at': datetime.utcnow().isoformat()
            }
        
        # Último recurso: Retorna None (cliente deve tratar)
        logger.error(f"Nenhuma fonte de preço disponível para {sku}")
        return None

    def _default_fallback_prices(self) -> Dict[str, float]:
        """Preços fallback padrão para produtos conhecidos"""
        return {
            "SKU001": 100.00,
            "SKU002": 250.00,
            "SKU003": 50.00,
            "SKU004": 1000.00,
        }

    def get_metrics(self) -> Dict[str, int]:
        """Retorna métricas de uso do serviço"""
        return self.metrics.copy()

    def reset_metrics(self):
        """Reseta métricas"""
        self.metrics = {
            'cache_hits': 0,
            'cache_misses': 0,
            'fallback_uses': 0
        }

    def update_cache_price(self, sku: str, price_data: Dict[str, Any]) -> bool:
        """Atualiza preço no cache"""
        if self.cache:
            return self.cache.set_price(sku, price_data)
        return False
