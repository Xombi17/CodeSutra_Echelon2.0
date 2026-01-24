# SilverSentinel - Implementation Plan

## Executive Summary

**SilverSentinel** is an autonomous AI-driven silver market intelligence and trading platform that revolutionizes commodity trading through narrative-aware decision making. The system implements three advanced problem statements:

- **PS 4**: Autonomous Resource Management - Self-optimizing data collection
- **PS 5**: Unsupervised Pattern Discovery - Zero-config narrative detection
- **PS 6**: Sentiment Lifecycle Tracking - Predictive phase transition detection

The platform uses multi-model orchestration (Groq, Ollama, HuggingFace) with intelligent fallback to ensure 99.9% uptime and zero rate-limit failures.

### Core Features (Priority Order)

1. **Autonomous Narrative Intelligence Engine** - Continuously monitors markets, detects emerging narratives
2. **Predictive Trading Agent** - Buy/sell signals with explainable AI reasoning
3. **Multi-Dimensional Market Analysis** - Cross-narrative conflict detection and resolution
4. **Portfolio Intelligence** - Real-time strategy recommendations
5. **Historical Pattern Matching** - "This narrative pattern led to +12% gains in Nov 2024"
6. **Bonus: Physical Silver Scanner** - CV-based instant valuation with market context

---

## Advanced Features (What Makes SilverSentinel Unique)

### 1. **Predictive Narrative Forecasting**
Not just tracking current narratives - predicting which narratives will emerge next.

**How it works**:
- Analyzes historical patterns: "Mining strike narrative → Supply shortage narrative (7 days later)"
- Tracks precursor signals: "Reddit mentions of 'Peru' +200% → Mining strike narrative likely in 48h"
- Assigns probability scores: "65% chance 'Industrial Shortage' narrative emerges this week"

**User Value**: Get ahead of the market by 2-5 days

---

### 2. **Smart Alert System with Context**
Intelligent notifications that explain WHY you're being alerted.

**Alert Types**:
```
🔥 URGENT: "Mining Strike" narrative entered REVERSAL phase
   → Your position: LONG 50g silver
   → Recommendation: Exit 70% within 24h
   → Reason: Conflicting "Trade Agreement" narrative gaining strength
   → Historical precedent: Similar pattern in June 2023 led to -8% drop
```

**Filters**:
- Only alert on narratives affecting YOUR portfolio
- Suppress low-confidence signals during low-volatility periods
- Escalation: Email → SMS → Phone call for critical events

---

### 3. **Portfolio-Aware Intelligence**
The agent knows what silver you own and personalizes recommendations.

**Features**:
- Track physical holdings (via scanner) + paper positions
- Calculate narrative exposure: "40% of your portfolio is vulnerable to 'Fed Rate' narrative"
- Diversification suggestions: "Consider hedging with gold ETF due to conflict risk"
- Tax optimization: "Sell Coin A (short-term loss) before Jewelry B (long-term gain)"

**Dashboard View**:
```
Your Portfolio: 150g silver (₹45,000)
├─ 75g Physical (via scanner)
├─ 75g Paper (ETF)

Narrative Exposure:
├─ "Wedding Demand" +₹2,250 (Growth phase) ✅
├─ "Fed Rates" -₹1,800 (Peak phase) ⚠️
└─ Net: +₹450 (+1% expected 30-day return)
```

---

### 4. **Historical Pattern Matching Engine**
Every narrative is matched against historical precedents.

**Example Output**:
```
Current Narrative: "Peru Mining Strike"
Phase: Growth (Day 5)

📚 Historical Matches:
1. Colombia Strike (Mar 2023) - 89% similarity
   ├─ Duration: 18 days
   ├─ Peak price impact: +12%
   └─ Exit signal appeared: Day 14

2. Chile Protest (Nov 2022) - 76% similarity
   ├─ Duration: 9 days (resolved quickly)
   ├─ Peak price impact: +6%
   └─ False alarm - prices returned to baseline

Recommendation: Hold until Day 12-14, monitor for resolution signals
```

