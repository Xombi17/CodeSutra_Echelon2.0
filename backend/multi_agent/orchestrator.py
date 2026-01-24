"""
Multi-Agent Orchestrator
Coordinates 5 specialized agents for consensus-based narrative analysis
"""
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
from collections import Counter

from .agents import (
    FundamentalAnalyst,
    SentimentAnalyst,
    TechnicalAnalyst,
    RiskAnalyst,
    MacroAnalyst,
    AgentVoteResult
)
from orchestrator import orchestrator as llm_orchestrator


class MultiAgentOrchestrator:
    """
    Orchestrates multi-agent debate for narrative analysis
    """
    
    def __init__(self):
        self.agents = {
            "fundamental": FundamentalAnalyst(),
            "sentiment": SentimentAnalyst(),
            "technical": TechnicalAnalyst(),
            "risk": RiskAnalyst(),
            "macro": MacroAnalyst()
        }
        self.debate_history = []
    
    async def analyze_narrative_multi(self, narrative_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run multi-agent consensus analysis
        
        Args:
            narrative_data: Dict with narrative_id, title, volume data, evidence
        
        Returns:
            Dict with consensus results and agent votes
        """
        print(f"🤖 Multi-agent analysis starting for: {narrative_data.get('narrative_title', 'Unknown')}")
        
        # Round 1: Independent analysis
        round1_votes = await self._round_1_analysis(narrative_data)
        
        # Check consensus level
        consensus_level = self._calculate_consensus(round1_votes)
        
        print(f"   Round 1 consensus: {consensus_level:.1%}")
        
        # Round 2: Debate if consensus < 60%
        if consensus_level < 0.6:
            print("   Consensus low - initiating debate round...")
            round2_votes = await self._round_2_debate(round1_votes, narrative_data)
            final_votes = round2_votes
        else:
            final_votes = round1_votes
        
        # Synthesize results
        result = self._synthesize_consensus(final_votes)
        
        print(f"   ✅ Consensus achieved: {result['consensus_lifecycle_phase']} (confidence: {result['overall_confidence']:.2f})")
        
        return result
    
    async def _round_1_analysis(self, narrative_data: Dict[str, Any]) -> List[AgentVoteResult]:
        """Round 1: Each agent analyzes independently"""
        
        # Create tasks for parallel execution
        tasks = []
        for agent_name, agent in self.agents.items():
            task = agent.analyze(narrative_data, self._call_llm)
            tasks.append(task)
        
        # Run all agents in parallel
        votes = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out any exceptions
        valid_votes = []
        for vote in votes:
            if isinstance(vote, AgentVoteResult):
                valid_votes.append(vote)
            elif isinstance(vote, Exception):
                print(f"   ⚠️ Agent error: {vote}")
        
        return valid_votes
    
    async def _round_2_debate(
        self,
        round1_votes: List[AgentVoteResult],
        narrative_data: Dict[str, Any]
    ) -> List[AgentVoteResult]:
        """Round 2: Agents see others' votes and can adjust"""
        
        # Build debate context
        debate_context = self._build_debate_context(round1_votes)
        
        # Add debate context to narrative data
        narrative_data_with_debate = {
            **narrative_data,
            "previous_round_votes": debate_context
        }
        
        # Each agent analyzes again with knowledge of others' views
        tasks = []
        for agent_name, agent in self.agents.items():
            # Find this agent's previous vote
            prev_vote = next((v for v in round1_votes if v.agent_name == agent_name), None)
            
            # Build debate prompt
            debate_prompt = f"""
Previous round votes:
{debate_context}

Your previous vote: {prev_vote.phase_vote if prev_vote else 'N/A'} (strength: {prev_vote.strength_vote if prev_vote else 'N/A'})

After seeing other agents' perspectives, reconsider your analysis.
You may change your vote if you find their arguments compelling, or defend your original position.
"""
            
            # Add debate context to the analysis
            task = agent.analyze({
                **narrative_data,
                "debate_context": debate_prompt
            }, self._call_llm)
            tasks.append(task)
        
        # Run debate round in parallel
        votes = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter valid votes
        valid_votes = [v for v in votes if isinstance(v, AgentVoteResult)]
        
        return valid_votes
    
    def _build_debate_context(self, votes: List[AgentVoteResult]) -> str:
        """Build summary of votes for debate"""
        context_lines = []
        for vote in votes:
            context_lines.append(
                f"- {vote.agent_name}: {vote.phase_vote} (strength: {vote.strength_vote}, "
                f"confidence: {vote.confidence:.0%}) - {vote.reasoning[:100]}"
            )
        return "\n".join(context_lines)
    
    def _calculate_consensus(self, votes: List[AgentVoteResult]) -> float:
        """Calculate consensus level (0.0 to 1.0)"""
        if not votes:
            return 0.0
        
        # Count phase votes
        phase_votes = [v.phase_vote for v in votes]
        phase_counter = Counter(phase_votes)
        most_common_count = phase_counter.most_common(1)[0][1]
        
        # Consensus is fraction agreeing on most common phase
        return most_common_count / len(votes)
    
    def _synthesize_consensus(self, votes: List[AgentVoteResult]) -> Dict[str, Any]:
        """Synthesize final consensus from all votes"""
        
        if not votes:
            return {
                "consensus_lifecycle_phase": "growth",
                "consensus_strength_score": 50,
                "overall_confidence": 0.5,
                "agent_votes": [],
                "minority_opinions": []
            }
        
        # Determine consensus phase (weighted by confidence)
        phase_weights = {}
        for vote in votes:
            phase = vote.phase_vote
            weight = vote.confidence
            phase_weights[phase] = phase_weights.get(phase, 0) + weight
        
        consensus_phase = max(phase_weights.items(), key=lambda x: x[1])[0]
        
        # Calculate weighted average strength
        total_weight = sum(v.confidence for v in votes)
        weighted_strength = sum(v.strength_vote * v.confidence for v in votes) / total_weight if total_weight > 0 else 50
        
        # Calculate overall confidence (average of all agents' confidence)
        overall_confidence = sum(v.confidence for v in votes) / len(votes)
        
        # Identify minority opinions (agents who disagree with consensus)
        minority_opinions = []
        for vote in votes:
            if vote.phase_vote != consensus_phase:
                minority_opinions.append({
                    "agent": vote.agent_name,
                    "phase": vote.phase_vote,
                    "strength": vote.strength_vote,
                    "reasoning": vote.reasoning
                })
        
        # Build agent votes summary
        agent_votes = []
        for vote in votes:
            agent_votes.append({
                "agent_name": vote.agent_name,
                "phase_vote": vote.phase_vote,
                "strength_vote": vote.strength_vote,
                "confidence": vote.confidence,
                "reasoning": vote.reasoning
            })
        
        return {
            "consensus_lifecycle_phase": consensus_phase,
            "consensus_strength_score": int(weighted_strength),
            "overall_confidence": overall_confidence,
            "agent_votes": agent_votes,
            "minority_opinions": minority_opinions,
            "num_agents": len(votes),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _call_llm(
        self,
        prompt: str,
        system: str,
        temperature: float = 0.3
    ) -> str:
        """
        Call LLM through existing orchestrator
        
        Args:
            prompt: User prompt
            system: System prompt
            temperature: Generation temperature
        
        Returns:
            LLM response text
        """
        try:
            response = await llm_orchestrator.generate_text(
                prompt=prompt,
                system_prompt=system,
                temperature=temperature,
                max_tokens=500
            )
            return response.content
        except Exception as e:
            print(f"   ⚠️ LLM call failed: {e}")
            return "ERROR: Unable to get LLM response"


# Global instance
multi_agent_orchestrator = MultiAgentOrchestrator()
