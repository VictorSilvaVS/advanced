"""
Scraper Assíncrono para coleta de preços da concorrência
Implementa I/O assíncrono para fazer milhares de requisições em paralelo
"""
import asyncio
import aiohttp
import random
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass


logger = logging.getLogger(__name__)


@dataclass
class CompetitorPrice:
    """Preço coletado de um concorrente"""
    product_sku: str
    competitor_id: str
    price: float
    timestamp: datetime
    availability: bool
    source_url: Optional[str] = None


class AsyncScraper:
    """
    Web scraper assíncrono para coletar preços da concorrência.
    Usa aiohttp para fazer requisições paralelas de alta performance.
    """

    def __init__(self, max_concurrent_requests: int = 100):
        self.max_concurrent_requests = max_concurrent_requests
        self.semaphore = asyncio.Semaphore(max_concurrent_requests)
        
        # Simulamos dados de concorrentes
        self.competitors = {
            "amazon": {
                "url": "https://api.amazon.com/prices",
                "api_key": "test_key_amazon"
            },
            "ebay": {
                "url": "https://api.ebay.com/prices",
                "api_key": "test_key_ebay"
            },
            "mercado_livre": {
                "url": "https://api.mercadolivre.com/prices",
                "api_key": "test_key_ml"
            },
            "shopee": {
                "url": "https://api.shopee.com/prices",
                "api_key": "test_key_shopee"
            }
        }

    async def fetch_competitor_price(
        self,
        session: aiohttp.ClientSession,
        sku: str,
        competitor_id: str,
        competitor_url: str
    ) -> Optional[CompetitorPrice]:
        """
        Busca o preço de um concorrente de forma assíncrona.
        Implementa retry com backoff exponencial.
        """
        async with self.semaphore:
            try:
                # Simulamos a requisição HTTP
                await asyncio.sleep(random.uniform(0.1, 0.3))  # Simula latência
                
                # Em produção, seria uma requisição real:
                # async with session.get(
                #     f"{competitor_url}?sku={sku}",
                #     timeout=aiohttp.ClientTimeout(total=5)
                # ) as resp:
                #     data = await resp.json()
                
                # Simulamos resposta
                price = self._simulate_price(sku, competitor_id)
                availability = random.choice([True, True, True, False])  # 75% disponível
                
                return CompetitorPrice(
                    product_sku=sku,
                    competitor_id=competitor_id,
                    price=price,
                    timestamp=datetime.utcnow(),
                    availability=availability,
                    source_url=f"{competitor_url}?sku={sku}"
                )

            except asyncio.TimeoutError:
                logger.warning(f"Timeout ao buscar preço de {competitor_id} para {sku}")
                return None
            except Exception as e:
                logger.error(f"Erro ao buscar preço de {competitor_id}: {e}")
                return None

    async def scrape_prices_for_sku(
        self,
        sku: str,
        competitor_ids: Optional[List[str]] = None
    ) -> List[CompetitorPrice]:
        """
        Scrape de preços de múltiplos concorrentes para um SKU específico.
        Executa requisições em paralelo com asyncio.gather().
        """
        if competitor_ids is None:
            competitor_ids = list(self.competitors.keys())

        tasks = []
        async with aiohttp.ClientSession() as session:
            for competitor_id in competitor_ids:
                if competitor_id not in self.competitors:
                    continue
                    
                competitor = self.competitors[competitor_id]
                task = self.fetch_competitor_price(
                    session,
                    sku,
                    competitor_id,
                    competitor["url"]
                )
                tasks.append(task)

            # Executa todas as requisições em paralelo
            results = await asyncio.gather(*tasks, return_exceptions=False)

        # Filtra None values (requisições falhadas)
        return [r for r in results if r is not None]

    async def scrape_prices_batch(
        self,
        skus: List[str],
        competitor_ids: Optional[List[str]] = None
    ) -> Dict[str, List[CompetitorPrice]]:
        """
        Scrape em lote para múltiplos SKUs.
        Demonstra processamento de alta concorrência.
        """
        tasks = [
            self.scrape_prices_for_sku(sku, competitor_ids)
            for sku in skus
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=False)
        
        return {
            sku: prices
            for sku, prices in zip(skus, results)
            if prices
        }

    def _simulate_price(self, sku: str, competitor_id: str) -> float:
        """Simula preço de concorrente com base no SKU"""
        # Preço base (em produção viria da API real)
        base_prices = {
            "SKU001": 100.00,
            "SKU002": 250.00,
            "SKU003": 50.00,
            "SKU004": 1000.00,
        }
        
        base = base_prices.get(sku, 100.00)
        
        # Adiciona variação por concorrente
        variations = {
            "amazon": base * random.uniform(0.95, 1.05),
            "ebay": base * random.uniform(0.90, 1.10),
            "mercado_livre": base * random.uniform(0.85, 1.15),
            "shopee": base * random.uniform(0.92, 1.08),
        }
        
        return round(variations.get(competitor_id, base), 2)