---

### 5. **Multi-Commodity Narrative Correlation**
Silver doesn't exist in isolation - tracks gold, copper, oil narratives.

**Cross-Market Intelligence**:
- "Gold 'Safe Haven' narrative strengthening → Silver likely follows in 48-72h"
- "Copper 'Industrial Slowdown' narrative → Silver solar demand may weaken"
- "Oil 'Geopolitical Risk' narrative → Inflation hedge narratives for silver incoming"

**Correlation Dashboard**:
```
Gold:   ████████░░ 0.82 correlation (Strong)
Copper: ████░░░░░░ 0.45 correlation (Moderate)
USD:    ██░░░░░░░░ -0.65 correlation (Inverse Strong)
```

---

### 6. **API Marketplace for Third-Party Integration**
Developers can build on top of SilverSentinel's intelligence.

**API Endpoints**:
```python
GET /api/v1/narratives/current
GET /api/v1/narratives/{id}/forecast
GET /api/v1/trading-signals/explained
POST /api/v1/portfolio/analyze
WebSocket /ws/live-narratives
```

**Use Cases**:
- Jewelry store POS systems auto-adjust prices based on narratives
- Trading bots execute on SilverSentinel signals
- News aggregators embed narrative timelines

---

### 7. **Narrative Genealogy Tracking**
Visualize how narratives spawn sub-narratives or merge.

**Example Flow**:
```
"EV Sales Boom" (Parent)
  |
  ├─ "Battery Demand Surge" (Child, Day 3)
  │   └─ "Silver Paste Shortage" (Grandchild, Day 8) ← CURRENT
  │
  └─ "Charging Infrastructure" (Child, Day 5)
      └─ Merged with → "Grid Upgrade" narrative
```

**Why This Matters**:
- Early detection: If parent narrative weakens, children will die soon
- Cascade effects: One strong parent can spawn 3-5 profitable children

---

### 8. **Sentiment Velocity Heatmap**
Real-time visualization of narrative momentum.

**Visual Design**:
```
        Bullish ↑
          ┃
    ⬤ Mining Strike (Accelerating)
    │
  ◯ Wedding Demand (Stable)
────┼─────────────> Time
    │
    ● Fed Rates (Decelerating)
          ┃
       Bearish ↓
```

**Color Coding**:
- 🔴 Red: High velocity, expect sharp moves
- 🟡 Yellow: Moderate, predictable trend
- 🟢 Green: Low velocity, range-bound

---

### 9. **Automated Weekly Intelligence Reports**
Every Sunday night, receive a comprehensive market analysis.

**Report Sections**:
1. **Executive Summary**: "Silver up 2.3% this week driven by 'Solar Demand' narrative"
2. **Narrative Birth/Death Log**: 3 new narratives detected, 1 declared dead
3. **Your Portfolio Performance**: +₹1,200 (+2.7%)
4. **Next Week Forecast**: "Expect volatility due to Fed announcement Wednesday"
5. **Recommended Actions**: "Consider taking profits on 30% of holdings"

**Format**: PDF + Interactive web version + Audio summary (AI-generated podcast)

---

### 10. **WhatsApp/Telegram Bot Integration**
Manage your silver intelligence on the go.

**Commands**:
```
User: /price
Bot:  Silver: ₹75,234/kg (+1.2% today)
      Dominant narrative: "Wedding Season Demand" (Growth)

User: /scan [photo]
Bot:  Detected: 925 silver chain, ~25g
      Value: ₹9,500-₹10,200
      Market context: Prices likely to rise 3-5% in 30 days

User: /should-i-sell
Bot:  HOLD ⏸️
      Reason: "Wedding Demand" narrative still in Growth phase
      Expected peak: 12-18 days (based on historical patterns)
      Recommended action: Set alert for Phase→Peak transition
```

---

## System Architecture

