"""
Geographic Bias Mitigation Module - ENHANCED VERSION
Addresses US media volume bias, cultural under-weighting, and supply/demand asymmetry

Features:
1. Cultural event boosting (Indian festivals)
2. Supply vs demand impact weighting
3. Consumer market size weighting  
4. Regional conflict detection
5. Transparency reporting
"""
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from database import get_session, Narrative, Article
import re


class GeographicBiasHandler:
    """
    Mitigates geographic bias in narrative strength scoring
    
    Key Enhancements:
    - Supply disruptions weighted 1.8x (Peru strike > US sentiment)
    - Cultural events boosted 1.3-1.5x during active months
    - Consumer market weighting (India 25% > US 10%)
    - Regional conflict detection with geographic context
    """
    
    # Known high-impact cultural events (India-focused)
    CULTURAL_EVENTS = {
        "dhanteras": {
            "boost_multiplier": 1.5,
            "typical_months": [10, 11],  # Oct-Nov (Diwali season)
            "description": "Major Indian gold/silver buying festival",
            "market_impact": "High - 40% of annual jewelry demand"
        },
        "akshaya tritiya": {
            "boost_multiplier": 1.4,
            "typical_months": [4, 5],  # Apr-May
            "description": "Auspicious day for precious metal purchases",
            "market_impact": "High - traditional buying day"
        },
        "diwali": {
            "boost_multiplier": 1.3,
            "typical_months": [10, 11],
            "description": "Festival of Lights - traditional gifting season",
            "market_impact": "Medium - silver gifting tradition"
        },
        "wedding season": {
            "boost_multiplier": 1.2,
            "typical_months": [11, 12, 1, 2],  # Nov-Feb
            "description": "Peak Indian wedding season",
            "market_impact": "Very High - sustained jewelry demand"
        }
    }
    
    # Impact type weights - NEW FEATURE
    IMPACT_TYPES = {
        "supply_disruption": 1.8,   # Mining strikes, production cuts
        "physical_demand": 1.4,     # Indian buying, Chinese imports
        "policy": 1.3,               # Fed rates, tariffs, duties
        "paper_sentiment": 1.0      # Futures trading, analyst opinions
    }
    
    # Consumer market shares - NEW FEATURE
    CONSUMER_MARKET_SHARE = {
        "india": 0.25,   # 25% of global silver demand
        "china": 0.20,   # 20%
        "us": 0.10,      # 10%
        "europe": 0.15,  # 15%
        "global": 1.0
    }
    
    # Regional source classification
    REGIONAL_SOURCES = {
        "india": ["economictimes", "indianexpress", "livemint", "moneycontrol", 
                  "hindustantimes", "business-standard", "bloombergquint"],
        "us": ["bloomberg", "wsj", "reuters", "cnbc", "marketwatch", 
               "financial-times", "barrons"],
        "china": ["scmp", "chinadaily", "xinhua"],
        "global": ["ft", "economist", "aljazeera", "bbc"]
    }
    
    def __init__(self):
        self.bias_metrics = {
            "total_articles_by_region": {},
            "narrative_strength_by_region": {},
            "cultural_boosts_applied": 0,
            "impact_type_boosts_applied": 0,
            "market_size_boosts_applied": 0
        }
    
    def calculate_adjusted_strength(
        self,
        narrative: Narrative,
        base_strength: int
    ) -> int:
        """
        Apply ALL geographic bias adjustments in sequence
        
        Order matters:
        1. Cultural boost (festival season)
        2. Impact type boost (supply > sentiment)
        3. Consumer market weight (India > US)
        
        Args:
            narrative: Narrative to adjust
            base_strength: Raw strength score (0-100)
        
        Returns:
            Adjusted strength (0-100)
        """
        strength = base_strength
        adjustments_applied = []
        
        # 1. Cultural event boost
        cultural_boost = self.apply_cultural_boost(narrative)
        if cultural_boost > 1.0:
            strength = int(strength * cultural_boost)
            adjustments_applied.append(f"Cultural: {cultural_boost}x")
        
        # 2. Impact type boost (NEW)
        impact_type = self.classify_narrative_impact_type(narrative)
        impact_boost = self.IMPACT_TYPES[impact_type]
        if impact_boost > 1.0:
            strength = int(strength * impact_boost)
            adjustments_applied.append(f"{impact_type}: {impact_boost}x")
            self.bias_metrics["impact_type_boosts_applied"] += 1
        
        # 3. Consumer market weight (NEW)
        region = self._get_narrative_region(narrative)
        market_boost = self._calculate_market_size_boost(region)
        if market_boost > 1.0:
            strength = int(strength * market_boost)
            adjustments_applied.append(f"Market size: {market_boost:.2f}x")
            self.bias_metrics["market_size_boosts_applied"] += 1
        
        # Log if any adjustments were made
        if adjustments_applied:
            print(f"📊 Adjusted '{narrative.name}': {base_strength} → {min(strength, 100)}")
            print(f"   Boosts: {', '.join(adjustments_applied)}")
        
        return min(strength, 100)
    
    def apply_cultural_boost(self, narrative: Narrative) -> float:
        """
        Apply strength boost for culturally significant narratives
        
        Returns:
            Boost multiplier (1.0 = no boost, 1.5 = 50% boost)
        """
        current_month = datetime.utcnow().month
        narrative_name_lower = narrative.name.lower()
        
        boost = 1.0
        applied_events = []
        
        for event_name, event_data in self.CULTURAL_EVENTS.items():
            # Check if event is mentioned in narrative name
            if event_name in narrative_name_lower or event_name.replace(" ", "") in narrative_name_lower:
                # Check if we're in the right time of year
                if current_month in event_data["typical_months"]:
                    boost = max(boost, event_data["boost_multiplier"])
                    applied_events.append(event_name)
                    self.bias_metrics["cultural_boosts_applied"] += 1
        
        return boost
    
    def classify_narrative_impact_type(self, narrative: Narrative) -> str:
        """
        NEW: Classify narrative by market impact type
        
        Supply disruptions > Physical demand > Policy > Sentiment
        """
        name_lower = narrative.name.lower()
        
        # Supply keywords (highest priority)
        supply_keywords = ["strike", "mine", "mining", "production", "shutdown", 
                          "supply", "output", "extraction", "refinery"]
        if any(k in name_lower for k in supply_keywords):
            return "supply_disruption"
        
        # Physical demand keywords
        physical_keywords = ["wedding", "festival", "jewelry", "coin", "bar", 
                            "buying", "demand", "imports", "exports", "consumption"]
        if any(k in name_lower for k in physical_keywords):
            return "physical_demand"
        
        # Policy keywords
        policy_keywords = ["rate", "fed", "tariff", "tax", "duty", "policy", 
                          "regulation", "government", "central bank"]
        if any(k in name_lower for k in policy_keywords):
            return "policy"
        
        # Default to sentiment (lowest weight)
        return "paper_sentiment"
    
    def _calculate_market_size_boost(self, region: str) -> float:
        """
        NEW: Calculate boost based on regional market size
        
        India (25% demand) deserves higher weight than US (10%)
        """
        market_share = self.CONSUMER_MARKET_SHARE.get(region, 0.1)
        
        # Boost if region is major consumer (20%+)
        if market_share >= 0.20:
            # Formula: 1.0 + (market_share * 0.5)
            # India (25%) → 1.125x boost
            # China (20%) → 1.10x boost
            return 1.0 + (market_share * 0.5)
        
        return 1.0
    
    def _get_narrative_region(self, narrative: Narrative) -> str:
        """Determine dominant region for narrative"""
        session = get_session()
        try:
            articles = session.query(Article).filter(
                Article.narrative_id == narrative.id
            ).limit(20).all()
            
            return self._get_dominant_region(articles)
        finally:
            session.close()
    
    def _get_dominant_region(self, articles: List[Article]) -> str:
        """Determine dominant region from article sources"""
        if not articles:
            return "global"
        
        region_counts = {"india": 0, "us": 0, "china": 0, "global": 0}
        
        for article in articles:
            region = self._classify_source_region(article.source)
            if region in region_counts:
                region_counts[region] += 1
            else:
                region_counts["global"] += 1
        
        # Return region with most articles
        return max(region_counts, key=region_counts.get)
    
    def _classify_source_region(self, source: str) -> str:
        """Classify article source by region"""
        source_lower = source.lower()
        
        for region, sources in self.REGIONAL_SOURCES.items():
            if any(s in source_lower for s in sources):
                return region
        
        return "global"
    
    def calculate_regional_distribution(self) -> Dict[str, Any]:
        """
        Calculate article distribution across regions
        Provides transparency into geographic bias
        """
        session = get_session()
        
        try:
            # Get all recent articles (last 30 days)
            cutoff = datetime.utcnow() - timedelta(days=30)
            articles = session.query(Article).filter(
                Article.published_at >= cutoff
            ).all()
            
            regional_counts = {"india": 0, "us": 0, "china": 0, "global": 0}
            regional_narratives = {"india": set(), "us": set(), "china": set(), "global": set()}
            
            for article in articles:
                region = self._classify_source_region(article.source)
                if region in regional_counts:
                    regional_counts[region] += 1
                
                if article.narrative_id and region in regional_narratives:
                    regional_narratives[region].add(article.narrative_id)
            
            total_articles = sum(regional_counts.values())
            
            return {
                "total_articles": total_articles,
                "articles_by_region": regional_counts,
                "region_percentages": {
                    region: (count / total_articles * 100) if total_articles > 0 else 0
                    for region, count in regional_counts.items()
                },
                "unique_narratives_by_region": {
                    region: len(narratives)
                    for region, narratives in regional_narratives.items()
                },
                "bias_warning": self._detect_bias_warning(regional_counts)
            }
        
        finally:
            session.close()
    
    def _detect_bias_warning(self, regional_counts: Dict[str, int]) -> Optional[str]:
        """Detect if any region is dominating coverage"""
        total = sum(regional_counts.values())
        if total == 0:
            return None
        
        for region, count in regional_counts.items():
            percentage = (count / total) * 100
            if percentage > 60:  # If one region >60% of coverage
                return f"{region.upper()} media dominance ({percentage:.0f}%)"
        
        return None
    
    def detect_regional_conflict(
        self,
        narrative1: Narrative,
        narrative2: Narrative
    ) -> Dict[str, Any]:
        """
        Enhanced conflict detection with geographic context
        
        Returns conflict details with regional information
        """
        session = get_session()
        
        try:
            # Get articles for each narrative
            articles1 = session.query(Article).filter(
                Article.narrative_id == narrative1.id
            ).all()
            
            articles2 = session.query(Article).filter(
                Article.narrative_id == narrative2.id
            ).all()
            
            # Classify regional dominance
            region1 = self._get_dominant_region(articles1)
            region2 = self._get_dominant_region(articles2)
            
            # Check for regional conflict
            is_regional_conflict = (
                region1 != region2 and
                region1 != "global" and
                region2 != "global"
            )
            
            conflict_data = {
                "is_regional_conflict": is_regional_conflict,
                "narrative1_region": region1,
                "narrative2_region": region2,
                "confidence_penalty": 0.3 if is_regional_conflict else 0.0,
                "explanation": ""
            }
            
            if is_regional_conflict:
                conflict_data["explanation"] = (
                    f"Regional conflict: {narrative1.name} ({region1.upper()}) "
                    f"vs {narrative2.name} ({region2.upper()}). "
                    f"Reducing confidence by 30% due to geographic information asymmetry."
                )
            
            return conflict_data
        
        finally:
            session.close()
    
    def get_transparency_report(self) -> str:
        """
        Generate detailed transparency report
        Shows exactly how we handle geographic bias
        """
        distribution = self.calculate_regional_distribution()
        
        report = f"""
🌍 GEOGRAPHIC BIAS TRANSPARENCY REPORT
{'=' * 60}

📊 Article Distribution (Last 30 Days):
   • India Sources:  {distribution['articles_by_region'].get('india', 0):4d} ({distribution['region_percentages'].get('india', 0):.1f}%)
   • US Sources:     {distribution['articles_by_region'].get('us', 0):4d} ({distribution['region_percentages'].get('us', 0):.1f}%)
   • China Sources:  {distribution['articles_by_region'].get('china', 0):4d} ({distribution['region_percentages'].get('china', 0):.1f}%)
   • Global Sources: {distribution['articles_by_region'].get('global', 0):4d} ({distribution['region_percentages'].get('global', 0):.1f}%)
   • Total:          {distribution['total_articles']:4d}

🎯 Unique Narratives by Region:
   • India:  {distribution['unique_narratives_by_region'].get('india', 0)}
   • US:     {distribution['unique_narratives_by_region'].get('us', 0)}
   • China:  {distribution['unique_narratives_by_region'].get('china', 0)}
   • Global: {distribution['unique_narratives_by_region'].get('global', 0)}

"""
        
        if distribution['bias_warning']:
            report += f"""
⚠️  BIAS WARNING: {distribution['bias_warning']}
   → Mitigation: Impact type weighting + cultural boosts + market size adjustment
   → Transparency: All narratives shown to user with regional context
   → Risk management: Reduced position size on regional conflicts

"""
        
        report += f"""
🎨 Adjustments Applied:
   • Cultural event boosts:   {self.bias_metrics['cultural_boosts_applied']}
   • Impact type boosts:      {self.bias_metrics['impact_type_boosts_applied']}
   • Market size adjustments: {self.bias_metrics['market_size_boosts_applied']}

💡 MITIGATION STRATEGIES:
   1. Supply disruptions → 1.8x weight (Peru strike > US sentiment)
   2. Cultural events → 1.3-1.5x boost during active months
   3. Consumer market → India (25% demand) gets 1.125x boost
   4. Regional conflicts → -30% confidence + -50% position size

⚖️  FUNDAMENTAL LIMITATION:
   We CANNOT fix US media volume dominance or English-only coverage.
   This is a structural reality. We acknowledge it and provide
   transparency + evidence-based adjustments rather than false precision.
"""
        
        return report
    
    def generate_adjustment_explanation(
        self,
        narrative: Narrative,
        base_strength: int,
        final_strength: int
    ) -> str:
        """
        Generate user-friendly explanation of adjustments
        """
        if final_strength == base_strength:
            return f"Strength: {final_strength}/100 (no geographic adjustments)"
        
        boost_pct = ((final_strength - base_strength) / base_strength) * 100
        
        explanation = [f"Strength: {base_strength} → {final_strength} (+{boost_pct:.0f}%)"]
        explanation.append("Adjustments:")
        
        # Cultural boost
        cultural_boost = self.apply_cultural_boost(narrative)
        if cultural_boost > 1.0:
            explanation.append(f"  • Cultural event boost: {cultural_boost}x")
        
        # Impact type
        impact_type = self.classify_narrative_impact_type(narrative)
        if self.IMPACT_TYPES[impact_type] > 1.0:
            explanation.append(f"  • High-impact type ({impact_type}): {self.IMPACT_TYPES[impact_type]}x")
        
        # Market size
        region = self._get_narrative_region(narrative)
        market_boost = self._calculate_market_size_boost(region)
        if market_boost > 1.0:
            explanation.append(f"  • Major consumer market ({region}): {market_boost:.2f}x")
        
        return "\n".join(explanation)


# Global instance
geo_bias_handler = GeographicBiasHandler()


if __name__ == "__main__":
    # Test the handler
    print("🧪 Testing Enhanced Geographic Bias Handler\n")
    
    # Generate transparency report
    report = geo_bias_handler.get_transparency_report()
    print(report)
    
    # Test with actual narratives
    session = get_session()
    narratives = session.query(Narrative).limit(5).all()
    
    if narratives:
        print("\n📈 Testing Narrative Adjustments:\n")
        for narrative in narratives:
            base_strength = narrative.strength
            adjusted_strength = geo_bias_handler.calculate_adjusted_strength(
                narrative,
                base_strength
            )
            
            if adjusted_strength != base_strength:
                explanation = geo_bias_handler.generate_adjustment_explanation(
                    narrative,
                    base_strength,
                    adjusted_strength
                )
                print(f"\n{explanation}\n")
    else:
        print("\n⚠️  No narratives in database for testing")
    
    session.close()
