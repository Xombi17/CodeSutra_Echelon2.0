# API Documentation

## Base URL
```
http://localhost:8000
```

## Authentication
Currently no authentication required (add for production)

---

## Endpoints

### Health Check
```http
GET /
```

**Response:**
```json
{
  "status": "online",
  "service": "SilverSentinel",
  "version": "1.0.0",
  "timestamp": "2024-01-24T12:00:00"
}
```

---

### Get All Narratives
```http
GET /api/narratives?active_only=true
```

**Parameters:**
- `active_only` (boolean, optional): Filter out dead narratives (default: true)

**Response:**
```json
{
  "narratives": [
    {
      "id": 1,
      "name": "Industrial Solar Demand",
      "phase": "growth",
      "strength": 85,
      "sentiment": 0.75,
      "birth_date": "2024-01-12T00:00:00",
      "age_days": 12,
      "article_count": 35
    }
  ],
  "count": 4,
  "timestamp": "2024-01-24T12:00:00"
}
```

---

### Get Narrative Details
```http
GET /api/narratives/{narrative_id}
```

**Response:**
```json
{
  "id": 1,
  "name": "Industrial Solar Demand",
  "phase": "growth",
  "strength": 85,
  "age_days": 12,
  "metrics": {
    "velocity_increase": 0.65,
    "price_correlation": 0.78,
    "current_velocity": 4.2,
    "conflicts": []
  },
  "sentiment": {
    "current_sentiment": 0.75,
    "trend": "improving",
    "article_count": 35
  }
}
```

---

### Get Trading Signal
```http
GET /api/trading-signal
```

**Response:**
```json
{
  "signal": {
    "action": "BUY",
    "confidence": 0.85,
    "strength": 85,
    "reasoning": "Narrative 'Industrial Solar Demand' in GROWTH phase...",
    "position_size": 1.2,
    "dominant_narrative": "Industrial Solar Demand",
    "price": 75234.50,
    "conflicts": 0
  },
  "explanation": "🟢 BUY Signal\nConfidence: 85%...",
  "timestamp": "2024-01-24T12:00:00"
}
```

---

### Get Current Price
```http
GET /api/price/current
```

**Response:**
```json
{
  "price": 75234.50,
  "timestamp": "2024-01-24T12:00:00",
  "source": "yfinance"
}
```

---

### Get Price History
```http
GET /api/price/history?hours=24
```

**Parameters:**
- `hours` (integer, optional): Hours of history to retrieve (default: 24)

**Response:**
```json
{
  "prices": [
    {
      "timestamp": "2024-01-24T11:00:00",
      "price": 75234.50,
      "open": 75100.00,
      "high": 75300.00,
      "low": 75050.00,
      "close": 75234.50,
      "volume": 250000
    }
  ],
  "count": 24,
  "hours": 24
}
```

---

### Get Stability Score
```http
GET /api/stability
```

**Response:**
```json
{
  "stability": {
    "score": 50,
    "risk_level": "MEDIUM",
    "warning": "🟡 Low volatility detected...",
    "recommendation": "Monitor for breakout signals",
    "volatility": "1.2%",
    "stable_days_streak": 5
  },
  "alert": null,
  "timestamp": "2024-01-24T12:00:00"
}
```

---

### Trigger Data Collection
```http
POST /api/collect-data
```

**Response:**
```json
{
  "success": true,
  "result": {
    "refreshed": ["news", "reddit", "price"],
    "articles_fetched": 15,
    "posts_fetched": 8,
    "prices_fetched": 24
  },
  "timestamp": "2024-01-24T12:00:00"
}
```

---

### Discover Narratives
```http
POST /api/discover-narratives
```

**Response:**
```json
{
  "success": true,
  "discovered": 2,
  "narratives": [
    {
      "name": "Mining Strike",
      "article_count": 12,
      "phase": "birth"
    }
  ],
  "timestamp": "2024-01-24T12:00:00"
}
```

---

### Track Lifecycles
```http
POST /api/track-lifecycles
```

**Response:**
```json
{
  "success": true,
  "message": "Lifecycle tracking completed",
  "timestamp": "2024-01-24T12:00:00"
}
```

---

### System Status
```http
GET /api/status
```

**Response:**
```json
{
  "status": "operational",
  "narratives": {
    "birth": 1,
    "growth": 2,
    "peak": 1,
    "reversal": 0,
    "death": 3
  },
  "orchestrator": {
    "groq_calls": 45,
    "ollama_calls": 12,
    "total_calls": 57,
    "success_rate": 0.98
  },
  "resource_manager": {
    "current_strategy": {
      "mode": "balanced",
      "news_interval_minutes": 30
    },
    "volatility": 1.5
  },
  "timestamp": "2024-01-24T12:00:00"
}
```

---

## WebSocket

### Live Updates
```
ws://localhost:8000/ws/live
```

**Messages Received:**
```json
{
  "type": "update",
  "price": 75234.50,
  "narratives": [...],
  "timestamp": "2024-01-24T12:00:00"
}
```

```json
{
  "type": "signal_update",
  "signal": {
    "action": "BUY",
    "confidence": 0.85,
    "reasoning": "..."
  },
  "timestamp": "2024-01-24T12:00:00"
}
```

---

## Error Responses

All endpoints may return standard HTTP error codes:

**404 Not Found:**
```json
{
  "detail": "Narrative not found"
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Internal server error"
}
```

---

## Interactive API Docs

FastAPI provides interactive documentation:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