```
┌──────────────────────────────────────────────────────────────┐
│              Next.js Web Application + Mobile PWA            │
├─────────────┬─────────────┬─────────────┬───────────────────┤
│ 📊 Dashboard│ 💼 Portfolio│ 🔔 Alerts   │ 📸 Scanner (Bonus)│
│ - Narratives│ - Holdings  │ - Smart     │ - Quick valuation │
│ - Forecasts │ - P&L       │ - Filtered  │ - Market context  │
│ - Heatmaps  │ - Exposure  │ - WhatsApp  │                   │
└─────────────┴─────────────┴─────────────┴───────────────────┘
                       ↓  (WebSocket + REST)
         ┌──────────────────────────────────┐
         │     FastAPI Backend (Async)      │
         │     + Background Task Queue      │
         └──────────────────────────────────┘
                       ↓
    ┌──────────────────┴────────────────────────────┐
    ↓                  ↓                            ↓
┌────────────┐  ┌──────────────┐       ┌──────────────────┐
│ Narrative  │  │ Trading      │       │ Vision (Bonus)   │
│ Intelligence│  │ Agent        │       │ - Scanner        │
│            │  │              │       │ - Valuation      │
│ - Resource │  │ - Signals    │       └──────────────────┘
│   Manager  │  │ - Portfolio  │
│ - Pattern  │  │ - Forecasts  │
│   Hunter   │  │ - Alerts     │
│ - Lifecycle│  │ - Reports    │
│   Tracker  │  │              │
└────────────┘  └──────────────┘
       ↓              ↓
┌──────────────────────────────────────────────────────┐
│         Multi-Model Orchestrator (99.9% Uptime)      │
│  ┌─────────┬─────────┬─────────┬──────────┐         │
│  │ Groq    │ Ollama  │ HF      │ Traditional│       │
│  │ (Fast)  │(Reliable)│(Backup) │ ML (VADER) │       │
│  │ Primary │ Fallback│ Validator│ Sentiment  │       │
│  └─────────┴─────────┴─────────┴──────────┘         │
└──────────────────────────────────────────────────────┘
       ↓
┌──────────────────────────────────────────────────────┐
│   Data Layer (SQLite + Redis Cache)                  │
│   ┌────────────┬────────────┬──────────────┐        │
│   │ Narratives │ Portfolio  │ Market Data  │        │
│   │ - History  │ - Holdings │ - Price OHLC │        │
│   │ - Patterns │ - Trades   │ - News cache │        │
│   │ - Forecasts│ - Alerts   │ - Sentiment  │        │
│   └────────────┴────────────┴──────────────┘        │
└──────────────────────────────────────────────────────┘
       ↓
┌──────────────────────────────────────────────────────┐
│   External Integrations                              │
│   - NewsAPI, Reddit, Twitter/X, Yahoo Finance        │
│   - WhatsApp/Telegram Bots                           │
│   - Email/SMS Alert Services                         │
│   - Public API for Third-Party Developers           │
└──────────────────────────────────────────────────────┘
```

---

## User Review Required

> [!WARNING]
> **Rate Limit Strategy**: The system uses multiple model providers with automatic fallback. Groq provides 30 requests/minute which may be insufficient for high-traffic demos. The implementation includes Ollama (local) as backup, which requires ~10GB disk space and a one-time model download (~20 minutes).

> [!IMPORTANT]
> **Computer Vision Accuracy**: Weight estimation from 2D images is inherently imprecise (±15-25% error). The implementation assumes users will provide a **reference object** (coin, ruler, A4 paper) for scale. For production deployment, integration with smartphone LiDAR sensors (iPhone 12+) is recommended.

> [!CAUTION]
> **Market Data Limitations**: NewsAPI free tier allows 100 requests/day. The Resource Manager (PS 4) implements intelligent throttling to prioritize high-volatility periods. For hackathon demo, we'll use cached sample data to showcase the system without hitting limits.

---

## Proposed Changes

### Core Infrastructure

#### [NEW] [orchestrator.py](file:///Users/varad/Github/Hackathons/Nmims%20hack/backend/orchestrator.py)

