# 📂 Backend Folder Structure Explained

This document explains what each folder and file in the **SilverSentinel backend** does and how they work together.

---

## 🗂️ Overview

The backend is built with **FastAPI** and implements an autonomous AI-driven silver market intelligence system. Here's the complete structure:

```
backend/
├── Root Files (Core Infrastructure)
│   ├── main.py                    # FastAPI application & API endpoints
│   ├── orchestrator.py            # Multi-model AI orchestration
│   ├── config.py                  # Configuration management
│   ├── database.py                # Database models (SQLAlchemy)
│   ├── data_collection.py         # Data fetching (news, Reddit, prices)
│   ├── seed_demo_data.py          # Demo data generator
│   └── requirements.txt           # Python dependencies
│
├── agent/                         # 🤖 Trading Intelligence
│   ├── trading_agent.py           # Decision engine (BUY/SELL/HOLD)
│   └── stability_monitor.py       # Overconfidence detection (PS 14)
│
├── narrative/                     # 📖 Market Narrative Analysis
│   ├── resource_manager.py        # Autonomous scraping (PS 4)
│   ├── pattern_hunter.py          # Narrative discovery (PS 5)
│   ├── lifecycle_tracker.py       # Phase tracking (PS 6)
│   ├── sentiment_analyzer.py      # VADER sentiment analysis
│   └── forecaster.py              # Predict narrative changes
│
├── vision/                        # 👁️ Computer Vision (Bonus Feature)
│   ├── vision_pipeline.py         # OpenCV + Vision LLM
│   ├── valuation_engine.py        # Silver price calculation
│   └── prompts.py                 # Vision model prompts
│
└── tests/                         # 🧪 Testing
    └── test_integration.py        # End-to-end tests
```

---

## 📄 Root Files (Core Infrastructure)

These files form the backbone of the system:

### `main.py` - FastAPI Application
**What it does:**
- Serves REST API endpoints (e.g., `/api/narratives`, `/api/trading-signal`)
- Handles WebSocket connections for real-time updates
- Coordinates all backend modules
- Runs background monitoring tasks

**Key responsibilities:**
- Health checks and status endpoints
- Data collection triggers
- Narrative discovery triggers
- Trading signal generation
- Price history endpoints
- Real-time WebSocket streaming

**Technologies:** FastAPI, asyncio, WebSockets

---

### `orchestrator.py` - Multi-Model AI Orchestration
**What it does:**
- Routes AI requests to different LLM providers (Groq, Gemini, Ollama)
- Provides **99.9% uptime** through intelligent fallback
- Handles rate limiting and error recovery

**Fallback Strategy:**
- **Text**: Groq → Gemini → Ollama (local)
- **Vision**: Groq → Gemini

**Key features:**
- Automatic provider switching on failure
- Rate limit tracking
- Standardized response format
- Async/sync support

**Technologies:** Groq API, Google Gemini, Ollama

---

### `config.py` - Configuration Management
**What it does:**
- Loads environment variables from `.env`
- Stores API keys and model configurations
- Defines thresholds for trading decisions
- Configures data collection intervals

**Configuration categories:**
- **Model Config**: API keys, model names, rate limits
- **Data Config**: NewsAPI, Reddit credentials
- **Narrative Config**: Clustering parameters, phase thresholds
- **Trading Config**: Risk thresholds, position sizing rules
- **System Config**: Logging, database path

---

### `database.py` - Database Models
**What it does:**
- Defines database schema using SQLAlchemy ORM
- Manages connections to SQLite database
- Provides session management

**Database Tables:**
1. **Narratives**: Market stories with lifecycle phases
2. **Articles**: News/social media content with sentiment
3. **PriceData**: Historical silver prices
4. **TradingSignals**: Generated BUY/SELL/HOLD signals
5. **SilverScans**: Vision scan results (bonus feature)

**Key relationships:**
- Narratives have many Articles
- Narratives can have parent-child relationships
- Articles linked to Narratives via clustering

---

### `data_collection.py` - Data Fetching
**What it does:**
- Fetches news articles from NewsAPI
- Scrapes Reddit posts about silver
- Downloads silver price data from Yahoo Finance
- Stores everything in the database

**Components:**
1. **NewsCollector**: Fetches articles about silver markets
2. **RedditCollector**: Scrapes r/Silverbugs, r/WallStreetSilver
3. **PriceCollector**: Downloads SI=F (silver futures) prices
4. **DataCollectionOrchestrator**: Coordinates all collectors

**Update frequency:** Controlled by `resource_manager.py` based on market volatility

---

### `seed_demo_data.py` - Demo Data Generator
**What it does:**
- Creates realistic demo data for testing/demos
- Generates 30 days of hourly price data
- Creates 4 narratives in different lifecycle phases
- Adds 60+ articles with sentiment scores

