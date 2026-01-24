# FIN Branch Integration Plan

## Overview
The `fin` branch merges production features from `main` with the multi-agent system from `abhishek`.

## Integrated Components

### From Main Branch (Retained)
1. **Computer Vision Pipeline** (879 lines)
   - `backend/vision/vision_pipeline.py` - Silver object analysis
   - `backend/vision/valuation_engine.py` - Market valuation
   - `backend/vision/prompts.py` - Vision prompts
   - ReferenceObject detection, purity detection, weight estimation

2. **Data Collection System** (331 lines)
   - `backend/data_collection.py`
   - NewsAPI integration
   - Reddit (PRAW) scraping
   - Yahoo Finance price fetching
   - Real-time data collection

3. **Database Layer** (253 lines)
   - `backend/database.py`
   - SQLAlchemy ORM models (Narrative, Article, PriceData, TradingSignal, SilverScan)
   - Relational data tracking

4. **Configuration Management** (180 lines)
   - `backend/config.py`
   - Centralized configuration for all subsystems

5. **Advanced Analytics** (1,286 lines)
   - `backend/narrative/lifecycle_tracker.py` - State machine with velocity/correlation
   - `backend/narrative/sentiment_analyzer.py` - VADER sentiment analysis
   - `backend/narrative/resource_manager.py` - Volatility-based scraping
   - `backend/narrative/pattern_hunter.py` - HDBSCAN clustering

6. **Agent Intelligence** (569 lines)
   - `backend/agent/trading_agent.py` - 6 phase-based strategies
   - `backend/agent/stability_monitor.py` - Paradoxical stability scoring

7. **Multi-Provider Orchestrator** (427 lines)
   - `backend/orchestrator.py`
   - Groq → Gemini → Ollama → HuggingFace fallback chain

8. **Streamlit UI** (443 lines)
   - `frontend/streamlit_app.py` - Interactive dashboard

### From Abhishek Branch (Added)
1. **Multi-Agent Debate System** (892 lines)
   - `backend/multi_agent.py`
   - 5 specialized agents: Fundamental, Sentiment, Technical, Risk, Macro
   - Consensus-based analysis with confidence scoring
   - Indian market context integration

2. **Pinecone Vector Store** (127 lines)
   - `backend/vectorstore.py`
   - Cloud-native vector database
   - 384-dimensional embeddings
   - AWS us-east-1 deployment

3. **Local Embeddings** (71 lines)
   - `backend/embeddings.py`
   - SentenceTransformers (all-MiniLM-L6-v2)
   - No OpenAI dependencies

4. **Price Service** (173 lines)
   - `backend/price_service.py`
   - Real-time silver price tracking

## Integration Changes

### Modified Files
1. **backend/main.py**
   - Added multi-agent orchestrator initialization
   - Added vectorstore initialization
   - Added `/api/multi-agent/analyze` endpoint
   - Added `/api/vectorstore/search` endpoint

2. **backend/requirements.txt**
   - Added `pinecone-client==3.0.0`
   - Added `langchain==0.1.0`
   - Added `langchain-groq==0.0.1`
   - Added `langchain-core==0.1.0`
   - Added `torch==2.0.0`

3. **.env.example**
   - Added `PINECONE_API_KEY` configuration

### Import Path Updates
- Fixed `app.*` imports to work with `backend/` structure
- Updated `from app.embeddings` → `from embeddings`
- Updated multi_agent.py imports to use backend structure

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Backend (main.py)                 │
│                                                              │
│  ┌──────────────┐  ┌─────────────┐  ┌──────────────┐      │
│  │   SQL DB     │  │  Pinecone   │  │ Multi-Agent  │      │
│  │ (Narratives, │  │ (Vectors)   │  │ Orchestrator │      │
│  │  Articles,   │  │             │  │              │      │
│  │  Signals)    │  │             │  │ 5 Agents     │      │
│  └──────────────┘  └─────────────┘  └──────────────┘      │
│                                                              │
│  ┌──────────────┐  ┌─────────────┐  ┌──────────────┐      │
│  │   Vision     │  │   Data      │  │  Analytics   │      │
│  │  Pipeline    │  │ Collection  │  │ (Clustering, │      │
│  │ (OpenCV+LLM) │  │(News,Reddit)│  │  Sentiment)  │      │
│  └──────────────┘  └─────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │ Streamlit UI    │
                    │ (Frontend)      │
                    └─────────────────┘
