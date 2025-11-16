"""
Modelos ORM SQLAlchemy para auditoria de preços.
Garante persistência e rastreabilidade de todas as decisões.
"""
from sqlalchemy import (
    Column, String, Float, DateTime, Integer, JSON,
    create_engine, Index, func
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

Base = declarative_base()


class PricingDecisionAudit(Base):
    """
    Registro de auditoria para decisões de preço.
    Garante compliance e rastreabilidade.
    """
    __tablename__ = "pricing_decisions"

    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String(50), index=True, nullable=False)
    current_price = Column(Float, nullable=False)
    recommended_price = Column(Float, nullable=False)
    margin_pct = Column(Float, nullable=False)
    confidence = Column(Float, nullable=False)
    reason = Column(String(500), nullable=True)
    competitor_prices = Column(JSON, nullable=True)
    
    # Rastreabilidade
    created_at = Column(DateTime, index=True, server_default=func.now(), nullable=False)
    applied = Column(Integer, default=0)  # 1 se preço foi aplicado
    applied_at = Column(DateTime, nullable=True)
    
    __table_args__ = (
        Index('idx_sku_created', 'sku', 'created_at'),
        Index('idx_created_at', 'created_at'),
    )

    def __repr__(self):
        return f"<PricingDecisionAudit(sku={self.sku}, recommended_price={self.recommended_price})>"


class PricingFailureLog(Base):
    """
    Log de falhas no processamento de preços.
    Rastreia erros e DLQ.
    """
    __tablename__ = "pricing_failures"

    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String(50), nullable=True)
    error_message = Column(String(1000), nullable=False)
    original_message = Column(JSON, nullable=True)
    processing_service = Column(String(100), nullable=False)
    
    created_at = Column(DateTime, index=True, server_default=func.now(), nullable=False)

    __table_args__ = (
        Index('idx_service_created', 'processing_service', 'created_at'),
    )

    def __repr__(self):
        return f"<PricingFailureLog(service={self.processing_service}, error={self.error_message[:50]})>"


class DatabaseManager:
    """Manager para operações com banco de dados"""

    def __init__(self, database_url: str):
        """
        Inicializa conexão com banco de dados.
        
        Args:
            database_url: Connection string (postgresql://user:password@host/db)
        """
        self.engine = create_engine(
            database_url,
            pool_size=20,
            max_overflow=40,
            pool_pre_ping=True,
            echo=False
        )
        
        # Cria tabelas
        Base.metadata.create_all(self.engine)
        
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )
        
        logger.info(f"Banco de dados inicializado: {database_url}")

    def get_session(self) -> Session:
        """Obtém sessão do banco de dados"""
        return self.SessionLocal()

    def record_pricing_decision(
        self,
        sku: str,
        current_price: float,
        recommended_price: float,
        margin_pct: float,
        confidence: float,
        reason: str,
        competitor_prices: list
    ) -> PricingDecisionAudit:
        """Registra uma decisão de preço"""
        session = self.get_session()
        try:
            decision = PricingDecisionAudit(
                sku=sku,
                current_price=current_price,
                recommended_price=recommended_price,
                margin_pct=margin_pct,
                confidence=confidence,
                reason=reason,
                competitor_prices=competitor_prices
            )
            
            session.add(decision)
            session.commit()
            
            logger.info(f"Decisão de preço registrada para {sku} (ID: {decision.id})")
            return decision
        
        except Exception as e:
            session.rollback()
            logger.error(f"Erro ao registrar decisão: {str(e)}")
            raise
        finally:
            session.close()

    def record_failure(
        self,
        error_message: str,
        processing_service: str,
        sku: str = None,
        original_message: dict = None
    ) -> PricingFailureLog:
        """Registra uma falha no processamento"""
        session = self.get_session()
        try:
            failure = PricingFailureLog(
                sku=sku,
                error_message=error_message,
                original_message=original_message,
                processing_service=processing_service
            )
            
            session.add(failure)
            session.commit()
            
            logger.warning(f"Falha registrada: {processing_service} - {error_message[:50]}")
            return failure
        
        except Exception as e:
            session.rollback()
            logger.error(f"Erro ao registrar falha: {str(e)}")
            raise
        finally:
            session.close()

    def get_decisions_by_sku(self, sku: str, limit: int = 100) -> list:
        """Recupera histórico de decisões para um SKU"""
        session = self.get_session()
        try:
            decisions = session.query(PricingDecisionAudit)\
                .filter(PricingDecisionAudit.sku == sku)\
                .order_by(PricingDecisionAudit.created_at.desc())\
                .limit(limit)\
                .all()
            
            return decisions
        finally:
            session.close()

    def get_recent_failures(self, hours: int = 24, limit: int = 100) -> list:
        """Recupera falhas recentes"""
        from datetime import timedelta
        
        session = self.get_session()
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            
            failures = session.query(PricingFailureLog)\
                .filter(PricingFailureLog.created_at >= cutoff_time)\
                .order_by(PricingFailureLog.created_at.desc())\
                .limit(limit)\
                .all()
            
            return failures
        finally:
            session.close()

    def get_statistics(self) -> dict:
        """Retorna estatísticas de auditoria"""
        session = self.get_session()
        try:
            total_decisions = session.query(func.count(PricingDecisionAudit.id)).scalar()
            total_failures = session.query(func.count(PricingFailureLog.id)).scalar()
            avg_confidence = session.query(
                func.avg(PricingDecisionAudit.confidence)
            ).scalar()
            avg_margin = session.query(
                func.avg(PricingDecisionAudit.margin_pct)
            ).scalar()
            
            return {
                'total_decisions': total_decisions or 0,
                'total_failures': total_failures or 0,
                'avg_confidence': float(avg_confidence or 0),
                'avg_margin': float(avg_margin or 0)
            }
        finally:
            session.close()

    def close(self):
        """Fecha conexão com banco de dados"""
        self.engine.dispose()
        logger.info("Conexão com banco de dados fechada")
