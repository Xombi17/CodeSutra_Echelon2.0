# Architecture: Hybrid Intelligence System

## Overview

SilverSentinel combines traditional quantitative metrics with a novel multi-agent AI consensus system to provide superior market intelligence for silver trading.

```
┌─────────────────────────────────────────────────────────────┐
│              HYBRID INTELLIGENCE ENGINE                      │
├──────────────────────────┬──────────────────────────────────┤
│   Quantitative Layer     │    Multi-Agent AI Layer          │
│   (Main Branch)          │    (New Feature)                 │
├──────────────────────────┼──────────────────────────────────┤
│ • Velocity Analysis      │ • Fundamental Analyst            │
│ • Price Correlation      │ • Sentiment Analyst              │
│ • Strength Scoring       │ • Technical Analyst              │
│ • Conflict Detection     │ • Risk Analyst                   │
│                          │ • Macro Analyst                  │
└──────────────────────────┴──────────────────────────────────┘
                          ↓
               Confidence-Based Weighting
                          ↓
                  Final Decision Output
        (Phase, Strength, Confidence, Reasoning)
```

## System Components

### 1. Quantitative Metrics Layer

**Location**: `backend/narrative/lifecycle_tracker.py`

Calculates deterministic metrics based on historical data:

- **Velocity Analysis**: Measures rate of narrative spread
  - Current velocity (mentions/hour)
  - Velocity increase ratio (24h vs 48h)
  
- **Price Correlation**: Correlation between narrative activity and silver price movements
  
- **Strength Scoring**: Multi-factor score (0-100)
  - Social velocity: 30%
  - News intensity: 25%
  - Price correlation: 25%
  - Institutional alignment: 20%

- **Conflict Detection**: Enhanced algorithm to avoid false positives
  - Sentiment opposition check
  - Volume ratio validation (avoid 10 vs 1000 mismatches)
  - Strength threshold (both > 60)
  - Temporal relevance (both active in last 3 days)

### 2. Multi-Agent AI Layer

**Location**: `backend/multi_agent/`

Five specialized agents debate narrative lifecycle:

#### Agent Roles

1. **Fundamental Analyst** (`agents.py`)
   - Focus: Supply/demand, industrial usage, fundamentals
   - Strengths: Long-term structural trends
   
2. **Sentiment Analyst** (`agents.py`)
   - Focus: Social media, retail behavior, market psychology
   - Strengths: Short-term momentum detection
   
3. **Technical Analyst** (`agents.py`)
   - Focus: Price patterns, momentum, volume
   - Strengths: Timing and correlation analysis
   
4. **Risk Analyst** (`agents.py`)
   - Focus: Downside scenarios, false signals, contradictions
   - Strengths: Avoiding false positives
   
5. **Macro Analyst** (`agents.py`)
   - Focus: Fed policy, inflation, geopolitics, economic cycles
   - Strengths: Market context and regime analysis

#### Debate Process

**Round 1**: Independent Analysis
- Each agent analyzes evidence independently
- Votes on: phase, strength (0-100), confidence (0-1)
- Provides reasoning

**Consensus Check**:
- Calculate agreement level
- If consensus ≥ 60%: Accept results
- If consensus < 60%: Proceed to Round 2

**Round 2**: Debate (if needed)
- Agents see each other's votes
- Can adjust their position or defend original view
- Maximum 3 debate rounds

**Synthesis**:
- Weighted by confidence scores
- Consensus phase = highest weighted vote
- Consensus strength = weighted average
- Minority opinions preserved for transparency

### 3. Hybrid Engine

**Location**: `backend/hybrid_engine.py`

Intelligently combines both approaches:

#### Decision Flow

```python
def analyze_narrative_hybrid(narrative_id):
    # 1. Calculate quantitative metrics (always runs)
    metrics = lifecycle_tracker.calculate_metrics(narrative)
    deterministic_phase = lifecycle_tracker.detect_phase_transition(narrative)
    
    # 2. Run multi-agent consensus (parallel)
    agent_result = multi_agent.analyze_narrative_multi(evidence)
    
    # 3. Confidence-based weighting
    if agent_confidence >= 0.75:
        # Trust agents (high confidence)
        final_phase = agent_result.phase
        final_confidence = agent_result.confidence
        method = "multi-agent"
    else:
        # Use metrics fallback (low agent agreement)
        final_phase = deterministic_phase
        final_confidence = 0.65
        method = "metrics-fallback"
    
    # 4. Weighted strength score
    final_strength = (0.6 * agent_strength) + (0.4 * metrics_strength)
    
    return comprehensive_analysis
```

#### Configuration

Weights are configurable in `backend/config.py`:

```python
class HybridConfig:
    agent_weight: float = 0.6           # 60% weight on agents
    metrics_weight: float = 0.4         # 40% weight on metrics
    high_confidence_threshold: float = 0.75
```

### 4. API Endpoints

**New Endpoints** (added to `backend/main.py`):

1. **POST `/api/narratives/{id}/analyze-hybrid`**
   - Hybrid analysis for existing narrative
   - Returns: phase, strength, confidence, agent votes, metrics, explanation

2. **POST `/api/narratives/analyze-multi-agent`**
   - Pure multi-agent analysis on provided data
   - Input: narrative data + evidence
   - Returns: consensus, individual votes, minority opinions