Multi-model orchestration engine with intelligent routing and fallback chains.

**Key Features**:
- Rate limit tracking with per-minute request counting
- Automatic model selection based on task type and availability
- Parallel execution for cross-validation tasks
- Consensus voting for critical decisions (purity detection)

**Models Matrix**:
```python
VISION_MODELS = {
    "primary": "groq/llama-3.2-90b-vision",      # Speed: 500 tok/s
    "backup": "ollama/llama3.2-vision",          # Unlimited, local
    "validator": "hf/Qwen2-VL-7B"                # Cross-check
}

TEXT_MODELS = {
    "narrative": "groq/llama-3.3-70b",           # Speed: 800 tok/s
    "clustering": "groq/mixtral-8x7b",           # Classification expert
    "sentiment": "vader",                         # Rule-based, instant
    "local": "ollama/gemma2:9b"                  # Offline fallback
}
```

#### [NEW] [config.py](file:///Users/varad/Github/Hackathons/Nmims%20hack/backend/config.py)

Centralized configuration management for API keys, model settings, and thresholds.

---

### Computer Vision Module

#### [NEW] [vision_pipeline.py](file:///Users/varad/Github/Hackathons/Nmims%20hack/backend/vision/vision_pipeline.py)

End-to-end pipeline for silver object analysis.

**Processing Steps**:
1. **Image Preprocessing**: Resize, normalize, enhance contrast
2. **Reference Detection**: Identify A4 paper/coin for scale calibration
3. **Object Segmentation**: Isolate silver item from background
4. **Dimension Estimation**: Calculate length/width using reference scale
5. **Purity Detection**: OCR-style extraction of 925/999 markings
6. **Quality Assessment**: Analyze tarnish, scratches, craftsmanship

**Multi-Model Validation**:
```python
async def validate_purity(image_path: str) -> dict:
    # Run 3 models in parallel
    results = await asyncio.gather(
        groq_vision_analysis(image_path),
        ollama_vision_analysis(image_path),
        qwen_vision_analysis(image_path)
    )
    
    # Consensus voting
    purity_votes = extract_purity_votes(results)
    confidence = calculate_confidence(purity_votes)
    
    return {
        "purity": majority_vote(purity_votes),
        "confidence": confidence,
        "raw_results": results
    }
```

#### [NEW] [valuation_engine.py](file:///Users/varad/Github/Hackathons/Nmims%20hack/backend/vision/valuation_engine.py)

Calculates silver value based on CV analysis + current market rates.

**Pricing Formula**:
```
Base Value = Weight (g) × Purity Factor × Current Spot Price
Adjusted Value = Base Value × (1 + Craftsmanship Premium - Condition Penalty)
```

---

### Narrative Intelligence Engine

#### [NEW] [resource_manager.py](file:///Users/varad/Github/Hackathons/Nmims%20hack/backend/narrative/resource_manager.py)

**PS 4 Implementation**: Autonomous data collection orchestration.

**Decision Logic**:
```python
class ResourceManager:
    def decide_scraping_strategy(self):
        volatility = self.calculate_volatility()
        
        if volatility > 5.0:
            # High volatility: aggressive scraping
            return {
                "news_interval": 10,      # minutes
                "reddit_interval": 5,
                "sources": ["all"]
            }
        elif volatility > 2.0:
            return {
                "news_interval": 30,
                "reddit_interval": 15,
                "sources": ["premium"]    # NewsAPI, Reuters
            }
        else:
            # Low volatility: conserve API calls
            return {
                "news_interval": 120,
                "reddit_interval": 60,
                "sources": ["cached"]
            }
```

**Budget Allocation**:
- Prioritizes sources with historically high signal-to-noise ratio
- Tracks "data freshness" and triggers refreshes only when stale
- Implements exponential backoff for failing sources

#### [NEW] [pattern_hunter.py](file:///Users/varad/Github/Hackathons/Nmims%20hack/backend/narrative/pattern_hunter.py)

**PS 5 Implementation**: Unsupervised narrative discovery.

