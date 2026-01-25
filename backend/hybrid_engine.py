"""
Hybrid Intelligence Engine
Combines quantitative metrics (main branch) with multi-agent consensus (abhishek branch)
"""
from typing import Dict, Any, List
from datetime import datetime, timedelta

from database import get_session, Narrative, Article
from narrative.lifecycle_tracker import lifecycle_tracker
from agent.trading_agent import trading_agent
from multi_agent.orchestrator import multi_agent_orchestrator
from config import config


class HybridEngine:
    """
    Hybrid analysis engine combining metrics-based and AI-based approaches
    """
    
    def __init__(self):
        self.lifecycle_tracker = lifecycle_tracker
        self.trading_agent = trading_agent
        self.multi_agent = multi_agent_orchestrator
    
    async def analyze_narrative_hybrid(self, narrative_id: int) -> Dict[str, Any]:
        """
        Hybrid analysis combining both approaches:
        1. Calculate quantitative metrics (velocity, correlation, strength)
        2. Run multi-agent consensus analysis
        3. Combine results with confidence weighting
        4. Generate comprehensive explanation
        
        Args:
            narrative_id: ID of narrative to analyze
        
        Returns:
            Dict with comprehensive analysis results
        """
        print(f"🔬 Hybrid analysis for narrative {narrative_id}")
        
        session = get_session()
        
        try:
            narrative = session.query(Narrative).get(narrative_id)
            
            if not narrative:
                raise ValueError(f"Narrative {narrative_id} not found")
            
            # Step 1: Quantitative metrics (main branch approach)
            print("   📊 Calculating quantitative metrics...")
            metrics = self.lifecycle_tracker.calculate_metrics(narrative)
            strength_metrics = self.lifecycle_tracker.calculate_narrative_strength(narrative)
            deterministic_phase = self.lifecycle_tracker.detect_phase_transition(narrative)
            
            # Step 2: Multi-agent analysis (abhishek branch approach)
            print("   🤖 Running multi-agent consensus...")
            evidence = self._gather_evidence(narrative, session)
            agent_result = await self.multi_agent.analyze_narrative_multi({
                "narrative_id": narrative_id,
                "narrative_title": narrative.name,
                "historical_volume_75pct": metrics.get("velocity_increase", 0) * 100,
                "recent_peak_volume": metrics.get("current_velocity", 0) * 100,
                "evidence": evidence
            })
            
            # Step 3: Combine with confidence weighting
            print("   ⚖️  Combining results...")
            
            # Get config values (with defaults if not defined yet)
            agent_weight = getattr(config, 'hybrid', None)
            if agent_weight and hasattr(agent_weight, 'agent_weight'):
                agent_w = agent_weight.agent_weight
                metrics_w = agent_weight.metrics_weight
                high_threshold = agent_weight.high_confidence_threshold
            else:
                agent_w = 0.6
                metrics_w = 0.4
                high_threshold = 0.75
            
            if agent_result["overall_confidence"] >= high_threshold:
                # High agent confidence - trust agents
                final_phase = agent_result["consensus_lifecycle_phase"]
                final_confidence = agent_result["overall_confidence"]
                analysis_method = "multi-agent"
            else:
                # Low agent confidence - use deterministic metrics
                final_phase = deterministic_phase or narrative.phase
                final_confidence = 0.65
                analysis_method = "metrics-fallback"
            
            # Weighted strength score
            agent_strength = agent_result["consensus_strength_score"]
            final_strength = int(
                agent_w * agent_strength +
                metrics_w * strength_metrics
            )
            
            # Step 4: Generate explanation
            explanation = self._generate_hybrid_explanation(
                metrics, agent_result, final_phase, final_confidence
            )
            
            result = {
                "narrative_id": narrative_id,
                "consensus_lifecycle_phase": final_phase,
                "consensus_strength_score": final_strength,
                "overall_confidence": final_confidence,
                "num_agents": agent_result.get("num_agents", 5),
                "analysis_method": analysis_method,
                "agent_votes": agent_result["agent_votes"],
                "minority_opinions": agent_result.get("minority_opinions", []),
                "metrics": metrics,
                "explanation": explanation,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Step 5: Persist results to database
            narrative.strength = final_strength
            narrative.phase = final_phase
            narrative.mention_velocity = metrics.get("current_velocity", 0)
            narrative.price_correlation = metrics.get("price_correlation", 0)
            session.commit()
            
            print(f"   ✅ Hybrid analysis complete and saved: {final_phase} (strength: {final_strength})")
            
            return result
        
        finally:
            session.close()
    
    def _gather_evidence(self, narrative: Narrative, session) -> List[Dict[str, Any]]:
        """Gather evidence for multi-agent analysis"""
        articles = session.query(Article).filter(
            Article.narrative_id == narrative.id
        ).order_by(Article.published_at.desc()).limit(20).all()
        
        evidence = []
        for article in articles:
            evidence.append({
                "source_id": f"article_{article.id}",
                "source_type": article.source,
                "timestamp": article.published_at.isoformat(),
                "text": f"{article.title}. {article.content or ''}",
                "author_reputation_score": 0.8,
                "mention_count": 1,
                "price_impact_correlation": narrative.price_correlation or 0.5
            })
        
        return evidence
    
    def _generate_hybrid_explanation(
        self,
        metrics: Dict[str, Any],
        agent_result: Dict[str, Any],
        final_phase: str,
        final_confidence: float
    ) -> str:
        """Generate human-readable explanation of hybrid decision"""
        
        # Metrics summary
        metrics_summary = f"Velocity: {metrics.get('current_velocity', 0):.2f}/hr"
        if metrics.get('velocity_increase', 0) > 0:
            metrics_summary += f" (+{metrics['velocity_increase']:.1%})"
        
        metrics_summary += f", Correlation: {metrics.get('price_correlation', 0):.2f}"
        
        # Agent summary
        agent_phases = [v['phase_vote'] for v in agent_result['agent_votes']]
        phase_counts = {}
        for p in agent_phases:
            phase_counts[p] = phase_counts.get(p, 0) + 1
        
        agent_summary = f"{agent_result['num_agents']} agents analyzed: "
        agent_summary += ", ".join([f"{count}x {phase}" for phase, count in phase_counts.items()])
        
        # Build explanation
        explanation = f"""
**Decision**: {final_phase.upper()} phase (confidence: {final_confidence:.0%})

**Quantitative Metrics**: {metrics_summary}

**Multi-Agent Consensus**: {agent_summary}

**Analysis Method**: {'AI consensus (high confidence)' if final_confidence > 0.75 else 'Metrics fallback (low agent agreement)'}
"""
        
        # Add minority opinions if present
        if agent_result.get('minority_opinions'):
            explanation += f"\n\n**Minority Opinions**: {len(agent_result['minority_opinions'])} agents dissented"
        
        return explanation.strip()


# Global instance
hybrid_engine = HybridEngine()