3. **GET `/api/trading-signal-enhanced`**
   - Trading signal with agent insights
   - Returns: traditional signal + agent consensus + hybrid analysis

4. **GET `/api/narratives/{id}/agent-history`**
   - Historical agent votes for a narrative
   - Tracks evolution of agent opinions over time

### 5. Database Models

**New Tables** (added to `backend/database.py`):

```python
class AgentVote(Base):
    """Store individual agent votes"""
    narrative_id: int
    agent_name: str  # "fundamental", "sentiment", etc.
    phase_vote: str
    strength_vote: int
    confidence: float
    reasoning: str
    timestamp: datetime
    debate_round: int

class NarrativeSnapshot(Base):
    """Track narrative evolution"""
    narrative_id: int
    phase: str
    strength: int
    velocity: float
    price_correlation: float
    analysis_method: str  # "metrics", "multi-agent", "hybrid"
    confidence: float
    agent_consensus_data: JSON
    timestamp: datetime
```

## Benefits Over Pure Approaches

### vs. Pure Metrics (Main Branch)

✅ **Handles qualitative factors** (sentiment, fundamentals)  
✅ **Adapts to new market dynamics** (learns from patterns)  
✅ **Provides reasoning** (not just numbers)  
✅ **Captures minority views** (risk awareness)

### vs. Pure AI (Single Agent)

✅ **Multiple perspectives** (avoid single-agent bias)  
✅ **Fallback to metrics** (reliability when consensus low)  
✅ **Quantitative grounding** (not purely subjective)  
✅ **Conflict detection** (deterministic checks still run)

## Performance Characteristics

### Latency

- **Metrics Only**: ~50ms (database queries + calculations)
- **Multi-Agent**: ~2-5s (5 LLM calls in parallel)
- **Hybrid**: ~2-5s (parallel execution)

### Accuracy (Expected)

- **Metrics**: Reliable for well-defined patterns
- **Multi-Agent**: Better for novel situations
- **Hybrid**: Best of both worlds (75%+ accuracy target)

### Cost

- **Metrics**: Free (computational only)
- **Multi-Agent**: ~$0.002 per analysis (5 agents × $0.0004/call)
- **Hybrid**: Same as multi-agent (metrics run in parallel)

## Usage Examples

### 1. Analyze Existing Narrative

```python
# Hybrid analysis
result = await hybrid_engine.analyze_narrative_hybrid(narrative_id=123)

print(result["phase"])              # "growth"
print(result["strength"])           # 78
print(result["confidence"])         # 0.85
print(result["analysis_method"])    # "multi-agent"
print(result["explanation"])        # Human-readable reasoning
```

### 2. Pure Multi-Agent Analysis

```python
# Prepare data
data = {
    "narrative_title": "Solar Demand Surge",
    "historical_volume_75pct": 65.0,
    "recent_peak_volume": 120.0,
    "evidence": [...]
}

# Run analysis
result = await multi_agent_orchestrator.analyze_narrative_multi(data)

print(result["consensus_lifecycle_phase"])  # "growth"
print(result["agent_votes"])                # List of all agent votes
print(result["minority_opinions"])          # Dissenting views
```

### 3. Enhanced Trading Signal

```python
# Get signal with agent insights
signal = await trading_agent.generate_signal()
enhanced = await hybrid_engine.enhance_signal(signal)

print(enhanced["action"])                    # "BUY"
print(enhanced["agent_insights"]["consensus"])  # Agent votes
print(enhanced["hybrid_analysis"]["metrics"])   # Quantitative data
```

## Future Enhancements

### Phase 2 Features (Not Yet Implemented)

1. **Agent Learning**
   - Track agent accuracy over time
   - Adjust confidence weights based on performance
   
2. **Custom Agent Training**
   - Fine-tune agents on silver-specific data
   - Domain-specific prompts for each agent

3. **Real-time WebSocket Updates**
   - Stream agent debates to frontend
   - Live consensus formation visualization

4. **Historical Backtesting**
   - Compare hybrid vs. pure approaches
   - Optimize confidence thresholds

## Testing

Run hybrid system tests:

```bash
cd backend
pytest tests/test_hybrid.py -v
```

Run demo with sample data:

```bash
./demo_hybrid.sh
```

## Configuration

Edit `backend/config.py` to tune hybrid system:

```python
@dataclass
class HybridConfig:
    agent_weight: float = 0.6              # Increase to trust agents more
    metrics_weight: float = 0.4            # Increase to trust metrics more
    high_confidence_threshold: float = 0.75  # Lower to use agents more often
    cache_agent_results: bool = True       # Enable caching for performance
    cache_ttl_minutes: int = 15            # Cache duration
```

## Monitoring

Key metrics to track:

1. **Consensus Rate**: % of analyses where agents agree (target: 70%+)
2. **Confidence Distribution**: Track high vs. low confidence analyses
3. **Method Usage**: multi-agent vs. metrics-fallback ratio
4. **Agent Agreement**: Which agents agree/disagree most often
5. **Accuracy**: Track predictions vs. actual outcomes

---

**Version**: 1.0.0  
**Last Updated**: 2024-01-24  
**Status**: MVP Complete