**Clustering Pipeline**:
1. **Text Preprocessing**: Clean, tokenize, remove stopwords
2. **Embedding**: TF-IDF vectorization (or sentence-transformers for better quality)
3. **Clustering**: HDBSCAN (auto-determines cluster count)
4. **Naming**: Groq Llama-3.3-70B generates human-readable labels

```python
from sklearn.feature_extraction.text import TfidfVectorizer
from hdbscan import HDBSCAN

class PatternHunter:
    async def discover_narratives(self, articles: list[str]):
        # Vectorize
        vectors = self.vectorizer.fit_transform(articles)
        
        # Cluster
        clusters = HDBSCAN(min_cluster_size=3).fit_predict(vectors)
        
        # Name each cluster
        narratives = []
        for cluster_id in set(clusters):
            if cluster_id == -1:  # Noise cluster
                continue
            
            cluster_articles = [articles[i] for i, c in enumerate(clusters) if c == cluster_id]
            narrative_name = await self.name_cluster(cluster_articles)
            narratives.append({
                "id": cluster_id,
                "name": narrative_name,
                "articles": cluster_articles,
                "birth_date": datetime.now()
            })
        
        return narratives
```

#### [NEW] [lifecycle_tracker.py](file:///Users/varad/Github/Hackathons/Nmims%20hack/backend/narrative/lifecycle_tracker.py)

**PS 6 Implementation**: Tracks narrative phases and detects transitions.

**State Machine**:
```
Birth ──────> Growth ──────> Peak ──────> Reversal ──────> Death
  │              │             │              │              │
  │              │             │              │              │
  ↓              ↓             ↓              ↓              ↓
New mentions  +50% velocity  Max correlation  Contradiction  0 mentions
detected       sustained      with price      appears       in 48h
```

**Transition Detection**:
```python
class LifecycleTracker:
    def detect_phase_transition(self, narrative: Narrative):
        current_phase = narrative.phase
        metrics = self.calculate_metrics(narrative)
        
        # Birth → Growth
        if current_phase == "birth" and metrics["velocity_increase"] > 0.5:
            return "growth"
        
        # Growth → Peak
        if current_phase == "growth" and metrics["price_correlation"] > 0.8:
            return "peak"
        
        # Peak → Reversal
        if current_phase == "peak" and (
            metrics["sentiment_decline"] > 0.3 or
            metrics["conflicting_narratives_detected"]
        ):
            return "reversal"
        
        # Reversal → Death
        if current_phase == "reversal" and metrics["mentions_48h"] == 0:
            return "death"
        
        return current_phase
```

**Conflict Detection**:
```python
def detect_conflicts(self, narratives: list[Narrative]):
    conflicts = []
    
    for n1, n2 in itertools.combinations(narratives, 2):
        if self.are_opposing(n1, n2):
            strength_diff = abs(n1.strength - n2.strength)
            conflicts.append({
                "narrative_1": n1.name,
                "narrative_2": n2.name,
                "net_sentiment": self.calculate_net_sentiment(n1, n2),
                "winner": n1 if n1.strength > n2.strength else n2,
                "confidence": strength_diff / 100.0
            })
    
    return conflicts
```

---

### Autonomous Trading Agent

#### [NEW] [trading_agent.py](file:///Users/varad/Github/Hackathons/Nmims%20hack/backend/agent/trading_agent.py)

Decision engine that translates narrative states into trading signals.

**Decision Matrix**:
| Dominant Narrative Phase | Price Trend | Strength | Action | Confidence |
|--------------------------|-------------|----------|--------|------------|
| Growth | Upward | >70 | **BUY** | High |
| Growth | Sideways | >60 | BUY | Medium |
| Peak | Any | >80 | HOLD (prepare to exit) | High |
| Reversal | Downward | >50 | **SELL** | High |
| Death | Any | N/A | SELL (narrative dead) | High |
| Conflicting narratives | Any | <40 | HOLD | Low |

