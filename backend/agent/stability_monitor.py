"""
Stability Monitor (PS 14 Implementation)
Detects overconfidence risk during stable market periods
"""
from typing import Dict, Any, List
from datetime import datetime, timedelta
import numpy as np
from database import get_session, PriceData
from config import config


class StabilityMonitor:
    """
    Monitors market stability and warns of overconfidence risk
    Implements PS 14: Paradoxical stability indicator
    
    Concept: When markets are TOO stable, traders become overconfident
    and a volatility spike becomes more likely
    """
    
    def calculate_stability_score(
        self,
        window_days: int = None
    ) -> Dict[str, Any]:
        """
        Calculate stability score (0-100)
        LOW score = HIGH RISK (market too stable)
        
        Args:
            window_days: Analysis window
            
        Returns:
            Dict with score, warning, and recommendation
        """
        if window_days is None:
            window_days = config.trading.stability_window_days
        
        session = get_session()
        
        try:
            cutoff = datetime.utcnow() - timedelta(days=window_days)
            prices = session.query(PriceData).filter(
                PriceData.timestamp >= cutoff
            ).order_by(PriceData.timestamp).all()
            
            if len(prices) < 10:
                return {
                    "score": 50,
                    "warning": "Insufficient data",
                    "recommendation": "Collect more price history",
                    "volatility": None
                }
            
            price_values = [p.price for p in prices]
            volatility = np.std(price_values) / np.mean(price_values) * 100
            
            # Paradoxical scoring: LOW volatility = LOW score = HIGH RISK
            if volatility < config.trading.high_stability_volatility_threshold:
                score = 20
                warning = "🔴 CAUTION: Market too stable. Volatility spike likely."
                recommendation = "Reduce position size by 30-50%"
                risk_level = "HIGH"
            
            elif volatility < config.trading.medium_stability_volatility_threshold:
                score = 50
                warning = "🟡 Low volatility detected. Stay alert."
                recommendation = "Monitor for breakout signals"
                risk_level = "MEDIUM"
            
            else:
                score = 80
                warning = None
                recommendation = "Normal market conditions"
                risk_level = "LOW"
            
            # Additional metrics
            price_range = max(price_values) - min(price_values)
            range_percentage = (price_range / np.mean(price_values)) * 100
            
            # Calculate consecutive stable days
            stable_days = self._count_stable_days(prices)
            
            return {
                "score": score,
                "risk_level": risk_level,
                "warning": warning,
                "recommendation": recommendation,
                "volatility": round(volatility, 2),
                "volatility_percentage": f"{volatility:.2f}%",
                "price_range_percentage": round(range_percentage, 2),
                "stable_days_streak": stable_days,
                "window_days": window_days,
                "samples": len(prices)
            }
        
        finally:
            session.close()
    
    def _count_stable_days(self, prices: List[PriceData]) -> int:
        """Count consecutive days with low daily volatility"""
        
        if len(prices) < 2:
            return 0
        
        # Group by day
        daily_prices = {}
        for price in prices:
            day = price.timestamp.date()
            if day not in daily_prices:
                daily_prices[day] = []
            daily_prices[day].append(price.price)
        
        # Calculate daily volatilities
        daily_vols = []
        for day, day_prices in sorted(daily_prices.items()):
            if len(day_prices) > 1:
                vol = np.std(day_prices) / np.mean(day_prices) * 100
                daily_vols.append(vol)
        
        # Count consecutive stable days (volatility < 0.5%)
        stable_streak = 0
        for vol in reversed(daily_vols):
            if vol < 0.5:
                stable_streak += 1
            else:
                break
        
        return stable_streak
    
    def get_position_adjustment(self, stability_score: int) -> float:
        """
        Get recommended position size adjustment based on stability
        
        Args:
            stability_score: Score from calculate_stability_score
            
        Returns:
            Multiplier for position size (e.g., 0.7 = reduce by 30%)
        """
        if stability_score <= 30:
            # High risk - reduce by 50%
            return 0.5
        elif stability_score <= 50:
            # Medium risk - reduce by 20%
            return 0.8
        else:
            # Normal - no adjustment
            return 1.0
    
    def generate_alert(self) -> Dict[str, Any]:
        """
        Generate stability alert if needed
        
        Returns:
            Alert dict or None
        """
        result = self.calculate_stability_score()
        
        if result["risk_level"] == "HIGH":
            return {
                "type": "STABILITY_WARNING",
                "severity": "HIGH",
                "title": "Overconfidence Risk Detected",
                "message": result["warning"],
                "recommendation": result["recommendation"],
                "data": {
                    "volatility": result["volatility_percentage"],
                    "stable_days": result["stable_days_streak"]
                },
                "timestamp": datetime.utcnow()
            }
        
        return None


# Global stability monitor
stability_monitor = StabilityMonitor()


if __name__ == "__main__":
    # Test stability monitor
    print("🧪 Testing Stability Monitor (PS 14)...\n")
    
    result = stability_monitor.calculate_stability_score()
    
    print(f"Stability Score: {result['score']}/100")
    print(f"Risk Level: {result['risk_level']}")
    print(f"Volatility: {result['volatility_percentage']}")
    print(f"Stable Days Streak: {result['stable_days_streak']}")
    
    if result['warning']:
        print(f"\n{result['warning']}")
        print(f"💡 Recommendation: {result['recommendation']}")
    
    # Test adjustment
    adjustment = stability_monitor.get_position_adjustment(result['score'])
    print(f"\nPosition Size Adjustment: {adjustment*100:.0f}%")
    
    # Test alert
    alert = stability_monitor.generate_alert()
    if alert:
        print(f"\n⚠️ ALERT: {alert['title']}")
        print(f"   {alert['message']}")
