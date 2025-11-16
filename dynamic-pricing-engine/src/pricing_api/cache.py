"""
Client Redis para cache de decisões de preço.
Otimiza latência crítica e fornece fallback.
"""
import json
import redis
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class RedisCache:
    """Cache distribuído com Redis para preços recomendados"""

    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0, ttl: int = 3600):
        """
        Inicializa conexão com Redis.
        
        Args:
            host: Host do Redis
            port: Porta do Redis
            db: Número do banco de dados
            ttl: Time-to-live em segundos
        """
        try:
            self.redis_client = redis.Redis(
                host=host,
                port=port,
                db=db,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_keepalive=True,
                health_check_interval=30
            )
            # Testa conexão
            self.redis_client.ping()
            logger.info(f"Conectado ao Redis em {host}:{port}")
        except Exception as e:
            logger.error(f"Erro ao conectar ao Redis: {e}")
            self.redis_client = None
        
        self.ttl = ttl

    def get_price(self, sku: str) -> Optional[Dict[str, Any]]:
        """
        Recupera preço recomendado do cache.
        Retorna None se não encontrado ou Redis indisponível.
        """
        if not self.redis_client:
            return None
        
        try:
            key = f"price:{sku}"
            data = self.redis_client.get(key)
            
            if data:
                return json.loads(data)
            
            return None
        except Exception as e:
            logger.warning(f"Erro ao buscar do cache: {e}")
            return None

    def set_price(self, sku: str, price_data: Dict[str, Any]) -> bool:
        """
        Armazena decisão de preço no cache.
        
        Args:
            sku: SKU do produto
            price_data: Dados da decisão de preço
        
        Returns:
            True se sucesso, False caso contrário
        """
        if not self.redis_client:
            return False
        
        try:
            key = f"price:{sku}"
            price_data['cached_at'] = datetime.utcnow().isoformat()
            
            self.redis_client.setex(
                key,
                self.ttl,
                json.dumps(price_data)
            )
            
            logger.debug(f"Preço armazenado em cache: {sku}")
            return True
        except Exception as e:
            logger.warning(f"Erro ao armazenar no cache: {e}")
            return False

    def delete_price(self, sku: str) -> bool:
        """Remove preço do cache"""
        if not self.redis_client:
            return False
        
        try:
            key = f"price:{sku}"
            self.redis_client.delete(key)
            return True
        except Exception as e:
            logger.warning(f"Erro ao deletar do cache: {e}")
            return False

    def get_all_prices(self, pattern: str = "price:*") -> Dict[str, Dict]:
        """
        Recupera múltiplos preços do cache.
        Útil para analytics e relatórios.
        """
        if not self.redis_client:
            return {}
        
        try:
            keys = self.redis_client.keys(pattern)
            result = {}
            
            for key in keys:
                sku = key.split(":")[-1]
                data = self.redis_client.get(key)
                if data:
                    result[sku] = json.loads(data)
            
            return result
        except Exception as e:
            logger.warning(f"Erro ao recuperar preços: {e}")
            return {}

    def is_healthy(self) -> bool:
        """Verifica saúde da conexão Redis"""
        if not self.redis_client:
            return False
        
        try:
            return self.redis_client.ping()
        except:
            return False

    def close(self):
        """Fecha conexão com Redis"""
        if self.redis_client:
            self.redis_client.close()