**Risk Management**:
```python
class TradingAgent:
    def calculate_position_size(self, signal: Signal, narratives: list[Narrative]):
        base_size = 1.0  # 100% allocation
        
        # Reduce size if conflicts exist
        if self.has_conflicts(narratives):
            base_size *= 0.5
        
        # Reduce size if confidence is low
        if signal.confidence < 0.6:
            base_size *= signal.confidence
        
        # Increase size for high-conviction trades
        if signal.confidence > 0.8 and signal.strength > 75:
            base_size *= 1.2
        
        return min(base_size, 1.5)  # Cap at 150%
```

#### [NEW] [stability_monitor.py](file:///Users/varad/Github/Hackathons/Nmims%20hack/backend/agent/stability_monitor.py)

**PS 14 Implementation**: Detects overconfidence risk during stable periods.

```python
def calculate_stability_score(price_history: list[float]) -> dict:
    """
    Returns low score (0-30) when market is too stable = HIGH RISK
    (paradoxical: stability breeds complacency)
    """
    volatility = np.std(price_history[-30:])  # 30-day window
    
    if volatility < 0.5:
        return {
            "score": 20,
            "warning": "CAUTION: Market too stable. Volatility spike likely.",
            "recommendation": "Reduce position size by 30%"
        }
    elif volatility < 1.0:
        return {
            "score": 50,
            "warning": "Low volatility detected.",
            "recommendation": "Stay alert for breakout"
        }
    else:
        return {
            "score": 80,
            "warning": None,
            "recommendation": "Normal market conditions"
        }
```

---

### Web Application

#### [NEW] [app/page.tsx](file:///Users/varad/Github/Hackathons/Nmims%20hack/frontend/app/page.tsx)

Next.js home page with dual interface: Scanner + Dashboard.

**Layout**:
```tsx
export default function Home() {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Left: Silver Scanner */}
      <ScannerPanel />
      
      {/* Right: Trading Dashboard */}
      <DashboardPanel />
    </div>
  )
}
```

#### [NEW] [components/ScannerPanel.tsx](file:///Users/varad/Github/Hackathons/Nmims%20hack/frontend/components/ScannerPanel.tsx)

Image upload interface with real-time analysis display.

**Features**:
- Drag-and-drop image upload
- Live preview with reference object detection overlay
- Progress indicators for each analysis step
- Animated value reveal with confidence score

#### [NEW] [components/NarrativeTimeline.tsx](file:///Users/varad/Github/Hackathons/Nmims%20hack/frontend/components/NarrativeTimeline.tsx)

Visual representation of narrative lifecycles.

**Design**:
```
┌─────────────────────────────────────────────┐
│  Industrial Solar Demand  🔥               │
│  ━━━━━━━━━━━━━━━━━●━━━━━━━━━━━━━━━━━━━   │
│  Birth → Growth → PEAK → Reversal → Death  │
│  Strength: 87/100 | Age: 14 days           │
└─────────────────────────────────────────────┘
```

#### [NEW] [components/AgentConsole.tsx](file:///Users/varad/Github/Hackathons/Nmims%20hack/frontend/components/AgentConsole.tsx)

Live log of autonomous agent decisions.

```
[14:23:45] Resource Manager: Volatility spike detected (6.2%)
[14:23:46] Initiating aggressive news scraping...
[14:24:12] Pattern Hunter: New narrative cluster detected
[14:24:15] Narrative named: "Peru Mining Strike"
[14:24:16] Lifecycle Tracker: Narrative in BIRTH phase
[14:25:30] Trading Agent: BUY signal (Confidence: 72%)
```

#### [NEW] [app/api/scan/route.ts](file:///Users/varad/Github/Hackathons/Nmims%20hack/frontend/app/api/route.ts)

API route for handling image uploads and forwarding to FastAPI backend.

---

### Backend API

#### [NEW] [main.py](file:///Users/varad/Github/Hackathons/Nmims%20hack/backend/main.py)

FastAPI application with WebSocket support for real-time updates.

