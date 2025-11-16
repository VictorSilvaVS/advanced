"""Pricing rules engine with complex business logic."""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from numba import jit


@dataclass
class PriceContext:
    """Contexto para decisão de preço"""
    sku: str
    current_price: float
    cost: float
    competitor_prices: List[float]
    inventory_level: int
    days_in_stock: int
    demand_forecast: float  # 0.0 a 1.0
    margin_constraints: Tuple[float, float]  # (min, max)


class PricingRulesEngine:
    """
    Engine de preços com múltiplas regras de negócio complexas.
    Implementa elasticidade de preço, análise competitiva, e otimização de margem.
    """

    def __init__(
        self,
        min_margin: float = 0.10,
        max_margin: float = 0.50,
        elasticity_factor: float = 1.5,
        competitive_discount: float = 0.02,
        base_confidence: float = 0.5,
        high_inventory_threshold: int = 1000,
        high_inventory_discount: float = 0.05,
        critical_inventory_threshold: int = 5000,
        critical_inventory_discount: float = 0.10,
        old_stock_days_threshold: int = 180,
        old_stock_discount: float = 0.08,
        critical_stock_days_threshold: int = 365,
        critical_stock_discount: float = 0.15,
        price_increase_threshold: float = 5.0,
        price_decrease_threshold: float = 5.0,
        aggressive_positioning_threshold: float = 0.05,
        premium_positioning_threshold: float = 0.05,
        confidence_boost_many_competitors: float = 0.2,
        confidence_boost_few_competitors: float = 0.1,
        confidence_boost_inventory: float = 0.15,
        confidence_boost_demand: float = 0.15,
        min_demand_confidence: float = 0.3,
        max_demand_confidence: float = 0.7,
    ):
        self.min_margin = min_margin
        self.max_margin = max_margin
        self.elasticity_factor = elasticity_factor
        self.competitive_discount = competitive_discount
        self.base_confidence = base_confidence
        self.high_inventory_threshold = high_inventory_threshold
        self.high_inventory_discount = high_inventory_discount
        self.critical_inventory_threshold = critical_inventory_threshold
        self.critical_inventory_discount = critical_inventory_discount
        self.old_stock_days_threshold = old_stock_days_threshold
        self.old_stock_discount = old_stock_discount
        self.critical_stock_days_threshold = critical_stock_days_threshold
        self.critical_stock_discount = critical_stock_discount
        self.price_increase_threshold = price_increase_threshold
        self.price_decrease_threshold = price_decrease_threshold
        self.aggressive_positioning_threshold = aggressive_positioning_threshold
        self.premium_positioning_threshold = premium_positioning_threshold
        self.confidence_boost_many_competitors = confidence_boost_many_competitors
        self.confidence_boost_few_competitors = confidence_boost_few_competitors
        self.confidence_boost_inventory = confidence_boost_inventory
        self.confidence_boost_demand = confidence_boost_demand
        self.min_demand_confidence = min_demand_confidence
        self.max_demand_confidence = max_demand_confidence
        self._default_price = 100.0
        self.price_history = pd.DataFrame()

    def calculate_price(self, context: PriceContext) -> Tuple[float, str, float]:
        min_price = self._calculate_minimum_price(context.cost)
        competitive_price = self._analyze_competition(context.competitor_prices)
        demand_adjusted_price = self._apply_demand_elasticity(
            competitive_price,
            context.demand_forecast
        )
        inventory_adjusted_price = self._adjust_for_inventory(
            demand_adjusted_price,
            context.inventory_level,
            context.days_in_stock
        )
        final_price = self._enforce_margin_constraints(
            inventory_adjusted_price,
            context.cost,
            min_price
        )
        confidence = self._calculate_confidence(context)
        reason = self._generate_reason(
            context,
            min_price,
            competitive_price,
            demand_adjusted_price,
            final_price
        )
        return round(final_price, 2), reason, confidence

    def calculate_batch_prices(
        self,
        contexts: List[PriceContext]
    ) -> pd.DataFrame:
        results = []
        for context in contexts:
            price, reason, confidence = self.calculate_price(context)
            margin = (price - context.cost) / context.cost if context.cost > 0 else 0
            results.append({
                'sku': context.sku,
                'current_price': context.current_price,
                'recommended_price': price,
                'margin_pct': margin,
                'confidence': confidence,
                'reason': reason,
                'cost': context.cost,
                'demand_forecast': context.demand_forecast,
                'inventory_level': context.inventory_level,
                'timestamp': datetime.utcnow()
            })
        
        df = pd.DataFrame(results)
        self.price_history = pd.concat([self.price_history, df], ignore_index=True)
        return df

    def _calculate_minimum_price(self, cost: float) -> float:
        """Preço mínimo: custo + margem mínima"""
        return cost * (1 + self.min_margin)

    def _analyze_competition(self, competitor_prices: List[float]) -> float:
        if not competitor_prices:
            return self._default_price
        prices_series = pd.Series(competitor_prices)
        median_price = prices_series.median()
        return median_price * (1 - self.competitive_discount)

    def _apply_demand_elasticity(
        self,
        base_price: float,
        demand_forecast: float
    ) -> float:
        return self._elasticity_calc(base_price, demand_forecast, self.elasticity_factor)

    @staticmethod
    @jit(nopython=True)
    def _elasticity_calc(base_price: float, demand: float, factor: float) -> float:
        deviation = (demand - 0.5) * 2
        elasticity_multiplier = 1.0 + (deviation * factor * 0.1)
        return base_price * elasticity_multiplier

    def _adjust_for_inventory(
        self,
        base_price: float,
        inventory_level: int,
        days_in_stock: int
    ) -> float:
        inventory_discount = 1.0
        
        if inventory_level > self.critical_inventory_threshold:
            inventory_discount *= (1 - self.critical_inventory_discount)
        elif inventory_level > self.high_inventory_threshold:
            inventory_discount *= (1 - self.high_inventory_discount)
        
        if days_in_stock > self.critical_stock_days_threshold:
            inventory_discount *= (1 - self.critical_stock_discount)
        elif days_in_stock > self.old_stock_days_threshold:
            inventory_discount *= (1 - self.old_stock_discount)
        
        return base_price * inventory_discount

    def _enforce_margin_constraints(
        self,
        suggested_price: float,
        cost: float,
        min_price: float
    ) -> float:
        price = max(suggested_price, min_price)
        max_price = cost * (1 + self.max_margin)
        return min(price, max_price)

    def _calculate_confidence(self, context: PriceContext) -> float:
        confidence = self.base_confidence
        
        num_competitors = len(context.competitor_prices)
        if num_competitors >= 3:
            confidence += self.confidence_boost_many_competitors
        elif num_competitors >= 1:
            confidence += self.confidence_boost_few_competitors
        
        if context.inventory_level > 0:
            confidence += self.confidence_boost_inventory
        
        if self.min_demand_confidence < context.demand_forecast < self.max_demand_confidence:
            confidence += self.confidence_boost_demand
        
        return min(confidence, 1.0)

    def _generate_reason(
        self,
        context: PriceContext,
        min_price: float,
        competitive_price: float,
        demand_adjusted_price: float,
        final_price: float
    ) -> str:
        price_delta = ((final_price - context.current_price) / context.current_price * 100)
        reasons = []
        
        if price_delta > self.price_increase_threshold:
            reasons.append("INCREASE: High demand or favorable competition")
        elif price_delta < -self.price_decrease_threshold:
            reasons.append(f"DISCOUNT: High inventory ({context.inventory_level}) or low demand")
        else:
            reasons.append("STABLE: Market aligned")
        
        if context.competitor_prices:
            avg_comp = np.mean(context.competitor_prices)
            if final_price < avg_comp * (1 - self.aggressive_positioning_threshold):
                reasons.append("Aggressive positioning")
            elif final_price > avg_comp * (1 + self.premium_positioning_threshold):
                reasons.append("Premium positioning")
        
        return " | ".join(reasons)

    def get_price_history(self) -> pd.DataFrame:
        return self.price_history.copy()

    def analyze_price_trends(self, sku: Optional[str] = None) -> Dict:
        if self.price_history.empty:
            return {}
        df = self.price_history if not sku else self.price_history[self.price_history['sku'] == sku]
        if df.empty:
            return {}
        return {
            'mean_recommended_price': df['recommended_price'].mean(),
            'mean_margin': df['margin_pct'].mean(),
            'price_volatility': df['recommended_price'].std(),
            'total_decisions': len(df),
            'avg_confidence': df['confidence'].mean()
        }
