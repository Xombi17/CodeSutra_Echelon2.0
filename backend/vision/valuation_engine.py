"""
Valuation Engine for Silver Objects
Calculates market value based on CV analysis + current silver prices
"""
import asyncio
from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime
import yfinance as yf

from .vision_pipeline import VisionAnalysisResult


@dataclass
class ValuationResult:
    """Valuation calculation result"""
    base_value: float  # Pure metal value
    adjusted_value: float  # After premiums/penalties
    value_range: tuple[float, float]  # (min, max) accounting for uncertainty
    spot_price_per_gram: float  # Current market price
    craftsmanship_premium: float  # % premium for craftsmanship
    condition_penalty: float  # % penalty for condition
    overall_confidence: float  # 0.0-1.0
    currency: str = "INR"
    calculation_timestamp: str = ""
    
    def __post_init__(self):
        if not self.calculation_timestamp:
            self.calculation_timestamp = datetime.now().isoformat()


class ValuationEngine:
    """
    Calculate silver object value based on:
    1. Current spot price
    2. Purity/weight
    3. Craftsmanship premium
    4. Condition penalty
    """
    
    # Premium percentages by object type and quality
    CRAFTSMANSHIP_PREMIUMS = {
        "jewelry": {
            "high": 0.30,    # 30% premium for high-quality jewelry
            "medium": 0.15,  # 15% for average
            "low": 0.05      # 5% for basic
        },
        "coin": {
            "high": 0.12,    # 12% premium for rare/collectible coins
            "medium": 0.08,  # 8% for standard bullion coins
            "low": 0.03      # 3% for common coins
        },
        "bar": {
            "high": 0.05,    # 5% for certified bars
            "medium": 0.02,  # 2% for standard bars
            "low": 0.00      # 0% for unofficial bars
        },
        "utensil": {
            "high": 0.20,    # 20% for antique silver utensils
            "medium": 0.10,  # 10% for vintage
            "low": 0.02      # 2% for modern
        }
    }
    
    def __init__(self):
        """Initialize valuation engine"""
        self._cached_spot_price: Optional[float] = None
        self._cache_timestamp: Optional[datetime] = None
        self._cache_duration_seconds = 300  # 5 minutes
    
    async def calculate_value(
        self,
        analysis: VisionAnalysisResult,
        use_narrative_context: bool = False
    ) -> ValuationResult:
        """
        Calculate market value of silver object
        
        Args:
            analysis: Vision analysis result
            use_narrative_context: Whether to adjust for market narratives (future feature)
            
        Returns:
            ValuationResult with pricing breakdown
        """
        # Get current spot price
        spot_price = await self.get_current_spot_price()
        
        # Base value calculation
        purity_factor = (analysis.purity or 925) / 1000  # Default to 925 if unknown
        base_value = analysis.estimated_weight_g * purity_factor * spot_price
        
        # Apply craftsmanship premium
        craftsmanship_premium = self._calculate_craftsmanship_premium(
            object_type=analysis.detected_type,
            quality_score=analysis.quality_score
        )
        
        # Apply condition penalty
        condition_penalty = self._calculate_condition_penalty(
            quality_score=analysis.quality_score
        )
        
        # Calculate adjusted value
        adjusted_value = base_value * (1 + craftsmanship_premium - condition_penalty)
        
        # Value range accounting for weight estimation uncertainty
        # Typical ±15-20% for weight, ±5% for price
        uncertainty_range = 0.20  # 20% margin
        min_value = adjusted_value * (1 - uncertainty_range)
        max_value = adjusted_value * (1 + uncertainty_range)
        
        return ValuationResult(
            base_value=round(base_value, 2),
            adjusted_value=round(adjusted_value, 2),
            value_range=(round(min_value, 2), round(max_value, 2)),
            spot_price_per_gram=round(spot_price, 2),
            craftsmanship_premium=craftsmanship_premium,
            condition_penalty=condition_penalty,
            overall_confidence=analysis.overall_confidence,
            currency="INR"
        )
    
    async def get_current_spot_price(self) -> float:
        """
        Fetch current silver spot price in INR per gram
        
        Uses cache to avoid frequent API calls
        """
        # Check cache
        if self._is_cache_valid():
            return self._cached_spot_price
        
        try:
            # Use XAGUSD (silver spot) as primary - price per troy ounce
            symbol = "XAGUSD=X"
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            if info and 'regularMarketPrice' in info:
                usd_price_per_oz = info.get('regularMarketPrice', 0)
                
                # Convert USD/oz to INR/gram
                # 1 troy ounce = 31.1035 grams
                troy_ounce_to_grams = 31.1035
                
                # Fetch live USD/INR rate or use realistic fallback
                try:
                    forex = yf.Ticker("INR=X")
                    rate_info = forex.info
                    usd_to_inr = rate_info.get('regularMarketPrice', 83.50)
                except:
                    usd_to_inr = 83.50
                
                spot_inr_gram = (usd_price_per_oz / troy_ounce_to_grams) * usd_to_inr
                
                # Cache the result
                self._cached_spot_price = spot_inr_gram
                self._cache_timestamp = datetime.now()
                
                print(f"✅ Valuation Engine: Fetched spot price ₹{spot_inr_gram:.2f}/gram (${usd_price_per_oz:.2f}/oz)")
                return spot_inr_gram
            else:
                raise ValueError("No price data in info")
        
        except Exception as e:
            print(f"Failed to fetch spot price: {e}")
            # Fallback based on realistic per-gram price (~₹95)
            return 95.0 # Updated fallback to be more accurate for 2025/2026
    
    async def _fetch_silver_price_yfinance(self) -> float:
        """Fetch silver price from Yahoo Finance"""
        loop = asyncio.get_event_loop()
        
        def fetch():
            silver = yf.Ticker("SI=F")
            data = silver.history(period="1d")
            if not data.empty:
                return data['Close'].iloc[-1]
            raise ValueError("No price data available")
        
        price_usd_oz = await loop.run_in_executor(None, fetch)
        return price_usd_oz
    
    def _is_cache_valid(self) -> bool:
        """Check if cached price is still valid"""
        if self._cached_spot_price is None or self._cache_timestamp is None:
            return False
        
        elapsed = (datetime.now() - self._cache_timestamp).total_seconds()
        return elapsed < self._cache_duration_seconds
    
    def _calculate_craftsmanship_premium(
        self,
        object_type: str,
        quality_score: int
    ) -> float:
        """
        Calculate premium based on craftsmanship quality
        
        Higher quality → higher premium above melt value
        """
        object_type = object_type.lower()
        if object_type not in self.CRAFTSMANSHIP_PREMIUMS:
            object_type = "jewelry"  # Default
        
        # Determine quality tier
        if quality_score >= 80:
            tier = "high"
        elif quality_score >= 60:
            tier = "medium"
        else:
            tier = "low"
        
        return self.CRAFTSMANSHIP_PREMIUMS[object_type][tier]
    
    def _calculate_condition_penalty(self, quality_score: int) -> float:
        """
        Calculate penalty for poor condition
        
        Tarnish, scratches, damage reduce value
        """
        if quality_score >= 75:
            return 0.00  # No penalty for good condition
        elif quality_score >= 60:
            return 0.05  # 5% penalty for minor issues
        elif quality_score >= 40:
            return 0.15  # 15% penalty for significant wear
        else:
            return 0.30  # 30% penalty for poor condition
    
    def format_valuation_for_display(self, valuation: ValuationResult) -> Dict[str, Any]:
        """Format valuation for API response"""
        return {
            "base_value": valuation.base_value,
            "adjusted_value": valuation.adjusted_value,
            "value_range": {
                "min": valuation.value_range[0],
                "max": valuation.value_range[1]
            },
            "currency": valuation.currency,
            "spot_price_per_gram": valuation.spot_price_per_gram,
            "breakdown": {
                "craftsmanship_premium": f"{valuation.craftsmanship_premium * 100:.1f}%",
                "condition_penalty": f"{valuation.condition_penalty * 100:.1f}%"
            },
            "confidence": valuation.overall_confidence,
            "timestamp": valuation.calculation_timestamp
        }