**Key Endpoints**:
```python
@app.post("/api/scan")
async def scan_silver(image: UploadFile):
    """Computer vision analysis of silver object"""
    
@app.get("/api/narratives")
async def get_narratives():
    """Retrieve active narratives with lifecycle status"""
    
@app.get("/api/trading-signal")
async def get_signal():
    """Get current buy/sell recommendation"""
    
@app.websocket("/ws/live")
async def websocket_endpoint(websocket: WebSocket):
    """Real-time price and narrative updates"""
```

#### [NEW] [database.py](file:///Users/varad/Github/Hackathons/Nmims%20hack/backend/database.py)

SQLite database schema and ORM models.

**Schema**:
```sql
CREATE TABLE narratives (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    phase TEXT CHECK(phase IN ('birth', 'growth', 'peak', 'reversal', 'death')),
    strength INTEGER CHECK(strength >= 0 AND strength <= 100),
    sentiment REAL,
    birth_date TIMESTAMP,
    last_updated TIMESTAMP,
    article_count INTEGER
);

CREATE TABLE scans (
    id INTEGER PRIMARY KEY,
    user_id TEXT,
    image_path TEXT,
    detected_type TEXT,
    purity INTEGER,
    estimated_weight REAL,
    valuation REAL,
    confidence REAL,
    created_at TIMESTAMP
);

CREATE TABLE price_history (
    id INTEGER PRIMARY KEY,
    timestamp TIMESTAMP,
    price REAL,
    source TEXT
);
```

---

## Verification Plan

### Automated Tests

#### Unit Tests
```bash
# Vision pipeline
pytest tests/test_vision_pipeline.py -v
# Tests: reference detection, dimension calculation, purity extraction

# Narrative engine
pytest tests/test_pattern_hunter.py -v
# Tests: clustering accuracy, narrative naming

# Lifecycle tracker
pytest tests/test_lifecycle.py -v
# Tests: phase transitions, conflict detection

# Trading agent
pytest tests/test_trading_agent.py -v
# Tests: decision logic, position sizing
```

#### Integration Tests
```bash
# End-to-end flow
pytest tests/test_integration.py -v
# Tests: Image upload → CV analysis → Valuation
#        News scraping → Clustering → Lifecycle tracking → Trading signal
```

#### Model Fallback Tests
```bash
# Orchestrator reliability
pytest tests/test_orchestrator.py -v
# Tests: Rate limit handling, fallback chains, consensus voting
```

### Manual Verification

#### Computer Vision Accuracy
1. Test with 10 real silver objects of known weight/purity
2. Calculate average error rate (target: <20%)
3. Verify reference object detection works with common items

#### Narrative Detection
1. Feed historical news from Dec 2024 (known silver price surge)
2. Verify system detects "Industrial Demand" narrative
3. Confirm lifecycle phases match actual market timeline

#### Trading Signal Validation
1. Backtest on 6 months of historical data
2. Compare against buy-and-hold strategy
3. Calculate Sharpe ratio and max drawdown

#### UI/UX Testing
1. Test on mobile (iOS Safari, Android Chrome)
2. Verify WebSocket reconnection on network drop
3. Test image upload with 10MB+ files

### Demo Scenarios

**Scenario 1: New User Scanning Silver**
1. User uploads photo of silver chain with coin for reference
2. System detects object, estimates 25g, 925 purity
3. Shows valuation: ₹9,500 with 78% confidence
4. Displays current market narrative: "Wedding Season Demand (Growth phase)"

**Scenario 2: Live Market Event**
1. During demo, manually trigger "news flash" about mining strike
2. Show Resource Manager deciding to increase scraping frequency
3. Pattern Hunter detects new narrative cluster
4. Lifecycle Tracker moves it to Birth phase
5. Trading Agent issues "Monitor closely" signal

**Scenario 3: Conflict Resolution**
1. Display two competing narratives: "Inflation Hedge" (bullish) vs "Fed Rate Hike" (bearish)
2. Show strength scores: 72 vs 68
3. Agent decision: "HOLD (Low confidence due to conflict)"
4. Explain reasoning in Agent Console