**Use case:** Quick start for evaluators without waiting for real data collection

---

## 🤖 `/agent` Folder - Trading Intelligence

This folder contains the **autonomous decision-making** components.

### `trading_agent.py` - Decision Engine
**What it does:**
- Analyzes all active narratives
- Generates trading signals (BUY/SELL/HOLD)
- Calculates position sizes based on risk
- Detects conflicts between competing narratives

**Decision Logic:**
- **BUY**: Narratives in GROWTH or early PEAK phase
- **SELL**: Narratives in REVERSAL or DEATH phase
- **HOLD**: Mixed signals or low confidence

**Output example:**
```json
{
  "action": "BUY",
  "confidence": 0.85,
  "strength": 85,
  "reasoning": "Narrative 'Industrial Solar Demand' in GROWTH phase",
  "position_size": 1.2,
  "dominant_narrative": "Industrial Solar Demand"
}
```

---

### `stability_monitor.py` - Overconfidence Detection (PS 14)
**What it does:**
- Calculates market stability score (0-100)
- Warns when markets are TOO calm (overconfidence risk)
- Adjusts position sizes during stable periods

**Why it matters:**
- Calm markets often precede major moves
- LOW stability score = HIGH risk of sudden change
- Prevents overconfidence in predictions

**Metrics tracked:**
- Price volatility (last 24 hours)
- Narrative churn (how fast narratives change)
- Consecutive stable days

---

## 📖 `/narrative` Folder - Market Narrative Analysis

This folder implements the core **unsupervised learning** and **narrative lifecycle tracking**.

### `resource_manager.py` - Autonomous Scraping (PS 4)
**What it does:**
- Calculates market volatility every 5 minutes
- Adjusts data collection intervals automatically
- Allocates scraping budget based on source quality

**Scraping Modes:**
- **Aggressive** (10 min): High volatility detected
- **Balanced** (30 min): Normal market conditions
- **Conservative** (2 hours): Low volatility, save resources

**Implementation:** Problem Statement 4 (Autonomous Resource Management)

---

### `pattern_hunter.py` - Narrative Discovery (PS 5)
**What it does:**
- Discovers market narratives using **unsupervised clustering**
- Groups similar articles together (HDBSCAN algorithm)
- Uses LLM to name narratives (no predefined categories!)

**Process:**
1. Extract articles from database
2. Convert to TF-IDF feature vectors
3. Cluster with HDBSCAN (min 3 articles per cluster)
4. Use LLM to generate human-readable narrative names
5. Store narratives in database

**Technologies:** HDBSCAN, TF-IDF, scikit-learn

**Implementation:** Problem Statement 5 (Unsupervised Pattern Discovery)

---

### `lifecycle_tracker.py` - Phase Tracking (PS 6)
**What it does:**
- Tracks narratives through 5 lifecycle phases
- Detects phase transitions automatically
- Identifies conflicts between competing narratives

**5 Phases:**
1. **BIRTH**: New narrative emerges (low articles, growing)
2. **GROWTH**: Gaining momentum (increasing mentions)
3. **PEAK**: Maximum strength (high articles, strong sentiment)
4. **REVERSAL**: Losing momentum (declining mentions)
5. **DEATH**: Faded away (inactive for 7+ days)

**State Machine Logic:**
- Birth → Growth: Article count > 5 AND sentiment increasing
- Growth → Peak: Article count > 10 AND high velocity
- Peak → Reversal: Sentiment turning negative
- Reversal → Death: No mentions for 7 days

**Implementation:** Problem Statement 6 (Sentiment Lifecycle Tracking)

---

### `sentiment_analyzer.py` - Sentiment Analysis
**What it does:**
- Analyzes sentiment of articles using VADER
- Calculates aggregate sentiment for narratives
- Tracks sentiment trends over time

**Output:** Sentiment score from -1.0 (very negative) to +1.0 (very positive)

**Technology:** VADER (Valence Aware Dictionary and sEntiment Reasoner)

---

### `forecaster.py` - Prediction Engine
**What it does:**
- Predicts when narrative phases will change
- Forecasts sentiment trends
- Identifies early warning signals

**Use case:** Get ahead of market moves by predicting narrative transitions

---

## 👁️ `/vision` Folder - Computer Vision (Bonus Feature - Phase 8)

This folder implements the **physical silver scanner** using computer vision.

### `vision_pipeline.py` - OpenCV + Vision LLM
**What it does:**
- Analyzes images of physical silver objects
- Detects reference objects for scale (coins, rulers)
- Estimates dimensions and weight
- Assesses purity and quality

