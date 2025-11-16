"""
Worker assíncrono do Audit Service.
Consome mensagens de preços recomendados e falhas, registra em PostgreSQL.
"""
import asyncio
import json
import logging
import sys
import os
from typing import Optional
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from aiokafka import AIOKafkaConsumer
from config.settings import settings
from src.common import KafkaMessage, setup_json_logger
from .models import DatabaseManager


logger = setup_json_logger("audit_service_worker")


class AuditServiceWorker:
    """
    Worker que consome decisões de preço e falhas,
    registrando tudo em PostgreSQL para auditoria.
    """

    def __init__(self):
        self.db_manager = DatabaseManager(settings.database_url)
        self.price_consumer: Optional[AIOKafkaConsumer] = None
        self.failure_consumer: Optional[AIOKafkaConsumer] = None
        self.running = False

    async def start(self):
        """Inicia consumers do Kafka"""
        logger.info("Iniciando Audit Service Worker")
        
        # Consumer para decisões de preço
        self.price_consumer = AIOKafkaConsumer(
            settings.KAFKA_PRICES_TOPIC,
            bootstrap_servers=settings.KAFKA_BROKER,
            group_id="audit_service_prices",
            auto_offset_reset='earliest',
            value_deserializer=lambda m: m.decode('utf-8')
        )
        
        # Consumer para falhas/DLQ
        self.failure_consumer = AIOKafkaConsumer(
            settings.KAFKA_DLQ_TOPIC,
            bootstrap_servers=settings.KAFKA_BROKER,
            group_id="audit_service_failures",
            auto_offset_reset='earliest',
            value_deserializer=lambda m: m.decode('utf-8')
        )
        
        await self.price_consumer.start()
        await self.failure_consumer.start()
        
        logger.info("Audit Service Worker iniciado")
        self.running = True

    async def stop(self):
        """Para consumers"""
        self.running = False
        if self.price_consumer:
            await self.price_consumer.stop()
        if self.failure_consumer:
            await self.failure_consumer.stop()
        self.db_manager.close()
        logger.info("Audit Service Worker parado")

    async def run(self):
        """Loop principal processando mensagens em paralelo"""
        await self.start()
        
        try:
            await asyncio.gather(
                self._process_prices(),
                self._process_failures(),
                return_exceptions=True
            )
        finally:
            await self.stop()

    async def _process_prices(self):
        """Processa mensagens de decisões de preço"""
        async for message in self.price_consumer:
            try:
                await self._record_price_decision(message.value)
            except Exception as e:
                logger.error(f"Erro ao registrar decisão de preço: {str(e)}")

    async def _process_failures(self):
        """Processa mensagens de falhas/DLQ"""
        async for message in self.failure_consumer:
            try:
                await self._record_failure(message.value)
            except Exception as e:
                logger.error(f"Erro ao registrar falha: {str(e)}")

    async def _record_price_decision(self, message_value: str):
        """Registra decisão de preço em PostgreSQL"""
        try:
            kafka_msg = KafkaMessage.from_json(message_value)
            data = kafka_msg.data
            
            self.db_manager.record_pricing_decision(
                sku=data.get("sku"),
                current_price=data.get("current_price", 0.0),
                recommended_price=data.get("recommended_price", 0.0),
                margin_pct=data.get("margin_pct", 0.0),
                confidence=data.get("confidence", 0.0),
                reason=data.get("reason", ""),
                competitor_prices=data.get("competitor_prices", [])
            )
            
            logger.debug(f"Decisão registrada: {data.get('sku')}")
        
        except json.JSONDecodeError as e:
            logger.error(f"Erro ao desserializar JSON: {str(e)}")
        except Exception as e:
            logger.error(f"Erro ao registrar decisão: {str(e)}")

    async def _record_failure(self, message_value: str):
        """Registra falha em PostgreSQL"""
        try:
            data = json.loads(message_value)
            
            self.db_manager.record_failure(
                error_message=data.get("error", "Unknown error"),
                processing_service=data.get("processing_service", "unknown"),
                sku=data.get("sku"),
                original_message=data.get("original_message")
            )
            
            logger.debug(f"Falha registrada: {data.get('processing_service')}")
        
        except json.JSONDecodeError as e:
            logger.error(f"Erro ao desserializar JSON: {str(e)}")
        except Exception as e:
            logger.error(f"Erro ao registrar falha: {str(e)}")


async def main():
    """Ponto de entrada do worker"""
    worker = AuditServiceWorker()
    
    try:
        await worker.run()
    except KeyboardInterrupt:
        logger.info("Interrupção do usuário")
        await worker.stop()
    except Exception as e:
        logger.error(f"Erro fatal: {str(e)}")
        await worker.stop()
        raise


if __name__ == "__main__":
    asyncio.run(main())
