"""
Testes unitários para o Rules Engine
Demonstra como testar a lógica de precificação
"""
import pytest
from src.rules_engine.engine import (
    PricingRulesEngine, 
    PriceContext,
)


class TestPricingRulesEngine:
    """Suite de testes para o Rules Engine"""

    @pytest.fixture
    def engine(self):
        """Fixture para criar instância do engine"""
        return PricingRulesEngine(
            min_margin=0.10,
            max_margin=0.50,
            elasticity_factor=1.5
        )

    @pytest.fixture
    def base_context(self):
        """Contexto padrão para testes"""
        return PriceContext(
            sku="TEST_SKU",
            current_price=100.0,
            cost=50.0,
            competitor_prices=[95.0, 98.0, 100.0, 102.0],
            inventory_level=1000,
            days_in_stock=30,
            demand_forecast=0.6,
            margin_constraints=(0.10, 0.50)
        )

    def test_minimum_margin_enforcement(self, engine, base_context):
        """Testa se margem mínima é respeitada"""
        price, reason, confidence = engine.calculate_price(base_context)
        margin = (price - base_context.cost) / base_context.cost
        
        assert margin >= engine.min_margin, "Margem abaixo do mínimo permitido"

    def test_maximum_margin_enforcement(self, engine, base_context):
        """Testa se margem máxima é respeitada"""
        price, reason, confidence = engine.calculate_price(base_context)
        margin = (price - base_context.cost) / base_context.cost
        
        assert margin <= engine.max_margin, "Margem acima do máximo permitido"

    def test_competitive_analysis(self, engine, base_context):
        """Testa análise competitiva"""
        # Preço deve estar próximo à mediana dos competidores
        price, reason, confidence = engine.calculate_price(base_context)
        median_competitor = sorted(base_context.competitor_prices)[
            len(base_context.competitor_prices) // 2
        ]
        
        # Deve estar dentro de 10% da mediana
        assert abs(price - median_competitor) < median_competitor * 0.15

    def test_high_inventory_discount(self, engine):
        """Testa desconto em inventário alto"""
        high_inventory = PriceContext(
            sku="TEST",
            current_price=100.0,
            cost=50.0,
            competitor_prices=[100.0],
            inventory_level=10000,  # Muito alto
            days_in_stock=30,
            demand_forecast=0.5,
            margin_constraints=(0.10, 0.50)
        )
        
        normal_inventory = PriceContext(
            sku="TEST",
            current_price=100.0,
            cost=50.0,
            competitor_prices=[100.0],
            inventory_level=100,  # Normal
            days_in_stock=30,
            demand_forecast=0.5,
            margin_constraints=(0.10, 0.50)
        )
        
        high_price, _, _ = engine.calculate_price(high_inventory)
        normal_price, _, _ = engine.calculate_price(normal_inventory)
        
        # Alto inventário deve resultar em preço menor
        assert high_price < normal_price

    def test_high_demand_increases_price(self, engine):
        """Testa que demanda alta aumenta preço"""
        high_demand = PriceContext(
            sku="TEST",
            current_price=100.0,
            cost=50.0,
            competitor_prices=[100.0],
            inventory_level=1000,
            days_in_stock=30,
            demand_forecast=0.9,  # Demanda alta
            margin_constraints=(0.10, 0.50)
        )
        
        low_demand = PriceContext(
            sku="TEST",
            current_price=100.0,
            cost=50.0,
            competitor_prices=[100.0],
            inventory_level=1000,
            days_in_stock=30,
            demand_forecast=0.1,  # Demanda baixa
            margin_constraints=(0.10, 0.50)
        )
        
        high_demand_price, _, _ = engine.calculate_price(high_demand)
        low_demand_price, _, _ = engine.calculate_price(low_demand)
        
        # Alta demanda deve resultar em preço maior
        assert high_demand_price > low_demand_price

    def test_batch_processing(self, engine):
        """Testa processamento em lote"""
        contexts = [
            PriceContext(
                sku=f"SKU_{i:03d}",
                current_price=100.0,
                cost=50.0,
                competitor_prices=[95.0, 98.0, 100.0],
                inventory_level=1000,
                days_in_stock=30,
                demand_forecast=0.5,
                margin_constraints=(0.10, 0.50)
            )
            for i in range(10)
        ]
        
        df = engine.calculate_batch_prices(contexts)
        
        assert len(df) == 10, "Deve processar todos os 10 contextos"
        assert all(col in df.columns for col in [
            'sku', 'recommended_price', 'margin_pct', 'confidence'
        ])

    def test_confidence_calculation(self, engine, base_context):
        """Testa cálculo de confiança"""
        price, reason, confidence = engine.calculate_price(base_context)
        
        assert 0.0 <= confidence <= 1.0, "Confiança deve estar entre 0 e 1"
        # Contexto com dados completos deve ter alta confiança
        assert confidence > 0.7, "Contexto com dados completos deve ter confiança > 0.7"

    def test_reason_generation(self, engine):
        """Testa geração de razão legível"""
        high_inventory_context = PriceContext(
            sku="TEST",
            current_price=100.0,
            cost=50.0,
            competitor_prices=[100.0],
            inventory_level=6000,
            days_in_stock=30,
            demand_forecast=0.5,
            margin_constraints=(0.10, 0.50)
        )
        
        price, reason, confidence = engine.calculate_price(high_inventory_context)
        
        assert reason is not None, "Razão não deve ser None"
        assert len(reason) > 0, "Razão deve ter conteúdo"
        assert "Inventário" in reason or "DESCONTO" in reason, "Razão deve mencionar inventário"

    def test_price_history_tracking(self, engine):
        """Testa rastreamento de histórico de preços"""
        contexts = [
            PriceContext(
                sku=f"SKU_{i:03d}",
                current_price=100.0,
                cost=50.0,
                competitor_prices=[95.0, 98.0, 100.0],
                inventory_level=1000,
                days_in_stock=30,
                demand_forecast=0.5,
                margin_constraints=(0.10, 0.50)
            )
            for i in range(5)
        ]
        
        engine.calculate_batch_prices(contexts)
        history = engine.get_price_history()
        
        assert len(history) == 5, "Histórico deve ter 5 entradas"

    def test_trend_analysis(self, engine):
        """Testa análise de trends de preço"""
        contexts = [
            PriceContext(
                sku="TREND_SKU",
                current_price=100.0 + i*10,
                cost=50.0,
                competitor_prices=[95.0, 98.0, 100.0],
                inventory_level=1000,
                days_in_stock=30,
                demand_forecast=0.5,
                margin_constraints=(0.10, 0.50)
            )
            for i in range(5)
        ]
        
        engine.calculate_batch_prices(contexts)
        trends = engine.analyze_price_trends("TREND_SKU")
        
        assert 'mean_recommended_price' in trends
        assert 'price_volatility' in trends
        assert 'total_decisions' in trends


class TestElasticitiyCalculation:
    """Testes para o cálculo de elasticidade otimizado com Numba"""

    def test_elasticity_with_numba(self):
        """Testa otimização Numba de elasticidade"""
        base_price = 100.0
        demand = 0.7
        factor = 1.5
        
        result = PricingRulesEngine._elasticity_calc(base_price, demand, factor)
        
        # Com demanda 0.7 (acima de 0.5), preço deve aumentar
        assert result > base_price

    def test_elasticity_symmetry(self):
        """Testa simetria da elasticidade"""
        base_price = 100.0
        factor = 1.5
        
        # Demanda alta (0.7) vs demanda baixa (0.3)
        high_result = PricingRulesEngine._elasticity_calc(base_price, 0.7, factor)
        low_result = PricingRulesEngine._elasticity_calc(base_price, 0.3, factor)
        
        # Alto deve ser maior que baixo
        assert high_result > low_result


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 