---

## Technical Stack Summary

| Layer | Technology | Justification |
|-------|------------|---------------|
| **Frontend** | Next.js 15 + TypeScript | Server components, optimal performance |
| **UI Library** | Tailwind CSS + shadcn/ui | Rapid development, professional design |
| **Charts** | Recharts + D3.js | Real-time price charts, narrative timelines |
| **Backend** | FastAPI + Python 3.11 | Async support, auto-generated OpenAPI docs |
| **Database** | SQLite | Zero-config, sufficient for demo/MVP |
| **Vision Models** | Groq Llama-3.2-90B, Ollama local | Speed + reliability |
| **Text Models** | Groq Llama-3.3-70B, Mixtral | Classification + generation tasks |
| **ML Libraries** | scikit-learn, HDBSCAN | Clustering, TF-IDF |
| **Sentiment** | VADER | Fast, rule-based, no API calls |
| **Real-time** | WebSockets | Live price updates, narrative changes |
| **Deployment** | Vercel (frontend) + Railway (backend) | Free tiers, easy setup |

---

## Development Timeline (24 Hours)

| Hour | Phase | Deliverable |
|------|-------|-------------|
| 0-2 | Environment setup | Ollama installed, API keys configured, dependencies installed |
| 2-4 | Database + Orchestrator | SQLite schema, multi-model orchestrator working |
| 4-8 | Vision pipeline | Image upload → CV analysis → Valuation |
| 8-12 | Narrative engine | News scraping → Clustering → Lifecycle tracking |
| 12-14 | Trading agent | Decision logic + Stability monitor |
| 14-18 | Frontend UI | Next.js app with Scanner + Dashboard |
| 18-20 | Integration | WebSocket, API connections, end-to-end flow |
| 20-22 | Testing + Polish | Bug fixes, UI animations, demo data seeding |
| 22-23 | Pitch deck | Presentation with architecture diagrams |
| 23-24 | Rehearsal | Practice live demo, record backup video |

---

## Risk Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Groq rate limits during demo | High | High | Ollama local fallback pre-tested |
| HDBSCAN fails with small data | Medium | Medium | Pre-seed database with 100+ sample articles |
| CV weight estimation inaccurate | High | Low | Clearly label as "estimate", allow manual override |
| WebSocket disconnects | Medium | Medium | Auto-reconnect logic + visual indicator |
| Model hallucinations | Medium | High | Cross-validation for critical decisions (purity) |

---

## Post-Hackathon Roadmap

### Phase 2 (Week 1-2)
- Integrate stripe for premium features
- Add user authentication (Clerk/Supabase Auth)
- Deploy on production infrastructure

### Phase 3 (Month 1)
- Mobile app (React Native) with camera integration
- LiDAR support for iPhone users (precise measurements)
- Multi-commodity support (gold, platinum)

### Phase 4 (Month 2-3)
- Marketplace for buying/selling silver
- Broker API integration for actual trading
- Advanced ML models (fine-tuned vision models)

---

## Success Metrics

**For Hackathon Judging**:
- ✅ Demonstrates all 3 problem statements working together
- ✅ Visually impressive UI with real-time updates
- ✅ Explainable AI (judges can understand decisions)
- ✅ Functional demo (no critical failures during presentation)
- ✅ Clear value proposition (solve real user problems)

**Technical Metrics**:
- CV analysis: <5 seconds per image
- Narrative detection: <10 minutes for new patterns
- WebSocket latency: <100ms
- Model fallback success rate: >95%

---

## Conclusion

This implementation plan delivers a production-ready MVP that showcases advanced AI capabilities while maintaining reliability through multi-model orchestration. The system addresses real market needs (jewelry buyer protection, trader decision support) while demonstrating technical sophistication through autonomous agents and computer vision.

The modular architecture allows for rapid iteration during the hackathon while providing a solid foundation for post-event development into a commercial product.