```

## Features Available

### Production Features (from main)
✅ Computer vision for physical silver valuation
✅ Live multi-source data collection (News, Reddit, Yahoo Finance)
✅ SQL database with relational tracking
✅ Sophisticated analytics (clustering, correlation, velocity)
✅ Multi-provider LLM orchestration with fallbacks
✅ Real-time monitoring with WebSocket support
✅ Trading signal generation
✅ Stability monitoring (Paradoxical stability indicator)
✅ Streamlit UI

### New Features (from abhishek)
✅ Multi-agent debate system
✅ Pinecone vector database
✅ Local embeddings (no OpenAI dependency)
✅ Consensus-based narrative analysis
✅ Indian market context integration
✅ Confidence scoring

## API Endpoints

### New Endpoints
- `POST /api/multi-agent/analyze` - Multi-agent narrative analysis
- `GET /api/vectorstore/search?query=...&limit=5` - Vector similarity search

### Existing Endpoints (preserved)
- `GET /api/narratives` - List narratives
- `GET /api/trading-signal` - Get trading signal
- `POST /api/scan` - Computer vision scan
- `POST /api/collect-data` - Trigger data collection
- `POST /api/discover-narratives` - Run clustering
- And more...

## Deployment Requirements

### Environment Variables
```bash
# Required
GROQ_API_KEY=...
PINECONE_API_KEY=...

# Optional
GEMINI_API_KEY=...
NEWS_API_KEY=...
REDDIT_CLIENT_ID=...
REDDIT_CLIENT_SECRET=...
HF_TOKEN=...
```

### Dependencies
- Python 3.11+
- PostgreSQL or SQLite (for SQL database)
- Pinecone account (free tier available)
- Groq API account

## Testing Strategy

1. **Unit Tests**
   - Test multi-agent debate consensus
   - Test vectorstore CRUD operations
   - Test embeddings generation

2. **Integration Tests**
   - Test SQL + Pinecone dual storage
   - Test multi-agent with real narratives
   - Test vision pipeline with multi-agent

3. **End-to-End Tests**
   - Data collection → Analysis → Storage → UI
   - Multi-agent analysis workflow
   - Trading signal generation with multi-agent input

## Known Limitations

1. **Manual Conflict Resolution Required**
   - Some edge cases in multi-agent consensus may need refinement
   - Vectorstore and SQL synchronization may need monitoring

2. **Performance**
   - Multi-agent analysis takes 10-30 seconds for 5 agents
   - Pinecone cold start can take 5-10 seconds

3. **Configuration**
   - Requires both SQL database AND Pinecone setup
   - More complex deployment than single-branch solutions

## Next Steps

1. Test multi-agent endpoint with sample data
2. Verify vectorstore connectivity
3. Test SQL database integration
4. Update Streamlit UI to show multi-agent results
5. Add comprehensive error handling
6. Performance optimization
7. Add monitoring and logging

## Migration Guide

### From main branch
- No changes needed - all features preserved
- Add `PINECONE_API_KEY` to environment
- Install new dependencies: `pip install -r backend/requirements.txt`

### From abhishek branch
- Gain computer vision capabilities
- Gain live data collection
- Gain sophisticated analytics
- Need to set up SQL database
- Keep existing Pinecone integration

## Support

For issues or questions:
1. Check logs in backend startup
2. Verify all API keys are set
3. Test endpoints individually
4. Check database connectivity (both SQL and Pinecone)
