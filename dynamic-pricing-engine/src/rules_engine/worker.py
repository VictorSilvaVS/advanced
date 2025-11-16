"""
Worker assíncrono do Pipeline de Regras.
Consome mensagens do Kafka, aplica regras, publica decisões.
"""
import asyncio
import json
import logging
import sys
import os
from typing import Optional
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from config.settings import settings
from src.common import KafkaMessage, PricingDecision, setup_json_logger
from .engine import PricingRulesEngine, PriceContext


logger = setup_json_logger("rules_engine_worker")


class RulesEngineWorker:
    """
    Worker que processa mensagens de preços da concorrência
    e publica decisões de preço recomendado.
    """

    def __init__(self):
        self.engine = PricingRulesEngine(
            min_margin=settings.MINIMUM_MARGIN,
            max_margin=settings.MAXIMUM_MARGIN,
            elasticity_factor=settings.ELASTICITY_FACTOR
        )
        self.consumer: Optional[AIOKafkaConsumer] = None
        self.producer: Optional[AIOKafkaProducer] = None
        self.dlq_producer: Optional[AIOKafkaProducer] = None
        self.running = False

    async def start(self):
        """Inicia consumer e producers Kafka"""
        logger.info("Iniciando Rules Engine Worker")
        
        self.consumer = AIOKafkaConsumer(
            settings.KAFKA_SCRAPER_TOPIC,
            bootstrap_servers=settings.KAFKA_BROKER,
            group_id="rules_engine_group",
            auto_offset_reset='earliest',
            value_deserializer=lambda m: m.decode('utf-8')
        )
        
        self.producer = AIOKafkaProducer(
            bootstrap_servers=settings.KAFKA_BROKER,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        
        self.dlq_producer = AIOKafkaProducer(
            bootstrap_servers=settings.KAFKA_BROKER,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        
        await self.consumer.start()
        await self.producer.start()
        await self.dlq_producer.start()
        
        logger.info("Rules Engine Worker iniciado com sucesso")
        self.running = True

    async def stop(self):
        """Para consumer e producers"""
        self.running = False
        if self.consumer:
            await self.consumer.stop()
        if self.producer:
            await self.producer.stop()
        if self.dlq_producer:
            await self.dlq_producer.stop()
        logger.info("Rules Engine Worker parado")

    async def run(self):
        """Loop principal de processamento"""
        await self.start()
        
        try:
            async for message in self.consumer:
                try:
                    await self._process_message(message.value)
                except Exception as e:
                    logger.error(f"Erro ao processar mensagem: {str(e)}")
                    # Envia para DLQ
                    await self._send_to_dlq(message.value, str(e))
        finally:
            await self.stop()

    async def _process_message(self, message_value: str):
        """
        Processa mensagem de preços da concorrência
        e publica decisão de preço.
        """
        try:
            # Desserializa mensagem
            kafka_msg = KafkaMessage.from_json(message_value)
            
            if kafka_msg.event_type != "raw_prices":
                logger.warning(f"Evento desconhecido: {kafka_msg.event_type}")
                return
            
            # Extrai dados
            data = kafka_msg.data
            sku = data.get("sku")
            current_price = data.get("current_price", 100.0)
            cost = data.get("cost", 50.0)
            competitor_prices = data.get("competitor_prices", [])
            inventory_level = data.get("inventory_level", 100)
            days_in_stock = data.get("days_in_stock", 30)
            demand_forecast = data.get("demand_forecast", 0.5)
            
            logger.info(f"Processando decisão de preço para {sku}")
            
            # Cria contexto
            context = PriceContext(
                sku=sku,
                current_price=current_price,
                cost=cost,
                competitor_prices=competitor_prices,
                inventory_level=inventory_level,
                days_in_stock=days_in_stock,
                demand_forecast=demand_forecast,
                margin_constraints=(settings.MINIMUM_MARGIN, settings.MAXIMUM_MARGIN)
            )
            
            # Calcula preço recomendado
            recommended_price, reason, confidence = self.engine.calculate_price(context)
            
            # Calcula margem
            margin = (recommended_price - cost) / cost if cost > 0 else 0
            
            # Cria decisão
            decision = PricingDecision(
                sku=sku,
                current_price=current_price,
                recommended_price=recommended_price,
                margin_pct=margin,
                confidence=confidence,
                reason=reason,
                competitor_prices=competitor_prices
            )
            
            # Publica decisão
            await self._publish_decision(decision)
            
            logger.info(f"Decisão publicada para {sku}: R${recommended_price:.2f}")
            
        except json.JSONDecodeError as e:
            logger.error(f"Erro ao desserializar JSON: {str(e)}")
            raise
        except KeyError as e:
            logger.error(f"Dados faltantes na mensagem: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Erro inesperado: {str(e)}")
            raise

    async def _publish_decision(self, decision: PricingDecision):
        """Publica decisão de preço para tópico Kafka"""
        if not self.producer:
            logger.error("Producer não inicializado")
            return
        
        message = KafkaMessage(
            event_type="recommended_price",
            data=decision.to_dict()
        )
        
        await self.producer.send_and_wait(
            settings.KAFKA_PRICES_TOPIC,
            value=json.loads(message.to_json())
        )

    async def _send_to_dlq(self, message_value: str, error_reason: str):
        """Envia mensagem para Dead Letter Queue"""
        if not self.dlq_producer:
            logger.error("DLQ Producer não inicializado")
            return
        
        dlq_message = {
            "original_message": message_value,
            "error": error_reason,
            "timestamp": datetime.utcnow().isoformat(),
            "processing_service": "rules_engine"
        }
        
        await self.dlq_producer.send_and_wait(
            settings.KAFKA_DLQ_TOPIC,
            value=dlq_message
        )
        
        logger.info(f"Mensagem enviada para DLQ: {error_reason}")


async def main():
    """Ponto de entrada do worker"""
    worker = RulesEngineWorker()
    
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
