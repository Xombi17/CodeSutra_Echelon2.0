"""
Trading Agent
Autonomous decision engine that translates narrative states into trading signals
"""
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Literal
from dataclasses import dataclass
from database import get_session, Narrative, TradingSignal, PriceData
from narrative.lifecycle_tracker import lifecycle_tracker, NarrativePhase
from config import config
import numpy as np


@dataclass
class Signal:
    """Trading signal recommendation"""
    action: Literal["BUY", "SELL", "HOLD"]
    confidence: float  # 0.0 to 1.0
    strength: int  # 0 to 100
    reasoning: str
    position_size: float  # Percentage allocation
    dominant_narrative: Optional[str] = None
    price_at_signal: Optional[float] = None
    conflicts: List[Dict] = None


class TradingAgent:
    """
    Autonomous trading agent
    Makes buy/sell decisions based on narrative lifecycle phases
    """
    
    # Maximum number of signals to keep in memory
    _max_signal_history = 100
    
    def __init__(self):
        self.signal_history: List[Signal] = []
    
    async def generate_signal(self) -> Signal:
        """
        Generate current trading signal based on all active narratives
        
        Returns:
            Signal with BUY/SELL/HOLD recommendation
        """
        print("🤖 Generating trading signal...")
        
        # Get all active narratives
        session = get_session()
        
        try:
            narratives = session.query(Narrative).filter(
                Narrative.phase != 'death'
            ).order_by(Narrative.strength.desc()).all()
            
            if not narratives:
                return self._no_signal()
            
            # Get dominant narrative
            dominant = narratives[0]
            
            # Check for conflicts
            conflicts = lifecycle_tracker.calculate_metrics(dominant).get("conflicts", [])
            
            # Get current price
            current_price = await self._get_current_price()
            
            # Decision logic based on dominant narrative phase
            signal = self._make_decision(dominant, narratives, conflicts, current_price)
            
            # Save signal to database
            await self._save_signal(signal)
            
            return signal
        
        finally:
            session.close()
    
    def _make_decision(
        self,
        dominant: Narrative,
        all_narratives: List[Narrative],
        conflicts: List[Dict],
        current_price: Optional[float]
    ) -> Signal:
        """Core decision logic"""
        
        phase = NarrativePhase(dominant.phase)
        strength = dominant.strength
        
        # Check for high-conviction conditions
        high_conviction = (
            strength > config.trading.high_conviction_strength and
            len(conflicts) == 0
        )
        
        # Decision matrix
        if phase == NarrativePhase.GROWTH:
            # Growth phase: BUY signals
            if strength > 70:
                action = "BUY"
                confidence = 0.85 if high_conviction else 0.65
                reasoning = f"Narrative '{dominant.name}' in GROWTH phase with high strength ({strength}/100)"
                
                if len(conflicts) > 0:
                    confidence *= 0.7
                    reasoning += f" | ⚠️ {len(conflicts)} conflicting narrative(s) detected"
            
            elif strength > 60:
                action = "BUY"
                confidence = 0.60
                reasoning = f"Narrative '{dominant.name}' in GROWTH phase with moderate strength ({strength}/100)"
            
            else:
                action = "HOLD"
                confidence = 0.50
                reasoning = f"Narrative in GROWTH but strength too low ({strength}/100)"
        
        elif phase == NarrativePhase.PEAK:
            # Peak phase: HOLD and prepare to exit
            action = "HOLD"
            confidence = 0.75
            reasoning = f"Narrative '{dominant.name}' at PEAK ({strength}/100) - monitor for reversal signals"
        
        elif phase == NarrativePhase.REVERSAL:
            # Reversal phase: SELL signals
            if strength > 50:
                action = "SELL"
                confidence = 0.80
                reasoning = f"Narrative '{dominant.name}' in REVERSAL phase - exit recommended"
            else:
                action = "SELL"
                confidence = 0.90
                reasoning = f"Narrative '{dominant.name}' in REVERSAL with weakening strength - strong exit signal"
        
        elif phase == NarrativePhase.DEATH:
            # Death phase: SELL immediately
            action = "SELL"
            confidence = 0.95
            reasoning = f"Narrative '{dominant.name}' DEAD - immediate exit"
        
        else:  # BIRTH
            # Birth phase: Monitor, don't act yet
            action = "HOLD"
            confidence = 0.40
            reasoning = f"Narrative '{dominant.name}' in BIRTH phase - too early to act"
        
        # Calculate position size
        position_size = self.calculate_position_size(
            Signal(
                action=action,
                confidence=confidence,
                strength=strength,
                reasoning=reasoning,
                position_size=1.0  # Temporary
            ),
            all_narratives,
            conflicts
        )
        
        return Signal(
            action=action,
            confidence=confidence,
            strength=strength,
            reasoning=reasoning,
            position_size=position_size,
            dominant_narrative=dominant.name,
            price_at_signal=current_price,
            conflicts=conflicts
        )
    
    def calculate_position_size(
        self,
        signal: Signal,
        narratives: List[Narrative],
        conflicts: List[Dict]
    ) -> float:
        """
        Calculate recommended position size
        
        Args:
            signal: Trading signal
            narratives: All active narratives
            conflicts: Detected conflicts
            
        Returns:
            Position size as percentage (0.0 to 1.5)
        """
        base_size = 1.0  # 100% allocation
        
        # Reduce size if conflicts exist
        if conflicts:
            base_size *= 0.5
            print(f"📉 Position size reduced by 50% due to {len(conflicts)} conflicts")
        
        # Reduce size for low confidence
        if signal.confidence < config.trading.low_confidence_threshold:
            base_size *= signal.confidence
            print(f"📉 Position size reduced to {signal.confidence*100:.0f}% due to low confidence")
        
        # Increase size for high-conviction trades
        if (signal.confidence > config.trading.high_conviction_confidence and 
            signal.strength > config.trading.high_conviction_strength):
            base_size *= 1.2
            print(f"📈 Position size increased by 20% (high conviction)")
        
        # Cap at max position size
        final_size = min(base_size, config.trading.max_position_size)
        
        return round(final_size, 2)
    
    async def _get_current_price(self) -> Optional[float]:
        """Get current silver price"""
        session = get_session()
        
        try:
            latest_price = session.query(PriceData).order_by(
                PriceData.timestamp.desc()
            ).first()
            
            return latest_price.price if latest_price else None
        
        finally:
            session.close()
    
    def _no_signal(self) -> Signal:
        """Return neutral signal when no narratives exist"""
        return Signal(
            action="HOLD",
            confidence=0.0,
            strength=0,
            reasoning="No active narratives detected",
            position_size=0.0
        )
    
    async def _save_signal(self, signal: Signal):
        """Save signal to database"""
        session = get_session()
        
        try:
            # Get dominant narrative ID
            narrative_id = None
            if signal.dominant_narrative:
                narrative = session.query(Narrative).filter_by(
                    name=signal.dominant_narrative
                ).first()
                if narrative:
                    narrative_id = narrative.id
            
            db_signal = TradingSignal(
                action=signal.action,
                confidence=signal.confidence,
                strength=signal.strength,
                reasoning=signal.reasoning,
                position_size=signal.position_size,
                dominant_narrative_id=narrative_id,
                price_at_signal=signal.price_at_signal,
                signal_metadata={"conflicts": signal.conflicts} if signal.conflicts else None
            )
            
            session.add(db_signal)
            session.commit()
            
            self.signal_history.append(signal)
            
            # Prevent memory leak by limiting signal history size
            if len(self.signal_history) > self._max_signal_history:
                self.signal_history = self.signal_history[-self._max_signal_history:]
            
            print(f"💾 Signal saved: {signal.action} (confidence: {signal.confidence:.0%})")
        
        except Exception as e:
            session.rollback()
            print(f"❌ Error saving signal: {e}")
        
        finally:
            session.close()
    
    def get_signal_explanation(self, signal: Signal) -> str:
        """
        Get human-readable explanation of signal
        
        Returns:
            Formatted explanation string
        """
        icon = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}[signal.action]
        
        explanation = f"""
{icon} {signal.action} Signal
Confidence: {signal.confidence:.0%} | Strength: {signal.strength}/100
Position Size: {signal.position_size*100:.0f}%

📊 Reasoning:
{signal.reasoning}

💰 Current Price: ₹{signal.price_at_signal:,.0f}/kg

{f"⚠️ Conflicts: {len(signal.conflicts)} competing narrative(s)" if signal.conflicts else "✅ No conflicts detected"}
        """.strip()
        
        return explanation
    
    def get_detailed_explanation(self, signal: Signal, narrative: Narrative) -> Dict[str, Any]:
        """
        Generate detailed explanation with metrics breakdown
        Inspired by nevan's explainer pattern
        """
        metrics = lifecycle_tracker.calculate_metrics(narrative)
        
        return {
            "decision": signal.action,
            "triggered_rule": f"{narrative.phase.upper()} phase AND strength > {config.trading.high_conviction_strength}",
            "metrics_used": {
                "velocity_increase": f"{metrics['velocity_increase']:.2%}",
                "price_correlation": f"{metrics['price_correlation']:.2f}",
                "sentiment_trend": metrics["sentiment_trend"],
                "current_velocity": f"{metrics['current_velocity']:.2f} mentions/hour"
            },
            "phase_explanation": self._explain_phase(narrative, metrics),
            "confidence_breakdown": {
                "base_confidence": 0.85,
                "conflict_penalty": -0.15 if signal.conflicts else 0.0,
                "strength_adjustment": 0.0 if signal.strength > 70 else -0.1,
                "final_confidence": signal.confidence
            },
            "reasoning": signal.reasoning
        }
    
    def _explain_phase(self, narrative: Narrative, metrics: Dict[str, Any]) -> str:
        """Explain why narrative is in current phase"""
        from narrative.lifecycle_tracker import NarrativePhase
        
        phase = NarrativePhase(narrative.phase)
        age_days = (datetime.utcnow() - narrative.birth_date).days
        
        if phase == NarrativePhase.BIRTH:
            return f"New narrative detected {age_days} days ago"
        elif phase == NarrativePhase.GROWTH:
            return f"Velocity increased by {metrics['velocity_increase']:.1%}, indicating growing interest"
        elif phase == NarrativePhase.PEAK:
            return f"Price correlation at {metrics['price_correlation']:.2f}, suggesting peak influence"
        elif phase == NarrativePhase.REVERSAL:
            return f"Sentiment declining with {len(metrics.get('conflicts', []))} conflicting narratives"
        else:
            return f"No mentions in last 48 hours"
    
    async def backtest(
        self,
        days_back: int = 30
    ) -> Dict[str, Any]:
        """
        Simple backtest of strategy
        
        Args:
            days_back: How many days to backtest
            
        Returns:
            Backtest results
        """
        print(f"📊 Running backtest for last {days_back} days...")
        
        # This is a simplified version
        # Full implementation would simulate trades over time
        
        session = get_session()
        
        try:
            cutoff = datetime.utcnow() - timedelta(days=days_back)
            
            # Get price range
            prices = session.query(PriceData).filter(
                PriceData.timestamp >= cutoff
            ).order_by(PriceData.timestamp).all()
            
            if len(prices) < 2:
                return {"error": "Insufficient price data"}
            
            start_price = prices[0].price
            end_price = prices[-1].price
            buy_and_hold_return = (end_price - start_price) / start_price
            
            return {
                "period_days": days_back,
                "start_price": start_price,
                "end_price": end_price,
                "buy_and_hold_return": buy_and_hold_return * 100,
                "note": "Full backtest implementation pending"
            }
        
        finally:
            session.close()


# Global trading agent
trading_agent = TradingAgent()


if __name__ == "__main__":
    # Test trading agent
    async def test():
        print("🧪 Testing Trading Agent...\n")
        
        # Generate signal
        signal = await trading_agent.generate_signal()
        
        print("\n" + "="*50)
        print(trading_agent.get_signal_explanation(signal))
        print("="*50)
        
        # Run simple backtest
        backtest_results = await trading_agent.backtest(days_back=30)
        print(f"\n📊 Backtest Results:")
        print(f"Period: {backtest_results.get('period_days')} days")
        print(f"Buy & Hold Return: {backtest_results.get('buy_and_hold_return', 0):.2f}%")
    
    asyncio.run(test())
