# Demo Data for Hybrid Multi-Agent System

This directory contains sample narrative data for testing the multi-agent debate system.

## Files

- **solar_demand.json** - Solar panel manufacturing driving silver demand (Growth phase, high confidence)
- **silver_squeeze.json** - Reddit-driven silver squeeze movement (Peak phase, medium confidence)
- **ev_demand.json** - Electric vehicle production boosting silver (Birth/Growth phase, high confidence)

## Usage

### Test Multi-Agent Analysis

```bash
curl -X POST http://localhost:8000/api/narratives/analyze-multi-agent \
  -H "Content-Type: application/json" \
  -d @demo_data/solar_demand.json
```

### Test with Different Narratives

```bash
# Solar demand narrative
curl -X POST http://localhost:8000/api/narratives/analyze-multi-agent \
  -H "Content-Type: application/json" \
  -d @demo_data/solar_demand.json | jq '.data.consensus_lifecycle_phase'

# Silver squeeze narrative
curl -X POST http://localhost:8000/api/narratives/analyze-multi-agent \
  -H "Content-Type: application/json" \
  -d @demo_data/silver_squeeze.json | jq '.data.consensus_lifecycle_phase'

# EV demand narrative
curl -X POST http://localhost:8000/api/narratives/analyze-multi-agent \
  -H "Content-Type: application/json" \
  -d @demo_data/ev_demand.json | jq '.data.consensus_lifecycle_phase'
```

## Expected Results

### Solar Demand
- **Phase**: Growth or Peak
- **Strength**: 75-85
- **Confidence**: High (0.8+)
- **Consensus**: Strong agreement among agents
- **Reasoning**: Industrial demand, high correlation, strong fundamentals

### Silver Squeeze
- **Phase**: Peak or Reversal
- **Strength**: 60-75
- **Confidence**: Medium (0.6-0.75)
- **Consensus**: Moderate agreement, risk analyst likely dissents
- **Reasoning**: High social volume but lower price correlation, sentiment-driven

### EV Demand
- **Phase**: Growth
- **Strength**: 70-80
- **Confidence**: High (0.75+)
- **Consensus**: Strong agreement
- **Reasoning**: Long-term structural demand, strong fundamentals

## Notes

- Evidence quality and source reputation affect agent confidence
- Price correlation is a key factor in phase determination
- Volume trends influence growth vs. peak classification
