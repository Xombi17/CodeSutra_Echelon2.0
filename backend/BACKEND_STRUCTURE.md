# 📚 Backend Folder Structure Documentation

This document explains the purpose and functionality of each folder and file in the backend directory of the CodeSutra Echelon 2.0 project.

## 📋 Table of Contents

- [Overview](#overview)
- [Root Directory Files](#root-directory-files)
- [Folder Structure](#folder-structure)
  - [agent/](#agent-folder)
  - [narrative/](#narrative-folder)
  - [vision/](#vision-folder)
  - [tests/](#tests-folder)
- [Architecture Diagram](#architecture-diagram)
- [Key Workflows](#key-workflows)

---

## 🎯 Overview

The backend is a **FastAPI-based application** that provides real-time silver market intelligence. It uses AI-powered narrative tracking to discover and monitor market patterns. The system generates trading signals based on these narratives and can value physical silver items through computer vision. It combines multiple data sources (news, social media, price data) to track market narratives that influence silver prices.

---

## 📄 Root Directory Files

### `main.py` - FastAPI Application Server

**Purpose**: Core REST API and WebSocket server for the entire application

**Key Features**:
- **REST API Endpoints**:
  - `/api/narratives` - Get active market narratives
  - `/api/signals` - Get latest trading signals (BUY/SELL/HOLD)
  - `/api/prices` - Historical silver price data
  - `/api/stability` - Market stability scores
  - `/api/stats` - System statistics
  - `/api/scan` - Upload silver images for valuation (Phase 8 CV feature)

- **WebSocket Endpoint**:
  - `/ws/live` - Real-time updates for price changes and narrative updates (broadcasts every 5 seconds)

- **Background Tasks**:
  - Continuous data collection from news/Reddit/price feeds
  - Narrative discovery and lifecycle tracking
  - Trading signal generation
  - Stability monitoring

- **Middleware**: CORS configuration for frontend integration

**When to modify**: When adding new API endpoints, changing background task schedules, or modifying CORS settings

---

### `config.py` - Configuration Management

**Purpose**: Centralized configuration using Python dataclasses

**Configuration Sections**:

1. **ModelConfig** - AI model settings
   - API keys for Groq, Gemini, Ollama, HuggingFace
   - Model selection for different tasks
   - Temperature and token limits

2. **DataConfig** - Data collection settings
   - News API credentials
   - Reddit scraping parameters
   - Yahoo Finance settings
   - Refresh intervals for each data source

3. **NarrativeConfig** - Narrative tracking parameters
   - Lifecycle transition thresholds
   - Strength scoring weights (velocity: 30%, news: 25%, price: 25%, institutional: 20%)
   - Conflict detection settings
   - Minimum narrative strength thresholds

4. **TradingConfig** - Trading signal settings
   - Signal generation thresholds
   - Risk management parameters
   - Position sizing rules

5. **DatabaseConfig** - Database settings
   - SQLite database path
   - Redis cache configuration

**When to modify**: When adjusting thresholds, adding new API keys, or changing system behavior parameters

---

### `database.py` - SQLAlchemy ORM Models

**Purpose**: Database schema definitions and data models

**Models**:

1. **Narrative**
   - Represents market narratives (e.g., "Solar Panel Demand Surge")
   - Fields: name, description, strength, lifecycle phase, sentiment, mention_velocity
   - **Lifecycle Phases**: birth → growth → peak → reversal → death

2. **Article**
   - News articles and social media posts
   - Fields: title, content, source, url, sentiment_score, published_at
   - Links to narratives for pattern clustering

3. **PriceData**
   - Historical silver price data (OHLCV)
   - Fields: timestamp, open, high, low, close, volume
   - Used for correlation analysis and trading signals

4. **TradingSignal**
   - Generated trading recommendations
   - Fields: action (BUY/SELL/HOLD), confidence, strength, position_size, dominant_narrative
   - Includes conflict detection for contradictory narratives

5. **Portfolio**
   - User holdings tracking
   - Fields: asset_type (physical/paper), quantity, purchase_price, current_value
   - Supports portfolio management features

6. **SilverScan**
   - Physical silver image scan results
   - Fields: image_path, purity, weight, dimensions, quality_score, estimated_value
   - Used by Phase 8 computer vision feature

**When to modify**: When adding new data models or changing database schema

---

### `orchestrator.py` - Multi-Model LLM Orchestrator

**Purpose**: Provides 99.9% uptime guarantee with intelligent model fallback chain

**Key Components**:

1. **LLMOrchestrator Class**
   - **Text Generation Chain**: Groq (primary) → Google Gemini → Ollama (local fallback)
   - **Vision Analysis Chain**: Groq → Google Gemini (no local vision model)
   - Rate limiting to prevent API throttling
   - Parallel validation across multiple models
   - Consensus calculation for critical decisions

2. **RateLimiter Class**
   - Sliding window rate limiting
   - Per-model request tracking
   - Prevents API throttling and budget overruns

**Features**:
- Automatic failover on API errors
- Response validation and retry logic
- Model-specific error handling
- Performance monitoring

**When to modify**: When adding new AI models, changing fallback logic, or adjusting rate limits

---

### `data_collection.py` - Data Aggregation

**Purpose**: Orchestrates data collection from multiple sources

**Collectors**:

1. **NewsCollector**
   - Fetches articles from NewsAPI
   - Falls back to mock data if no API key configured
   - Filters for silver/precious metals keywords
   - Extracts: title, description, source, URL, published date

2. **RedditCollector**
   - Scrapes Reddit posts from silver-related subreddits
   - Subreddits: r/Silverbugs, r/WallStreetSilver, r/Gold
   - Extracts: title, selftext, score, created_utc, url
   - Converts to Article format for database storage

3. **PriceCollector**
   - Fetches silver futures price from Yahoo Finance (ticker: SI=F)
   - Retrieves OHLCV data (Open, High, Low, Close, Volume)
   - Stores in PriceData model for historical tracking

4. **DataCollectionOrchestrator**
   - Runs all collectors in parallel for efficiency
   - Combines results and saves to database
   - Handles errors gracefully (continues if one collector fails)
   - Returns collection statistics

**When to modify**: When adding new data sources, changing collection frequency, or modifying data extraction logic

---

### `seed_demo_data.py` - Test Data Generator

**Purpose**: Creates realistic demo data for development and testing

**Generated Data**:

1. **Price Data**
   - 30 days of hourly silver prices
   - Realistic volatility patterns
   - Base price around $25-30/oz with natural fluctuations

2. **Sample Articles**
   - Pre-defined templates for common silver narratives:
     - Mining Strike (bearish impact)
     - Solar Panel Demand (bullish impact)
     - Indian Wedding Season (seasonal demand)
     - Federal Reserve Concerns (macro-economic factor)
   - Multiple articles per narrative with varying dates

3. **Narratives**
   - 4+ sample narratives in different lifecycle phases
   - Varying strength levels (0.3 to 0.9)
   - Mixed sentiment scores
   - Realistic mention velocities

**Usage**: Run `python seed_demo_data.py` to populate database with test data

**When to modify**: When adding new narrative templates or changing demo data structure

---

## 📁 Folder Structure

### `agent/` Folder - Trading Intelligence

This folder contains AI agents responsible for generating trading signals and monitoring market stability.

#### `trading_agent.py` - Trading Signal Generation

**Purpose**: Generates BUY/SELL/HOLD trading signals based on active narratives

**Key Components**:

1. **TradingAgent Class**
   - Main trading decision engine
   - Analyzes active narratives (phase: growth or peak)
   - Combines narrative strength, sentiment, and price correlation
   - Determines optimal position sizes

2. **Signal Dataclass**
   - Structure for trading recommendations
   - Fields: action, confidence, strength, position_size, dominant_narrative, conflicting_narratives
   - Includes risk warnings for conflicting signals

3. **Core Logic**:
   - Filters narratives by lifecycle phase (only active ones)
   - Weights narratives by strength score
   - Checks for conflicts (contradictory signals)
   - Adjusts position size based on confidence and conflicts
   - Returns structured trading signal with explanation

4. **backtest() Method**
   - Historical testing of trading strategy
   - Validates signal accuracy against past data
   - Performance metrics calculation

**Example Signal**:
```python
Signal(
    action="BUY",
    confidence=0.85,
    strength=0.75,
    position_size=0.15,  # 15% of portfolio
    dominant_narrative="Solar Demand Surge",
    conflicting_narratives=[]
)
```

**When to modify**: When changing trading strategy, adjusting position sizing logic, or adding new signal types

---

#### `stability_monitor.py` - Market Stability Tracking

**Purpose**: Risk management layer that monitors market stability and adjusts trading behavior

**Key Components**:

1. **StabilityMonitor Class**
   - Calculates stability scores (0-100 scale)
   - Higher score = more stable market = larger positions allowed
   - Lower score = volatile market = smaller positions recommended

2. **Stability Calculation**:
   - Analyzes price volatility over 30-day window
   - Uses standard deviation of returns
   - Normalizes to 0-100 scale
   - Updates every hour

3. **Position Size Adjustment**:
   - High stability (>70): Allow larger positions (up to 30%)
   - Medium stability (40-70): Standard positions (10-20%)
   - Low stability (<40): Reduced positions (5-10%)

4. **Alert Generation**:
   - Generates warnings for sudden stability drops
   - Flags unusual market conditions
   - Triggers risk reduction protocols

**When to modify**: When adjusting risk management rules, changing volatility thresholds, or adding new stability metrics

---

### `narrative/` Folder - Market Intelligence & Pattern Recognition

This folder contains the core narrative discovery and tracking system - the heart of the silver market intelligence platform.

#### `pattern_hunter.py` - Narrative Discovery

**Purpose**: Discovers new market narratives from news articles and social media posts

**Key Components**:

1. **PatternHunter Class**
   - Main narrative discovery engine
   - Uses NLP and clustering to identify patterns

2. **Discovery Process**:
   - **Step 1**: Collects recent articles (last 7 days)
   - **Step 2**: Extracts text features using TF-IDF
   - **Step 3**: Clusters similar articles using DBSCAN
   - **Step 4**: Names each cluster using LLM (e.g., "Solar Demand Surge")
   - **Step 5**: Calculates cluster sentiment from article sentiment scores
   - **Step 6**: Saves new narratives to database (if meeting minimum threshold)

3. **Clustering Parameters**:
   - Minimum cluster size: 3 articles
   - Similarity threshold: 0.6 (cosine similarity)
   - Max clusters per run: 10

4. **LLM Integration**:
   - Uses orchestrator to generate narrative names
   - Ensures names are descriptive and market-relevant
   - Validates naming consistency

**Example Output**:
```python
Narrative(
    name="Solar Panel Manufacturing Boom",
    description="Increased industrial silver demand from solar...",
    strength=0.65,
    phase="birth",
    sentiment=0.7
)
```

**When to modify**: When tuning clustering parameters, changing narrative naming logic, or adjusting discovery frequency

---

#### `lifecycle_tracker.py` - Narrative Phase Tracking

**Purpose**: Monitors narrative progression through 5 lifecycle phases

**Lifecycle Phases**:

1. **Birth** - Narrative just discovered
   - Low mention count (<10 articles)
   - Emerging sentiment
   - Minimal price correlation

2. **Growth** - Narrative gaining traction
   - 50%+ increase in mention velocity
   - Rising sentiment scores
   - Increasing media coverage

3. **Peak** - Narrative at maximum influence
   - High price correlation (>0.8)
   - Maximum mention velocity
   - Dominant market sentiment

4. **Reversal** - Narrative losing influence
   - Declining sentiment
   - Mention velocity decreasing
   - Price correlation weakening

5. **Death** - Narrative no longer relevant
   - No mentions in last 48 hours
   - Very low sentiment
   - Minimal market impact

**Key Components**:

1. **LifecycleTracker Class**
   - Monitors all active narratives
   - Calculates phase transition criteria
   - Updates narrative phases automatically

2. **Tracking Metrics**:
   - **mention_velocity**: Articles/hour mentioning narrative
   - **price_correlation**: Correlation between mentions and price changes
   - **sentiment_score**: Aggregate sentiment from all related articles
   - **institutional_interest**: Mentions from financial institutions

3. **Phase Transition Logic**:
   - birth → growth: 50% velocity increase OR 0.6 sentiment
   - growth → peak: 0.8 price correlation OR 2x velocity
   - peak → reversal: Sentiment decline >20% OR velocity drop >30%
   - reversal → death: No mentions for 48 hours

4. **Strength Score Calculation**:
   - Weighted formula: 
     - mention_velocity: 30%
     - news_coverage: 25%
     - price_correlation: 25%
     - institutional_interest: 20%
   - Score range: 0.0 to 1.0

5. **Conflict Detection**:
   - Identifies narratives with opposing sentiments
   - Flags contradictory signals for trading agent
   - Example: "Federal Reserve Hawkish" (bearish) vs "Industrial Demand Surge" (bullish)

**When to modify**: When adjusting phase transition thresholds, changing strength scoring weights, or adding new lifecycle phases

---

#### `resource_manager.py` - Adaptive Data Collection

**Purpose**: Optimizes data collection frequency based on market conditions

**Key Components**:

1. **ResourceManager Class**
   - Dynamically adjusts scraping frequency
   - Manages API rate limits
   - Optimizes budget allocation

2. **Market Volatility Calculation**:
   - Analyzes 24-hour price changes
   - Calculates standard deviation of returns
   - Categorizes as: low, medium, or high volatility

3. **Scraping Strategy**:
   - **High volatility** (>5% daily change): Scrape every 10 minutes
   - **Medium volatility** (2-5% daily change): Scrape every 30 minutes
   - **Low volatility** (<2% daily change): Scrape every 2 hours

4. **API Rate Limiting**:
   - Tracks requests per API per time window
   - Prevents exceeding free tier limits
   - Queues requests during high-demand periods

5. **Source Staleness Monitoring**:
   - Tracks last successful data fetch per source
   - Flags stale sources (>4 hours old)
   - Prioritizes refreshing stale data

6. **Budget Allocation**:
   - Distributes API calls across sources
   - Prioritizes high-value sources during budget constraints
   - Balances between news, social media, and price data

**When to modify**: When changing collection strategies, adjusting rate limits, or adding new data sources

---

#### `forecaster.py` - Narrative Prediction

**Purpose**: Predicts narrative lifecycle progression and price impact

**Key Components**:

1. **NarrativeForecaster Class**
   - Forecasts next phase transitions
   - Estimates price impact from narratives
   - Provides confidence intervals

2. **predict_lifecycle() Method**:
   - Analyzes historical velocity trends
   - Estimates time to next phase transition
   - Uses linear regression on mention velocity
   - Returns: days_to_next_phase, confidence_score

3. **predict_price_impact() Method**:
   - Combines narrative strength and sentiment
   - Historical correlation analysis
   - Formula: `impact = sentiment × strength × historical_beta`
   - Returns: estimated_price_change_percentage

4. **Forecasting Features**:
   - Short-term predictions (1-7 days)
   - Confidence scores for each prediction
   - Multiple scenario analysis (best/worst/likely)
   - Accounts for narrative interactions

**Example Output**:
```python
{
    "narrative": "Solar Demand Surge",
    "current_phase": "growth",
    "predicted_next_phase": "peak",
    "days_to_transition": 3,
    "predicted_price_impact": "+2.5%",
    "confidence": 0.75
}
```

**When to modify**: When improving prediction algorithms, adding new forecasting models, or changing prediction windows

---

#### `sentiment_analyzer.py` - Sentiment Analysis

**Purpose**: Analyzes sentiment of text content using VADER (Valence Aware Dictionary and sEntiment Reasoner)

**Key Components**:

1. **SentimentAnalyzer Class**
   - VADER-based sentiment scoring
   - Optimized for financial/social media text
   - Handles market-specific language

2. **analyze() Method**:
   - Analyzes individual articles/posts
   - Returns compound sentiment score (-1 to +1)
   - -1 = very bearish, 0 = neutral, +1 = very bullish

3. **analyze_batch() Method**:
   - Processes multiple articles efficiently
   - Returns list of sentiment scores
   - Useful for clustering and narrative discovery

4. **detect_sentiment_inflection() Method**:
   - Identifies sentiment momentum shifts
   - Compares recent vs historical sentiment
   - Flags rapid sentiment changes (>30% shift)

5. **calculate_narrative_sentiment() Method**:
   - Aggregates sentiment from all articles in narrative
   - Weights by article recency and source credibility
   - Returns overall narrative sentiment score

**VADER Advantages**:
- Pre-trained on financial and social media text
- Handles negations, intensifiers, and emojis
- No training data required
- Fast and lightweight

**When to modify**: When switching to different sentiment models (e.g., FinBERT), adjusting score thresholds, or adding custom sentiment lexicons

---

### `vision/` Folder - Physical Silver Image Analysis (Phase 8)

This folder implements computer vision capabilities for analyzing images of physical silver items to estimate purity, weight, and market value.

#### `vision_pipeline.py` - Image Analysis Pipeline

**Purpose**: End-to-end image processing for physical silver valuation

**Key Components**:

1. **VisionPipeline Class**
   - Orchestrates entire image analysis workflow
   - Combines OpenCV and LLM-based vision models
   - Returns structured analysis results

2. **detect_reference_object() Method**:
   - Identifies coins, rulers, or other calibration objects
   - Uses OpenCV for edge detection
   - LLM vision models for object recognition
   - Extracts real-world dimensions for scale calculation

3. **segment_silver_object() Method**:
   - Isolates silver item from background
   - Uses color-based segmentation (silver's metallic reflectance)
   - Applies morphological operations for noise removal
   - Returns binary mask of silver object

4. **detect_purity() Method**:
   - Looks for purity stamps (925, 950, 999)
   - Uses OCR and vision models in parallel
   - Validates stamps with multiple models for consensus
   - Returns purity level and confidence score

5. **estimate_thickness() Method**:
   - Calculates from reference object dimensions
   - Uses pixel ratios and perspective geometry
   - Estimates volume if multiple angles provided
   - Returns thickness in millimeters

6. **assess_quality() Method**:
   - Detects surface defects:
     - Scratches and dents
     - Oxidation and tarnishing
     - Structural damage
   - Returns quality score (0-100)
   - Generates condition report

7. **calculate_weight() Method**:
   - Derives from dimensions + purity + silver density
   - Silver density: 10.49 g/cm³ (source: standard silver density at 20°C)
   - Adjusts for hollow items or gemstone inclusions
   - Returns estimated weight in grams

**Complete Analysis Flow**:
```
Upload Image → Detect Reference → Segment Silver → 
Detect Purity → Estimate Dimensions → Assess Quality → 
Calculate Weight → Send to Valuation Engine
```

**When to modify**: When improving CV algorithms, adding new purity detection methods, or enhancing quality assessment

---

#### `valuation_engine.py` - Market Value Calculation

**Purpose**: Computes market value of silver items based on analysis results

**Key Components**:

1. **ValuationEngine Class**
   - Calculates fair market value
   - Applies market adjustments
   - Returns valuation range with confidence

2. **get_spot_price() Method**:
   - Fetches current silver spot price from Yahoo Finance
   - Converts to ₹/gram (Indian Rupees - configurable for other currencies)
   - Caches price for 1 hour to reduce API calls
   - Falls back to recent average if fetch fails

3. **calculate_base_value() Method**:
   - Formula: `weight (g) × purity × spot_price (₹/g)`
   - Example: 50g × 0.925 (92.5% pure) × ₹85/g = ₹3,931

4. **apply_adjustments() Method**:
   - **Craftsmanship Premium**:
     - Jewelry: +15-30%
     - Artistic pieces: +20-50%
     - Rare designs: +50-100%
   - **Condition Penalty**:
     - Quality score <50: -10-30%
     - Heavy oxidation: -15%
     - Damage: -20-40%
   - **Purity Adjustment**:
     - 999 (fine silver): No adjustment
     - 950: -2%
     - 925 (sterling): -5%

5. **calculate_valuation_range() Method**:
   - Returns [min_value, max_value] range
   - Accounts for market uncertainty
   - Typical range: ±10% of base value
   - Wider range for low-confidence assessments

6. **get_confidence_score() Method**:
   - Based on image quality, purity detection confidence, and reference object clarity
   - Returns 0-100 score
   - <50: Low confidence (advise physical appraisal)
   - 50-80: Medium confidence
   - >80: High confidence

**Example Output**:
```python
{
    "weight": 52.3,  # grams
    "purity": 925,
    "base_value": 4125,  # ₹
    "adjusted_value": 4950,  # ₹ (with craftsmanship premium)
    "valuation_range": [4455, 5445],  # ₹ (±10%)
    "confidence": 78,
    "spot_price": 85.3,  # ₹/gram
    "adjustments_applied": ["craftsmanship_premium: +20%"]
}
```

**When to modify**: When adjusting valuation formulas, adding new adjustment factors, or changing premium calculations

---

#### `prompts.py` - Vision Model Prompts

**Purpose**: Stores LLM prompts specifically designed for image analysis tasks

**Contents**:
- Purity stamp detection prompts
- Quality assessment instructions
- Reference object identification prompts
- Silver vs non-silver classification prompts

**When to modify**: When improving prompt engineering for better vision model performance

---

### `tests/` Folder - Test Suite

**Purpose**: Integration and unit tests for backend components

#### `test_integration.py` - Integration Tests

**Test Coverage**:
1. End-to-end data collection flow
2. Narrative discovery and tracking
3. Trading signal generation
4. Vision pipeline with sample images
5. API endpoint validation
6. WebSocket connection testing
7. Database operations

**Running Tests**:
```bash
cd backend
pytest tests/test_integration.py -v
```

**When to modify**: When adding new features or changing existing behavior

---

## 🏗️ Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│              FastAPI Server (main.py)                   │
│  • REST API (narratives, signals, prices, scan)         │
│  • WebSocket (/ws/live - real-time updates)             │
│  • Background Tasks (data collection, tracking)         │
└───────────────┬─────────────────────────────────────────┘
                │
    ┌───────────┼───────────┬───────────┬──────────┐
    │           │           │           │          │
┌───▼───┐  ┌───▼────┐  ┌───▼─────┐ ┌──▼─────┐ ┌─▼────┐
│ Agent │  │ Vision │  │Narrative│ │  Data  │ │Config│
│ ───── │  │ ────── │  │  ─────  │ │ ────── │ │ ──── │
│Trading│  │Pipeline│  │ Pattern │ │ News   │ │ API  │
│Signal │  │Segment │  │ Hunter  │ │ Reddit │ │ Keys │
│Stabil-│  │Valua-  │  │Lifecycl-│ │ Price  │ │Thresh│
│ity    │  │tion    │  │ Tracker │ │Collect-│ │-olds │
└───┬───┘  └───┬────┘  └───┬─────┘ └──┬─────┘ └──────┘
    │          │           │           │
    │          │           │           │
    └──────────┼───────────┼───────────┘
               │           │
         ┌─────▼───────────▼──────┐
         │   LLM Orchestrator     │
         │  ─────────────────     │
         │  • Groq (primary)      │
         │  • Gemini (backup)     │
         │  • Ollama (local)      │
         │  • Rate limiting       │
         │  • Consensus validation│
         └─────────┬──────────────┘
                   │
         ┌─────────▼──────────────┐
         │   SQLite Database      │
         │   ───────────────      │
         │  • narratives          │
         │  • articles            │
         │  • price_data          │
         │  • trading_signals     │
         │  • silver_scans        │
         │  • portfolio           │
         └────────────────────────┘
```

---

## 🔄 Key Workflows

### 1. Data Collection Workflow
```
Every 30 minutes (configurable):
NewsCollector + RedditCollector + PriceCollector (parallel)
    ↓
Save to Database (articles, price_data tables)
    ↓
Trigger Pattern Hunter (if enough new articles)
```

### 2. Narrative Discovery Workflow
```
Every 4 hours:
PatternHunter.discover_narratives()
    ↓
Cluster recent articles by topic
    ↓
Name clusters using LLM
    ↓
Calculate cluster sentiment
    ↓
Save new narratives to database
```

### 3. Narrative Tracking Workflow
```
Every 10 minutes:
LifecycleTracker.update_all()
    ↓
For each narrative:
  - Calculate mention_velocity
  - Compute price_correlation
  - Update sentiment_score
  - Check phase transition criteria
  - Update strength score
  - Detect conflicts with other narratives
```

### 4. Trading Signal Workflow
```
Every 5 minutes:
TradingAgent.generate_signal()
    ↓
Get active narratives (growth/peak phases)
    ↓
Calculate aggregate strength & sentiment
    ↓
Check for conflicts
    ↓
Determine BUY/SELL/HOLD with position size
    ↓
Get stability score from StabilityMonitor
    ↓
Adjust position size based on stability
    ↓
Save signal to database
    ↓
Broadcast via WebSocket
```

### 5. Vision Analysis Workflow
```
User uploads silver image via /api/scan:
VisionPipeline.analyze()
    ↓
Detect reference object (scale)
    ↓
Segment silver object from background
    ↓
Detect purity stamps (925/950/999)
    ↓
Estimate dimensions and thickness
    ↓
Assess quality (scratches, oxidation)
    ↓
Calculate weight
    ↓
ValuationEngine.calculate_value()
    ↓
Get current spot price
    ↓
Apply adjustments (craftsmanship, condition, purity)
    ↓
Return valuation range + confidence
    ↓
Save to database (silver_scans table)
```

### 6. Real-time Updates Workflow
```
WebSocket connection established at /ws/live:
Every 5 seconds:
    ↓
Get latest price data
    ↓
Get active narratives
    ↓
Get latest trading signal
    ↓
Get stability score
    ↓
Broadcast JSON update to all connected clients
```

---

## 📊 Database Schema Quick Reference

```sql
-- Narratives
narratives (
    id, name, description, strength, phase,
    sentiment, mention_velocity, price_correlation,
    created_at, updated_at
)

-- Articles
articles (
    id, title, content, source, url,
    sentiment_score, published_at, narrative_id
)

-- Price Data
price_data (
    id, timestamp, open, high, low, close, volume
)

-- Trading Signals
trading_signals (
    id, action, confidence, strength, position_size,
    dominant_narrative, conflicting_narratives,
    created_at
)

-- Silver Scans
silver_scans (
    id, image_path, purity, weight, dimensions,
    quality_score, estimated_value, confidence,
    created_at
)

-- Portfolio
portfolio (
    id, asset_type, quantity, purchase_price,
    current_value, last_updated
)
```

---

## 🚀 Getting Started

### Running the Backend

```bash
# Install dependencies
cd backend
pip install -r requirements.txt

# Set up environment variables
cp ../.env.example ../.env
# Edit .env with your API keys

# Initialize database with demo data
python seed_demo_data.py

# Start the server
python main.py
```

### API Access

- **Base URL**: `http://localhost:8000`
- **API Docs**: `http://localhost:8000/docs` (Swagger UI)
- **WebSocket**: `ws://localhost:8000/ws/live`

### Configuration

Edit `config.py` to customize:
- API keys and model selections
- Data collection intervals
- Narrative thresholds
- Trading parameters

---

## 🛠️ Development Tips

1. **Adding New Data Sources**: Modify `data_collection.py` and create a new collector class
2. **Changing Trading Logic**: Edit `agent/trading_agent.py` signal generation logic
3. **Adjusting Narrative Phases**: Update thresholds in `narrative/lifecycle_tracker.py`
4. **Improving Vision Analysis**: Enhance algorithms in `vision/vision_pipeline.py`
5. **Adding API Endpoints**: Add routes in `main.py` and update CORS if needed

---

## 📝 Notes

- All timestamps in the database are in UTC
- Sentiment scores range from -1 (very bearish) to +1 (very bullish)
- Strength scores range from 0 (weak) to 1 (very strong)
- Position sizes are percentages (0.15 = 15% of portfolio)
- WebSocket messages are JSON-encoded with `type` and `data` fields

---

## 🔐 Security Considerations

- API keys stored in environment variables (never commit to git)
- Rate limiting on all endpoints
- Input validation on file uploads
- SQL injection prevention via ORM (SQLAlchemy)
- CORS configured for specific frontend origins only

---

## 📚 Further Reading

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy ORM Guide](https://docs.sqlalchemy.org/en/14/orm/)
- [VADER Sentiment Analysis](https://github.com/cjhutto/vaderSentiment)
- [OpenCV Documentation](https://docs.opencv.org/)

---

**Version**: 1.0  
**Maintainer**: CodeSutra Echelon 2.0 Team
