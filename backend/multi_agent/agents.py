"""
Specialized Agent Implementations
Each agent has a unique perspective on narrative analysis
"""
from typing import Dict, Any, List
from dataclasses import dataclass
from pathlib import Path


@dataclass
class AgentVoteResult:
    """Result of an individual agent's vote"""
    agent_name: str
    phase_vote: str  # birth, growth, peak, reversal, death
    strength_vote: int  # 0-100
    confidence: float  # 0.0-1.0
    reasoning: str


class BaseAnalyst:
    """Base class for all analysts"""
    
    def __init__(self, name: str, specialty: str):
        self.name = name
        self.specialty = specialty
        self.system_prompt = self._load_system_prompt()
    
    def _load_system_prompt(self) -> str:
        """Load system prompt from file"""
        prompt_file = Path(__file__).parent / "prompts" / "system.txt"
        if prompt_file.exists():
            return prompt_file.read_text()
        return f"You are a {self.specialty} analyzing silver market narratives."
    
    def get_perspective_prompt(self) -> str:
        """Get agent-specific perspective to add to prompts"""
        return f"As a {self.specialty}, focus on {self._get_focus_areas()}."
    
    def _get_focus_areas(self) -> str:
        """Override in subclasses"""
        return "relevant factors"
    
    async def analyze(
        self,
        narrative_data: Dict[str, Any],
        orchestrator_call_llm
    ) -> AgentVoteResult:
        """
        Analyze narrative and return vote
        
        Args:
            narrative_data: Dict with narrative info and evidence
            orchestrator_call_llm: Function to call LLM (from orchestrator)
        
        Returns:
            AgentVoteResult with phase, strength, confidence
        """
        # Build analysis prompt
        prompt = self._build_analysis_prompt(narrative_data)
        
        # Call LLM through orchestrator
        response = await orchestrator_call_llm(
            prompt=prompt,
            system=self.system_prompt + "\n\n" + self.get_perspective_prompt(),
            temperature=0.3
        )
        
        # Parse response
        return self._parse_response(response)
    
    def _build_analysis_prompt(self, narrative_data: Dict[str, Any]) -> str:
        """Build prompt for analysis"""
        evidence_text = "\n".join([
            f"- [{e['source_type']}] {e['text'][:200]}... (correlation: {e.get('price_impact_correlation', 0):.2f})"
            for e in narrative_data.get('evidence', [])[:10]
        ])
        
        return f"""Analyze this silver market narrative from your {self.specialty} perspective:

**Narrative**: {narrative_data.get('narrative_title', 'Unknown')}
**Historical Volume (75th percentile)**: {narrative_data.get('historical_volume_75pct', 0):.1f}%
**Recent Peak Volume**: {narrative_data.get('recent_peak_volume', 0):.1f}

**Evidence**:
{evidence_text or 'No evidence provided'}

**Your Task**:
1. Determine lifecycle phase: birth, growth, peak, reversal, or death
2. Rate strength (0-100): How impactful is this narrative right now? Consider the volume of evidence and price potential.
3. Provide confidence (0-100): How certain are you about this analysis?
4. Explain your reasoning briefly (2-3 sentences). Be specific about the evidence.

**Response Format** (strictly follow this):
PHASE: [phase]
STRENGTH: [0-100]
CONFIDENCE: [0-100]
REASONING: [your reasoning]
"""
    
    def _parse_response(self, response: str) -> AgentVoteResult:
        """Parse LLM response into AgentVoteResult"""
        lines = response.strip().split('\n')
        
        phase = "growth"  # default
        strength = 50
        confidence = 0.5
        reasoning = "Unable to parse response"
        
        for line in lines:
            line = line.strip()
            upper_line = line.upper()
            
            if "PHASE:" in upper_line:
                phase = line.split(":", 1)[1].strip().lower().replace("*", "").replace(".", "")
            elif "STRENGTH:" in upper_line:
                try:
                    strength_str = "".join(filter(str.isdigit, line.split(":", 1)[1]))
                    strength = int(strength_str) if strength_str else 50
                except:
                    strength = 50
            elif "CONFIDENCE:" in upper_line:
                try:
                    conf_str = "".join(filter(str.isdigit, line.split(":", 1)[1]))
                    if conf_str:
                        conf_val = int(conf_str)
                        # Handle both 0-1 and 0-100 formats
                        confidence = conf_val / 100.0 if conf_val > 1 else conf_val
                    else:
                        confidence = 0.5
                except:
                    confidence = 0.5
            elif "REASONING:" in upper_line:
                reasoning = line.split(":", 1)[1].strip().replace("*", "")
        
        # If reasoning is still default, try to find any non-tag line at the end
        if reasoning == "Unable to parse response" and len(lines) > 0:
            for line in reversed(lines):
                if ":" not in line and len(line.strip()) > 20:
                    reasoning = line.strip()
                    break

        return AgentVoteResult(
            agent_name=self.name,
            phase_vote=phase,
            strength_vote=max(0, min(100, strength)),
            confidence=max(0.0, min(1.0, confidence)),
            reasoning=reasoning
        )


class FundamentalAnalyst(BaseAnalyst):
    """Analyzes supply/demand fundamentals"""
    
    def __init__(self):
        super().__init__(
            name="fundamental",
            specialty="Fundamental Analyst"
        )
    
    def _get_focus_areas(self) -> str:
        return "industrial demand (solar, EVs, electronics), supply dynamics, inventory levels, and real-world utility"


class SentimentAnalyst(BaseAnalyst):
    """Analyzes market sentiment and social signals"""
    
    def __init__(self):
        super().__init__(
            name="sentiment",
            specialty="Sentiment Analyst"
        )
    
    def _get_focus_areas(self) -> str:
        return "social media trends, news sentiment, retail investor behavior, and fear/greed indicators"


class TechnicalAnalyst(BaseAnalyst):
    """Analyzes price patterns and momentum"""
    
    def __init__(self):
        super().__init__(
            name="technical",
            specialty="Technical Analyst"
        )
    
    def _get_focus_areas(self) -> str:
        return "price correlation with narrative timing, momentum, volume patterns, and historical price behavior"


class RiskAnalyst(BaseAnalyst):
    """Assesses risks and downside scenarios"""
    
    def __init__(self):
        super().__init__(
            name="risk",
            specialty="Risk Analyst"
        )
    
    def _get_focus_areas(self) -> str:
        return "contradicting evidence, false signals, potential for narrative collapse, and downside risks"


class MacroAnalyst(BaseAnalyst):
    """Analyzes macroeconomic factors"""
    
    def __init__(self):
        super().__init__(
            name="macro",
            specialty="Macro Analyst"
        )
    
    def _get_focus_areas(self) -> str:
        return "Federal Reserve policy, inflation trends, dollar strength, geopolitical factors, and economic cycles"