**Process:**
1. **OpenCV Processing**: Edge detection, contour finding
2. **Reference Detection**: Find known objects (e.g., 5 rupee coin)
3. **Scale Calibration**: Calculate pixels-per-mm ratio
4. **Vision LLM Analysis**: Detect hallmarks, assess quality
5. **Dimension Calculation**: Measure width, height, area

**Technologies:** OpenCV, Groq Vision, Google Gemini Vision

---

### `valuation_engine.py` - Silver Price Calculation
**What it does:**
- Calculates market value based on:
  - Weight (grams)
  - Purity (92.5% for sterling, 99.9% for fine silver)
  - Current silver spot price
  - Condition and quality

**Formula:**
```
Value = Weight (g) × Purity % × Spot Price (per gram) × Condition Factor
```

---

### `prompts.py` - Vision Model Prompts
**What it does:**
- Stores prompt templates for vision AI
- Ensures consistent analysis across scans

**Prompts:**
- Purity detection (hallmarks, stamps)
- Quality assessment (scratches, tarnish)
- Reference object detection
- Thickness estimation

---

## 🧪 `/tests` Folder - Testing

### `test_integration.py` - End-to-End Tests
**What it does:**
- Tests the entire pipeline from data collection to signal generation
- Validates database operations
- Ensures API endpoints work correctly

**Test coverage:**
- Data collection
- Narrative discovery
- Lifecycle tracking
- Trading signal generation
- Vision pipeline (bonus)

**Run tests:**
```bash
cd backend
pytest tests/test_integration.py -v
```

---

## 🔄 How Everything Works Together

Here's the complete workflow:

### 1. Data Collection (Triggered by `resource_manager`)
```
data_collection.py → Fetches news, Reddit, prices
                  ↓
database.py       → Stores in SQLite
```

### 2. Narrative Discovery (Triggered by API or schedule)
```
pattern_hunter.py → Clusters articles
                  ↓
orchestrator.py   → Names narratives with LLM
                  ↓
database.py       → Stores narratives
```

### 3. Lifecycle Tracking (Runs every 5 minutes)
```
lifecycle_tracker.py → Updates phase for each narrative
                     ↓
database.py          → Updates narrative records
```

### 4. Trading Signal Generation (On-demand via API)
```
trading_agent.py → Analyzes all active narratives
                 ↓
stability_monitor.py → Checks for overconfidence risk
                 ↓
database.py → Stores trading signal
```

### 5. API Serving (Continuous)
```
main.py → Serves REST endpoints
        → Streams WebSocket updates
        → Coordinates all modules
```

---

## 🎯 Problem Statements Mapping

| Folder/File | Problem Statement | Description |
|-------------|-------------------|-------------|
| `narrative/resource_manager.py` | **PS 4** | Autonomous Resource Management |
| `narrative/pattern_hunter.py` | **PS 5** | Unsupervised Pattern Discovery |
| `narrative/lifecycle_tracker.py` | **PS 6** | Sentiment Lifecycle Tracking |
| `agent/stability_monitor.py` | **PS 14** | Overconfidence Detection |
| `vision/` (entire folder) | **Bonus Feature** | Computer Vision Scanner (Phase 8) |

---

## 🚀 Quick Start Guide

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
nano .env  # Add your API keys (GROQ_API_KEY required, NewsAPI/Reddit optional)
```

### 3. Initialize Database
```bash
python database.py
python seed_demo_data.py
```

### 4. Start Server
```bash
python main.py
```

### 5. Access API
- **Docs**: http://localhost:8000/docs
- **Trading Signal**: http://localhost:8000/api/trading-signal
- **Narratives**: http://localhost:8000/api/narratives

---

## 📊 Technology Stack by Folder

| Folder | Technologies |
|--------|-------------|
| **Root** | FastAPI, SQLAlchemy, asyncio, WebSockets |
| **agent/** | NumPy, Custom logic |
| **narrative/** | HDBSCAN, scikit-learn, TF-IDF, VADER |
| **vision/** | OpenCV, Groq Vision, Google Gemini Vision |
| **tests/** | pytest |

---

## 🔧 Key Configuration Files

- `.env` - API keys and secrets
- `config.py` - System thresholds and parameters
- `requirements.txt` - Python package dependencies

---

## 📝 Summary

The backend is organized into **logical modules** that each handle a specific part of the system:

1. **Root files** = Core infrastructure (API, database, AI orchestration)
2. **`/agent`** = Autonomous trading decisions
3. **`/narrative`** = Unsupervised learning and lifecycle tracking
4. **`/vision`** = Computer vision for physical silver
5. **`/tests`** = Quality assurance

All modules communicate through the **database** and are coordinated by **main.py**.

---

**Need help?** Check:
- API documentation: http://localhost:8000/docs
- Main README: `/README.md`
- Deployment guide: `/DEPLOYMENT.md`

**Made with ❤️ for autonomous intelligence**
