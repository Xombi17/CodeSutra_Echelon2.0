"""
Lifecycle Tracker (PS 6 Implementation)
Tracks narrative phases and detects transitions
"""
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Literal
from enum import Enum
import numpy as np
from database import get_session, Narrative, Article, PriceData
from narrative.sentiment_analyzer import sentiment_analyzer
from config import config


class NarrativePhase(str, Enum):
    """Narrative lifecycle phases"""
    BIRTH = "birth"
    GROWTH = "growth"
    PEAK = "peak"
    REVERSAL = "reversal"
    DEATH = "death"


class LifecycleTracker:
    """
    Tracks narrative lifecycle and phase transitions
    Implements PS 6: Sentiment & Lifecycle Tracker
    """
    
    def __init__(self):
        self.phase_history = {}  # Track phase changes
    
    def calculate_metrics(self, narrative: Narrative) -> Dict[str, Any]:
        """
        Calculate all metrics needed for phase detection
        
        Args:
            narrative: Narrative to analyze
            
        Returns:
            Dict with velocity, correlation, sentiment metrics
        """
        session = get_session()
        
        try:
            # Calculate mention velocity (mentions per hour)
            velocity = self._calculate_velocity(narrative, session)
            
            # Calculate price correlation
            correlation = self._calculate_price_correlation(narrative, session)
            
            # Get sentiment metrics
            sentiment_data = sentiment_analyzer.analyze_narrative_sentiment(
                narrative.id,
                hours_back=24
            )
            
            # Check for conflicting narratives
            conflicts = self._detect_conflicts_for_narrative(narrative, session)
            
            # Calculate mentions in last 48h
            cutoff = datetime.utcnow() - timedelta(hours=48)
            mentions_48h = session.query(Article).filter(
                Article.narrative_id == narrative.id,
                Article.published_at >= cutoff
            ).count()
            
            return {
                "velocity_increase": velocity.get("increase_ratio", 0.0),
                "price_correlation": correlation,
                "sentiment_decline": sentiment_data.get("sentiment_change", 0.0) < -0.1,
                "conflicting_narratives_detected": len(conflicts) > 0,
                "mentions_48h": mentions_48h,
                "current_velocity": velocity.get("current", 0.0),
                "sentiment_trend": sentiment_data.get("trend", "stable"),
                "conflicts": conflicts
            }
        
        finally:
            session.close()
    
    def _calculate_velocity(
        self,
        narrative: Narrative,
        session
    ) -> Dict[str, float]:
        """Calculate mention velocity and increase ratio"""
        
        # Get mentions in last 24h and 24-48h ago
        now = datetime.utcnow()
        cutoff_24h = now - timedelta(hours=24)
        cutoff_48h = now - timedelta(hours=48)
        
        recent_mentions = session.query(Article).filter(
            Article.narrative_id == narrative.id,
            Article.published_at >= cutoff_24h
        ).count()
        
        previous_mentions = session.query(Article).filter(
            Article.narrative_id == narrative.id,
            Article.published_at >= cutoff_48h,
            Article.published_at < cutoff_24h
        ).count()
        
        current_velocity = recent_mentions / 24.0  # Per hour
        
        if previous_mentions > 0:
            increase_ratio = (recent_mentions - previous_mentions) / previous_mentions
        else:
            increase_ratio = 1.0 if recent_mentions > 0 else 0.0
        
        return {
            "current": current_velocity,
            "increase_ratio": increase_ratio,
            "recent_count": recent_mentions,
            "previous_count": previous_mentions
        }
    
    def _calculate_price_correlation(
        self,
        narrative: Narrative,
        session
    ) -> float:
        """Calculate correlation between narrative mentions and price"""
        
        # Get articles with timestamps
        cutoff = datetime.utcnow() - timedelta(days=7)
        articles = session.query(Article).filter(
            Article.narrative_id == narrative.id,
            Article.published_at >= cutoff
        ).order_by(Article.published_at).all()
        
        if len(articles) < 5:
            return 0.0
        
        # Group by day and count
        daily_mentions = {}
        for article in articles:
            day = article.published_at.date()
            daily_mentions[day] = daily_mentions.get(day, 0) + 1
        
        # Get prices for same period
        prices = session.query(PriceData).filter(
            PriceData.timestamp >= cutoff
        ).order_by(PriceData.timestamp).all()
        
        if len(prices) < 5:
            return 0.0
        
        # Group prices by day (simple average)
        daily_prices = {}
        for price in prices:
            day = price.timestamp.date()
            if day not in daily_prices:
                daily_prices[day] = []
            daily_prices[day].append(price.price)
        
        daily_avg_prices = {day: np.mean(prices) for day, prices in daily_prices.items()}
        
        # Find common days
        common_days = set(daily_mentions.keys()) & set(daily_avg_prices.keys())
        
        if len(common_days) < 3:
            return 0.0
        
        # Calculate correlation
        mentions_series = [daily_mentions[day] for day in sorted(common_days)]
        price_series = [daily_avg_prices[day] for day in sorted(common_days)]
        
        try:
            correlation = np.corrcoef(mentions_series, price_series)[0, 1]
            return float(correlation) if not np.isnan(correlation) else 0.0
        except:
            return 0.0
    
    def _detect_conflicts_for_narrative(
        self,
        narrative: Narrative,
        session
    ) -> List[Dict[str, Any]]:
        """Detect narratives conflicting with this one"""
        
        # Get other active narratives
        other_narratives = session.query(Narrative).filter(
            Narrative.id != narrative.id,
            Narrative.phase.in_(['growth', 'peak']),
            Narrative.strength >= config.narrative.min_strength_for_conflict
        ).all()
        
        conflicts = []
        
        for other in other_narratives:
            # Check if sentiments are opposing
            if self._are_opposing(narrative, other):
                strength_diff = abs(narrative.strength - other.strength)
                conflicts.append({
                    "narrative_id": other.id,
                    "narrative_name": other.name,
                    "strength_diff": strength_diff,
                    "winner": narrative.name if narrative.strength > other.strength else other.name
                })

        
        return conflicts
    
    def _are_opposing(self, n1: Narrative, n2: Narrative) -> bool:
        """Check if two narratives have opposing sentiments"""
        
        # Simple check: if one is positive and one is negative
        if n1.sentiment is None or n2.sentiment is None:
            return False
        
        return (n1.sentiment > 0.1 and n2.sentiment < -0.1) or \
               (n1.sentiment < -0.1 and n2.sentiment > 0.1)
    
    def detect_phase_transition(
        self,
        narrative: Narrative
    ) -> Optional[NarrativePhase]:
        """
        Detect if narrative should transition to new phase
        
        Args:
            narrative: Narrative to check
            
        Returns:
            New phase if transition should occur, None otherwise
        """
        current_phase = NarrativePhase(narrative.phase)
        metrics = self.calculate_metrics(narrative)
        
        # Birth → Growth
        if current_phase == NarrativePhase.BIRTH:
            if metrics["velocity_increase"] > config.narrative.birth_to_growth_velocity_threshold:
                return NarrativePhase.GROWTH
        
        # Growth → Peak
        elif current_phase == NarrativePhase.GROWTH:
            if metrics["price_correlation"] > config.narrative.growth_to_peak_correlation_threshold:
                return NarrativePhase.PEAK
        
        # Peak → Reversal
        elif current_phase == NarrativePhase.PEAK:
            if (metrics["sentiment_decline"] or 
                metrics["conflicting_narratives_detected"]):
                return NarrativePhase.REVERSAL
        
        # Reversal → Death
        elif current_phase == NarrativePhase.REVERSAL:
            if metrics["mentions_48h"] == 0:
                return NarrativePhase.DEATH
        
        return None
    
    def update_narrative_phase(self, narrative: Narrative, new_phase: NarrativePhase):
        """Update narrative to new phase"""
        session = get_session()
        
        try:
            old_phase = narrative.phase
            narrative.phase = new_phase.value
            narrative.last_updated = datetime.utcnow()
            
            if new_phase == NarrativePhase.DEATH:
                narrative.death_date = datetime.utcnow()
            
            # Track history
            if narrative.id not in self.phase_history:
                self.phase_history[narrative.id] = []
            
            self.phase_history[narrative.id].append({
                "from_phase": old_phase,
                "to_phase": new_phase.value,
                "timestamp": datetime.utcnow()
            })
            
            session.add(narrative)
            session.commit()
            
            print(f"✨ Narrative '{narrative.name}' transitioned: {old_phase} → {new_phase.value}")
        
        finally:
            session.close()
    
    def calculate_narrative_strength(self, narrative: Narrative) -> int:
        """
        Calculate narrative strength score (0-100)
        
        Combines:
        - Social velocity (30%)
        - News intensity (25%)
        - Price correlation (25%)
        - Institutional alignment (20%)
        """
        session = get_session()
        
        try:
            metrics = self.calculate_metrics(narrative)
            
            # Social velocity score (0-100)
            velocity_score = min(metrics["current_velocity"] * 10, 100)
            
            # News intensity (article count)
            cutoff = datetime.utcnow() - timedelta(days=1)
            article_count = session.query(Article).filter(
                Article.narrative_id == narrative.id,
                Article.published_at >= cutoff
            ).count()
            news_score = min(article_count * 5, 100)
            
            # Price correlation score
            correlation_score = abs(metrics["price_correlation"]) * 100
            
            # Institutional alignment (placeholder - would use real data)
            institutional_score = 50  # Neutral default
            
            # Weighted sum
            strength = (
                velocity_score * config.narrative.social_velocity_weight +
                news_score * config.narrative.news_intensity_weight +
                correlation_score * config.narrative.price_correlation_weight +
                institutional_score * config.narrative.institutional_alignment_weight
            )
            
            return int(min(strength, 100))
        
        finally:
            session.close()
    
    async def track_all_narratives(self):
        """Track all active narratives and update phases"""
        session = get_session()
        
        try:
            active_narratives = session.query(Narrative).filter(
                Narrative.phase != 'death'
            ).all()
            
            print(f"🔄 Tracking {len(active_narratives)} active narratives...")
            
            for narrative in active_narratives:
                # Update strength
                new_strength = self.calculate_narrative_strength(narrative)
                narrative.strength = new_strength
                
                # Update sentiment
                sentiment_data = sentiment_analyzer.analyze_narrative_sentiment(narrative.id)
                narrative.sentiment = sentiment_data["current_sentiment"]
                
                # Check for phase transition
                new_phase = self.detect_phase_transition(narrative)
                
                if new_phase:
                    self.update_narrative_phase(narrative, new_phase)
                else:
                    narrative.last_updated = datetime.utcnow()
                    session.add(narrative)
            
            session.commit()
            print("✅ Narrative tracking complete")
        
        finally:
            session.close()
    
    def get_narrative_status(self, narrative_id: int) -> Dict[str, Any]:
        """Get comprehensive status of a narrative"""
        session = get_session()
        
        try:
            narrative = session.query(Narrative).get(narrative_id)
            if not narrative:
                return {}
            
            metrics = self.calculate_metrics(narrative)
            sentiment_data = sentiment_analyzer.analyze_narrative_sentiment(narrative_id)
            
            age_days = (datetime.utcnow() - narrative.birth_date).days if narrative.birth_date else 0
            
            return {
                "id": narrative.id,
                "name": narrative.name,
                "phase": narrative.phase,
                "strength": narrative.strength,
                "age_days": age_days,
                "metrics": metrics,
                "sentiment": sentiment_data,
                "phase_history": self.phase_history.get(narrative_id, [])
            }
        
        finally:
            session.close()


# Global lifecycle tracker
lifecycle_tracker = LifecycleTracker()


if __name__ == "__main__":
    # Test lifecycle tracker
    async def test():
        print("🧪 Testing Lifecycle Tracker (PS 6)...\n")
        
        # Track all narratives
        await lifecycle_tracker.track_all_narratives()
        
        # Get status of first narrative
        session = get_session()
        narrative = session.query(Narrative).first()
        
        if narrative:
            status = lifecycle_tracker.get_narrative_status(narrative.id)
            print(f"\n📊 Narrative Status: {status['name']}")
            print(f"Phase: {status['phase']}")
            print(f"Strength: {status['strength']}/100")
            print(f"Age: {status['age_days']} days")
            print(f"Metrics: {status['metrics']}")
        
        session.close()
    
    asyncio.run(test())
