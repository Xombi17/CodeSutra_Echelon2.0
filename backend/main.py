# Startup Trace Timestamp: 2026-01-25 19:49
import sys
print("--- [DEBUG] STARTING MAIN.PY IMPORT PHASE ---"); sys.stdout.flush()
import os
print("Importing FastAPI...")
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, UploadFile, File, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
import aiofiles
import uuid
print("Importing Path...")
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import time
print("Importing Pydantic..."); sys.stdout.flush()
from pydantic import BaseModel, EmailStr, Field

# Import core modules
# NOTE: Heavy imports are now delayed to lifespan to ensure instant startup
# from data_collection import collector -> Moved to get_collector() dependency or lifecycle
# from narrative.resource_manager import resource_manager -> Moved
# from narrative.pattern_hunter import pattern_hunter -> Moved
# from narrative.lifecycle_tracker import lifecycle_tracker -> Moved
print("DEBUG: Importing forecaster..."); sys.stdout.flush()
from narrative.forecaster import forecaster
print("DEBUG: Importing trading_agent..."); sys.stdout.flush()
from agent.trading_agent import trading_agent
print("DEBUG: Importing stability_monitor..."); sys.stdout.flush()
from agent.stability_monitor import stability_monitor
print("DEBUG: Importing orchestrator..."); sys.stdout.flush()
from orchestrator import orchestrator

# Import vision module
print("DEBUG: Importing vision..."); sys.stdout.flush()
from vision import VisionPipeline, ValuationEngine

# Import database utilities
print("Importing Database..."); sys.stdout.flush()
from database import get_session

# Import hybrid intelligence system
print("DEBUG: Importing hybrid_engine..."); sys.stdout.flush()
from hybrid_engine import hybrid_engine
print("DEBUG: Importing multi_agent orchestrator..."); sys.stdout.flush()
from multi_agent.orchestrator import multi_agent_orchestrator

# Import authentication
print("DEBUG: Importing auth..."); sys.stdout.flush()
from auth import (
    create_user, authenticate_user, create_access_token,
    require_auth, optional_auth, TokenData
)
print("DEBUG: All imports complete!"); sys.stdout.flush()


# Pydantic models for request validation
class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=100)
    name: str = Field(..., min_length=1, max_length=100)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


# Background tasks with max size to prevent memory leak
MAX_BACKGROUND_TASKS = 100
background_tasks: set = set()


# Global placeholders for lazy loading
collector = None
resource_manager = None
pattern_hunter = None
lifecycle_tracker = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events with enhanced diagnostic logging"""
    print("🚀 [STARTUP] SilverSentinel backend is initializing...")
    
    # Initialize globals lazily
    global collector, resource_manager, pattern_hunter, lifecycle_tracker
    
    try:
        # Step 1: Initialize database
        print("📁 [STARTUP] Initializing database..."); sys.stdout.flush()
        from database import init_database
        init_database()
        
        # Step 2: Lazy load heavy modules
        print("📥 [STARTUP] Loading core modules..."); sys.stdout.flush()
        
        import data_collection
        collector = data_collection.collector
        
        import narrative.resource_manager
        resource_manager = narrative.resource_manager.resource_manager
        
        import narrative.pattern_hunter
        pattern_hunter = narrative.pattern_hunter.pattern_hunter
        
        import narrative.lifecycle_tracker
        lifecycle_tracker = narrative.lifecycle_tracker.lifecycle_tracker
        
        # Step 3: Start background monitoring
        print("📡 [STARTUP] Starting background tasks..."); sys.stdout.flush()
        
        async def delayed_monitoring():
            print("⏳ [STARTUP] Deferring background tasks for 10 seconds to allow health check...")
            await asyncio.sleep(10)
            print("🤖 [STARTUP] Starting continuous monitoring task...")
            # We must import run_continuous_monitoring here or have it available
            # Assuming it is defined later in this file, we can call it.
            # If not, we need to import it. But usually it is defined in main.py.
            # Checking if run_continuous_monitoring is available in main...
            # It seems it is defined below. 
            await run_continuous_monitoring()

        task = asyncio.create_task(delayed_monitoring())
        background_tasks.add(task)
        task.add_done_callback(lambda t: background_tasks.discard(t))
        print("📡 [STARTUP] Background tasks scheduled!"); sys.stdout.flush()
        
    except Exception as e:
        print(f"❌ [STARTUP] CRITICAL FAILURE DURING LIFESPAN: {e}"); sys.stdout.flush()
        import traceback
        traceback.print_exc()

    print("🌟 [STARTUP] Lifespan complete - server is ready to accept connections"); sys.stdout.flush()
    yield
    
    # Cleanup
    print("🛑 [SHUTDOWN] Shutting down SilverSentinel...")
    for task in background_tasks:
        task.cancel()


app = FastAPI(
    title="SilverSentinel API",
    description="Autonomous AI-driven silver market intelligence and trading platform",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware - Configure allowed origins from environment
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")
if os.getenv("CORS_ALLOW_ALL", "false").lower() == "true":
    ALLOWED_ORIGINS = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =====================
# Health & Status Endpoints
# =====================

@app.get("/")
@app.get("/health")
async def health_check():
    """Hugging Face Space health check endpoint"""
    return {
        "status": "online",
        "service": "SilverSentinel",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }


# =====================
# Authentication Endpoints
# =====================

@app.post("/api/auth/register", response_model=TokenResponse)
async def register(user_data: UserRegister):
    """
    Register a new user
    
    Returns JWT access token on success
    """
    user = create_user(user_data.email, user_data.password, user_data.name)
    if not user:
        raise HTTPException(
            status_code=400,
            detail="User with this email already exists"
        )
    
    token = create_access_token(user)
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in=24 * 3600  # 24 hours in seconds
    )


@app.post("/api/auth/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    """
    Authenticate user and return JWT token
    """
    user = authenticate_user(credentials.email, credentials.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )
    
    token = create_access_token(user)
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in=24 * 3600
    )


@app.get("/api/auth/me")
async def get_current_user_info(current_user: TokenData = Depends(require_auth)):
    """
    Get current authenticated user info
    """
    return {
        "user_id": current_user.user_id,
        "email": current_user.email,
        "name": current_user.name
    }


# =====================
# Narrative Endpoints
# =====================

@app.get("/api/narratives")
async def get_narratives(
    active_only: bool = True,
    page: int = Query(default=1, ge=1, description="Page number (1-indexed)"),
    limit: int = Query(default=20, ge=1, le=100, description="Items per page (1-100)")
):
    """
    Get all narratives with pagination
    
    Args:
        active_only: If True, only return non-dead narratives
        page: Page number (1-indexed)
        limit: Number of items per page (max 100)
    """
    session = get_session()
    
    try:
        query = session.query(Narrative)
        
        if active_only:
            query = query.filter(Narrative.phase != 'death')
        
        # Get total count for pagination metadata
        total_count = query.count()
        
        # Apply pagination
        offset = (page - 1) * limit
        narratives = query.order_by(Narrative.strength.desc()).offset(offset).limit(limit).all()
        
        # Calculate pagination metadata
        total_pages = (total_count + limit - 1) // limit  # Ceiling division
        
        return {
            "narratives": [n.to_dict() for n in narratives],
            "count": len(narratives),
            "pagination": {
                "page": page,
                "limit": limit,
                "total_count": total_count,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    
    finally:
        session.close()


@app.get("/api/narratives/{narrative_id}")
async def get_narrative_detail(narrative_id: int):
    """Get detailed information about a specific narrative"""
    status = lifecycle_tracker.get_narrative_status(narrative_id)
    
    if not status:
        raise HTTPException(status_code=404, detail="Narrative not found")
    
    return status


@app.get("/api/narratives/{narrative_id}/forecast")
async def get_narrative_forecast(narrative_id: int):
    """Get 48h forecast for a narrative"""
    session = get_session()
    try:
        narrative = session.query(Narrative).filter(Narrative.id == narrative_id).first()
        if not narrative:
            raise HTTPException(status_code=404, detail="Narrative not found")
        
        lifecycle_pred = forecaster.predict_lifecycle(narrative)
        price_pred = forecaster.predict_price_impact(narrative)
        
        return {
            "narrative_id": narrative_id,
            "lifecycle_forecast": lifecycle_pred,
            "price_impact_forecast": price_pred,
            "timestamp": datetime.utcnow().isoformat()
        }
    finally:
        session.close()


@app.get("/api/trading-signal")
async def get_trading_signal():
    """Get current trading recommendation"""
    signal = await trading_agent.generate_signal()
    
    return {
        "signal": {
            "action": signal.action,
            "confidence": signal.confidence,
            "strength": signal.strength,
            "reasoning": signal.reasoning,
            "position_size": signal.position_size,
            "dominant_narrative": signal.dominant_narrative,
            "price": signal.price_at_signal,
            "conflicts": len(signal.conflicts) if signal.conflicts else 0
        },
        "explanation": trading_agent.get_signal_explanation(signal),
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/api/price/current")
async def get_current_price():
    """Get current silver price in INR per gram"""
    # Fetch fresh price data from collector
    price_data = await collector.price_collector.fetch_price_data()
    
    if not price_data:
        raise HTTPException(status_code=503, detail="Unable to fetch current price")
    
    return {
        "price": price_data.get("current_price"),
        "previous_close": price_data.get("previous_close"),
        "change": price_data.get("price_change"),
        "change_percent": price_data.get("price_change_pct"),
        "timestamp": price_data.get("timestamp").isoformat() if price_data.get("timestamp") else datetime.utcnow().isoformat(),
        "source": price_data.get("source", "Silver Spot"),
        "currency": price_data.get("currency", "INR"),
        "unit": price_data.get("unit", "per gram"),
        "usd_inr_rate": price_data.get("usd_inr_rate")
    }


@app.get("/api/price/history")
async def get_price_history(
    hours: int = Query(default=24, ge=1, le=168, description="Hours of history (1-168)")
):
    """
    Get price history in INR per gram
    
    First tries to fetch from database, then falls back to yfinance for historical data
    """
    from datetime import timedelta
    
    session = get_session()
    try:
        # Calculate time range
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours)
        
        # Try to get from database first
        db_prices = session.query(PriceData).filter(
            PriceData.timestamp >= start_time
        ).order_by(PriceData.timestamp.asc()).all()
        
        if db_prices and len(db_prices) >= 5:
            # Use database data
            prices = [
                {
                    "price": round(p.price, 2),
                    "timestamp": p.timestamp.isoformat(),
                    "open": p.open_price,
                    "high": p.high_price,
                    "low": p.low_price,
                    "close": p.close_price
                }
                for p in db_prices
            ]
        else:
            # Fetch from yfinance and cache
            print("📡 [PRICE] Fetching historical data from yfinance..."); sys.stdout.flush()
            try:
                import yfinance as yf
                
                # Get silver ETF data (SLV) and convert to INR/gram
                ticker = yf.Ticker("SI=F")  # Silver futures
                # Use history instead of info
                hist_period = f"{min(hours // 24 + 1, 7)}d"
                hist = ticker.history(period=hist_period, interval="1h")
                
                # Get USD to INR rate reliably
                try:
                    usd_inr_ticker = yf.Ticker("USDINR=X")
                    usd_inr_hist = usd_inr_ticker.history(period="1d")
                    usd_inr_rate = usd_inr_hist["Close"].iloc[-1] if not usd_inr_hist.empty else 83.5
                    print(f"✅ [PRICE] USD/INR rate: {usd_inr_rate}"); sys.stdout.flush()
                except:
                    usd_inr_rate = 83.5
                    print("⚠️ [PRICE] Using default USD/INR rate: 83.5"); sys.stdout.flush()
                
                # Convert: Silver is in USD/troy oz, we need INR/gram
                INDIA_PREMIUM = 4.15
                conversion_factor = (usd_inr_rate / 31.1035) * INDIA_PREMIUM
                
                prices = []
                if not hist.empty:
                    for timestamp, row in hist.iterrows():
                        price_inr = row["Close"] * conversion_factor
                        price_entry = {
                            "price": round(price_inr, 2),
                            "timestamp": timestamp.isoformat(),
                            "open": round(row["Open"] * conversion_factor, 2) if "Open" in row else None,
                            "high": round(row["High"] * conversion_factor, 2) if "High" in row else None,
                            "low": round(row["Low"] * conversion_factor, 2) if "Low" in row else None,
                            "close": round(row["Close"] * conversion_factor, 2) if "Close" in row else None
                        }
                        prices.append(price_entry)
                        
                        # Cache in database
                        db_price = PriceData(
                            timestamp=timestamp.to_pydatetime(),
                            price=price_inr,
                            open_price=row["Open"] * conversion_factor if "Open" in row else None,
                            high_price=row["High"] * conversion_factor if "High" in row else None,
                            low_price=row["Low"] * conversion_factor if "Low" in row else None,
                            close_price=row["Close"] * conversion_factor if "Close" in row else None,
                            volume=row["Volume"] if "Volume" in row else None,
                            source="yfinance"
                        )
                        session.merge(db_price)
                    
                    session.commit()
                    print(f"✅ [PRICE] Cached {len(prices)} price points"); sys.stdout.flush()
                else:
                    print("⚠️ [PRICE] yfinance returned empty history"); sys.stdout.flush()
                    raise Exception("Empty history")
            
            except Exception as e:
                print(f"yfinance fetch failed: {e}, using simulated data")
                # Fallback to simulated data
                import random
                current_data = await collector.price_collector.fetch_price_data()
                current_price = current_data.get("current_price", 80.0) if current_data else 80.0
                
                prices = []
                points = min(hours * 4, 96)
                
                for i in range(points):
                    hours_ago = hours * (1 - i / points)
                    timestamp = datetime.utcnow() - timedelta(hours=hours_ago)
                    variation = random.uniform(-0.02, 0.02) * current_price
                    trend = (i / points - 0.5) * current_price * 0.01
                    price = current_price + variation + trend
                
                    prices.append({
                        "price": round(price, 2),
                        "timestamp": timestamp.isoformat(),
                    })
        
        return {
            "prices": prices,
            "count": len(prices),
            "hours": hours,
            "unit": "per gram",
            "currency": "INR"
        }
    finally:
        session.close()


@app.get("/api/stability")
async def get_stability_score():
    """Get current market stability assessment"""
    result = stability_monitor.calculate_stability_score()
    alert = stability_monitor.generate_alert()
    
    return {
        "stability": result,
        "alert": alert,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/api/collect-data")
async def trigger_data_collection():
    """Manually trigger data collection"""
    result = await resource_manager.refresh_data_sources(force=True)
    
    return {
        "success": True,
        "result": result,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/api/discover-narratives")
async def trigger_narrative_discovery():
    """Manually trigger narrative discovery"""
    narratives = await pattern_hunter.discover_narratives(days_back=7)
    
    if narratives:
        await pattern_hunter.save_narratives(narratives)
    
    return {
        "success": True,
        "discovered": len(narratives),
        "narratives": narratives,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/api/narratives/discover")
async def discover_narratives_endpoint(
    days_back: int = 7,
    top_n: int = 5
):
    """
    Discover top narratives from collected articles using AI-powered pipeline
    
    Query params:
    - days_back: Days of articles to analyze (default: 7)
    - top_n: Number of top narratives to return (default: 5)
    
    Returns:
        Dict with discovered narratives and processing metadata
    """
    try:
        # Import discovery engine
        from narrative.narrative_discovery import NarrativeDiscoveryEngine
        from data_collection import format_for_narrative_discovery
        
        # Collect data
        data = await collector.collect_all(news_days_back=days_back)
        
        # Format for discovery
        articles = format_for_narrative_discovery(data)
        
        # Run discovery pipeline
        engine = NarrativeDiscoveryEngine()
        narratives, metadata = await engine.discover_narratives(articles, top_n=top_n)
        
        return {
            "success": True,
            "narratives": [n.to_dict() for n in narratives],
            "metadata": metadata,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Narrative discovery failed: {str(e)}")


@app.post("/api/track-lifecycles")
async def trigger_lifecycle_tracking():
    """Manually trigger lifecycle tracking"""
    await lifecycle_tracker.track_all_narratives()
    
    return {
        "success": True,
        "message": "Lifecycle tracking completed",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/api/stats")
async def get_stats():
    """Get system statistics"""
    session = get_session()
    
    try:
        narrative_count = session.query(Narrative).count()
        active_narratives = session.query(Narrative).filter(Narrative.phase != 'death').count()
        signal_count = session.query(TradingSignal).count()
        price_count = session.query(PriceData).count()
        scan_count = session.query(SilverScan).count()
        
        # Get orchestrator stats
        orch_stats = orchestrator.get_stats()
        
        return {
            "narratives": {
                "total": narrative_count,
                "active": active_narratives
            },
            "signals": signal_count,
            "prices": price_count,
            "scans": scan_count,
            "orchestrator": orch_stats,
            "timestamp": datetime.utcnow().isoformat()
        }
    finally:
        session.close()


@app.get("/api/signals/history")
async def get_signal_history(
    page: int = Query(default=1, ge=1, description="Page number (1-indexed)"),
    limit: int = Query(default=10, ge=1, le=100, description="Items per page (1-100)")
):
    """Get trading signal history with pagination"""
    session = get_session()
    
    try:
        # Get total count
        total_count = session.query(TradingSignal).count()
        
        # Apply pagination
        offset = (page - 1) * limit
        signals = session.query(TradingSignal).order_by(
            TradingSignal.timestamp.desc()
        ).offset(offset).limit(limit).all()
        
        # Calculate pagination metadata
        total_pages = (total_count + limit - 1) // limit
        
        return {
            "signals": [s.to_dict() for s in signals],
            "count": len(signals),
            "pagination": {
                "page": page,
                "limit": limit,
                "total_count": total_count,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1
            }
        }
    finally:
        session.close()


@app.get("/api/prices")
async def get_prices(limit: int = 24):
    """Get recent price data"""
    session = get_session()
    
    try:
        # Convert limit to int if it's a string (FastAPI should handle this, but being explicit)
        limit_value = int(limit) if isinstance(limit, str) else limit
        
        prices = session.query(PriceData).order_by(
            PriceData.timestamp.desc()
        ).limit(limit_value).all()
        
        return {
            "prices": [p.to_dict() for p in prices],
            "count": len(prices)
        }
    finally:
        session.close()


@app.get("/api/status")
async def get_system_status():
    """Get overall system status"""
    session = get_session()
    
    try:
        # Count narratives by phase
        narrative_counts = {}
        for phase in ['birth', 'growth', 'peak', 'reversal', 'death']:
            count = session.query(Narrative).filter(Narrative.phase == phase).count()
            narrative_counts[phase] = count
        
        # Get orchestrator stats
        orchestrator_stats = orchestrator.get_stats()
        
        # Get resource manager status
        rm_status = resource_manager.get_status()
        
        return {
            "status": "operational",
            "narratives": narrative_counts,
            "orchestrator": orchestrator_stats,
            "resource_manager": rm_status,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    finally:
        session.close()


# =====================
# Hybrid Intelligence Endpoints
# =====================

@app.post("/api/narratives/{narrative_id}/analyze-hybrid")
async def analyze_narrative_hybrid(narrative_id: int):
    """
    Hybrid analysis combining metrics + multi-agent consensus
    Returns comprehensive analysis with both quantitative and qualitative insights
    """
    try:
        result = await hybrid_engine.analyze_narrative_hybrid(narrative_id)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/narratives/analyze-multi-agent")
async def analyze_multi_agent(narrative_data: Dict[str, Any]):
    """
    Pure multi-agent analysis (5 specialized agents debate)
    """
    try:
        result = await multi_agent_orchestrator.analyze_narrative_multi(narrative_data)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/simulate")
async def simulate_what_if(
    request: dict
):
    """
    Run "What-If" market simulation
    
    Request Body:
    {
        "narrative_ids": [1, 5],
        "factors": ["Silver Price +5%", "Miners Strike Ends"]
    }
    """
    try:
        session = get_session()
        narrative_ids = request.get("narrative_ids", [])
        factors = request.get("factors", [])
        
        # Fetch active narratives
        narratives = []
        if narrative_ids:
            db_narratives = session.query(Narrative).filter(Narrative.id.in_(narrative_ids)).all()
            narratives = [n.to_dict() for n in db_narratives]
        else:
            # Default to top 3 active narratives
            db_narratives = session.query(Narrative).filter(
                Narrative.phase.in_(['growth', 'peak'])
            ).order_by(Narrative.strength.desc()).limit(3).all()
            narratives = [n.to_dict() for n in db_narratives]
            
        session.close()
        
        # Run simulation
        result = await multi_agent_orchestrator.simulate_scenario(narratives, factors)
        
        return {
            "success": True,
            "simulation": result,
            "inputs": {
                "narratives_count": len(narratives),
                "factors": factors
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/trading-signal-enhanced")
async def get_enhanced_signal():
    """
    Trading signal with multi-agent debate reasoning
    """
    session = get_session()
    try:
        narratives = session.query(Narrative).filter(
            Narrative.phase != 'death'
        ).order_by(Narrative.strength.desc()).all()
        
        if not narratives:
            return {
                "success": True,
                "signal": {
                    "action": "HOLD",
                    "confidence": 0.0,
                    "strength": 0,
                    "reasoning": "No active narratives",
                    "position_size": 0.0
                }
            }
        
        # Analyze top narrative with hybrid engine
        dominant = narratives[0]
        hybrid_analysis = await hybrid_engine.analyze_narrative_hybrid(dominant.id)
        
        # Generate traditional signal
        signal = await trading_agent.generate_signal()
        
        # Enhance with agent insights
        enhanced_signal = {
            "action": signal.action,
            "confidence": signal.confidence,
            "strength": signal.strength,
            "reasoning": signal.reasoning,
            "position_size": signal.position_size,
            "dominant_narrative": signal.dominant_narrative,
            "price": signal.price_at_signal,
            "conflicts": len(signal.conflicts) if signal.conflicts else 0,
            "agent_insights": {
                "consensus": hybrid_analysis["explanation"],
                "votes": hybrid_analysis["agent_votes"],
                "minority_opinions": hybrid_analysis["minority_opinions"],
                "agent_confidence": hybrid_analysis["overall_confidence"]
            },
            "hybrid_analysis": {
                "method": hybrid_analysis["analysis_method"],
                "metrics": hybrid_analysis["metrics"]
            }
        }
        
        return {"success": True, "signal": enhanced_signal}
    finally:
        session.close()


@app.get("/api/narratives/{narrative_id}/agent-history")
async def get_agent_history(narrative_id: int):
    """
    Get historical agent votes for a narrative
    """
    session = get_session()
    try:
        votes = session.query(AgentVote).filter(
            AgentVote.narrative_id == narrative_id
        ).order_by(AgentVote.timestamp.desc()).limit(50).all()
        
        return {
            "narrative_id": narrative_id,
            "vote_count": len(votes),
            "votes": [v.to_dict() for v in votes]
        }
    finally:
        session.close()


# =====================
# Geographic Bias Transparency  
# =====================

@app.get("/api/bias/report")
async def get_bias_report():
    """
    Get geographic bias transparency report
    
    Shows:
    - Article distribution by region
    - Bias warnings
    - Adjustments applied to narratives
    """
    from narrative.geo_bias_handler import geo_bias_handler
    report = geo_bias_handler.get_transparency_report()
    return {"report": report, "timestamp": datetime.utcnow().isoformat()}


@app.get("/api/bias/test")
async def test_bias_adjustments():
    """
    Test geo bias adjustments on current narratives
    
    Returns before/after strength scores with explanations
    """
    from narrative.geo_bias_handler import geo_bias_handler
    
    session = get_session()
    try:
        narratives = session.query(Narrative).filter(
            Narrative.phase != 'death'
        ).all()
        
        results = []
        for narrative in narratives:
            # Calculate base strength (without geo bias)
            base_strength = narrative.strength
            
            # Calculate adjusted strength
            adjusted_strength = geo_bias_handler.calculate_adjusted_strength(
                narrative,
                base_strength
            )
            
            # Generate explanation
            explanation = geo_bias_handler.generate_adjustment_explanation(
                narrative,
                base_strength,
                adjusted_strength
            )
            
            results.append({
                "narrative_id": narrative.id,
                "narrative_name": narrative.name,
                "base_strength": base_strength,
                "adjusted_strength": adjusted_strength,
                "adjustment_factor": adjusted_strength / base_strength if base_strength > 0 else 1.0,
                "explanation": explanation
            })
        
        return {
            "narratives": results,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    finally:
        session.close()


# =====================
# Camera Scanning Endpoints
# =====================

# Initialize vision components
vision_pipeline = VisionPipeline()
valuation_engine = ValuationEngine()

UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@app.post("/api/scan")
async def scan_silver_object(
    image: UploadFile = File(...),
    user_id: Optional[str] = None
):
    """
    Analyze uploaded silver object image
    
    Returns comprehensive analysis including:
    - Object type (jewelry, coin, bar)
    - Purity (925, 950, 999)
    - Estimated weight
    - Valuation with range
    - Quality assessment
    - Market context from active narratives
    """
    try:
        # Save uploaded file
        file_id = str(uuid.uuid4())
        file_extension = Path(image.filename).suffix
        file_path = UPLOAD_DIR / f"{file_id}{file_extension}"
        
        async with aiofiles.open(file_path, 'wb') as f:
            content = await image.read()
            await f.write(content)
        
        # Run vision analysis
        analysis = await vision_pipeline.analyze_image(str(file_path))
        
        # Calculate valuation
        valuation = await valuation_engine.calculate_value(analysis)
        
        # Get market context (active narratives)
        session = get_session()
        active_narratives = session.query(Narrative).filter(
            Narrative.phase.in_(['growth', 'peak'])
        ).order_by(Narrative.strength.desc()).limit(3).all()
        
        market_context = "Current market: "
        if active_narratives:
            narrative = active_narratives[0]
            market_context += f"{narrative.name} narrative ({narrative.phase} phase) - prices may {'+' if narrative.sentiment > 0 else '-'}{'rise' if narrative.sentiment > 0 else 'fall'} 3-5% in coming days"
        else:
            market_context += "Stable conditions, no dominant narratives detected"
        
        # Store scan in database
        scan = SilverScan(
            id=file_id,
            user_id=user_id or "anonymous",
            image_path=str(file_path),
            detected_type=analysis.detected_type,
            purity=analysis.purity,
            estimated_weight=analysis.estimated_weight_g,
            estimated_dimensions={
                "width_mm": analysis.dimensions.width_mm,
                "height_mm": analysis.dimensions.height_mm,
                "thickness_mm": analysis.thickness_mm,
                "area_mm2": analysis.dimensions.area_mm2
            },
            valuation_min=valuation.value_range[0],
            valuation_max=valuation.value_range[1],
            confidence=valuation.overall_confidence,
            narrative_context={
                "narratives": [n.to_dict() for n in active_narratives],
                "market_summary": market_context
            }
        )
        
        session.add(scan)
        session.commit()
        scan_id = scan.id
        session.close()
        
        # Return comprehensive result
        return {
            "scan_id": scan_id,
            "detected_type": analysis.detected_type,
            "purity": analysis.purity,
            "purity_confidence": analysis.purity_confidence,
            "estimated_weight_g": analysis.estimated_weight_g,
            "dimensions": {
                "width_mm": round(analysis.dimensions.width_mm, 2),
                "height_mm": round(analysis.dimensions.height_mm, 2),
                "thickness_mm": round(analysis.thickness_mm, 2)
            },
            "valuation": valuation_engine.format_valuation_for_display(valuation),
            "quality": {
                "score": analysis.quality_score,
                "notes": analysis.quality_notes
            },
            "reference_object": {
                "detected": analysis.reference_detected,
                "type": analysis.reference_object.type if analysis.reference_object else None,
                "calibration_quality": analysis.reference_object.confidence if analysis.reference_object else None
            },
            "overall_confidence": analysis.overall_confidence,
            "market_context": market_context,
            "created_at": datetime.utcnow().isoformat()
        }
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.get("/api/scans/{scan_id}")
async def get_scan_result(scan_id: str):
    """Retrieve previous scan result by ID"""
    session = get_session()
    
    try:
        scan = session.query(SilverScan).filter(SilverScan.id == scan_id).first()
        
        if not scan:
            raise HTTPException(status_code=404, detail="Scan not found")
        
        return {
            "scan_id": scan.id,
            "detected_type": scan.detected_type,
            "purity": scan.purity,
            "weight_g": scan.estimated_weight,
            "dimensions": scan.estimated_dimensions,
            "valuation_range": {
                "min": scan.valuation_min,
                "max": scan.valuation_max,
                "currency": "INR"
            },
            "confidence": scan.confidence,
            "market_context": scan.narrative_context,
            "created_at": scan.created_at.isoformat()
        }
    
    finally:
        session.close()


@app.get("/api/scans/user/{user_id}")
async def get_user_scans(
    user_id: str,
    page: int = Query(default=1, ge=1, description="Page number (1-indexed)"),
    limit: int = Query(default=10, ge=1, le=50, description="Items per page (1-50)")
):
    """Get scan history for a user with pagination"""
    session = get_session()
    
    try:
        # Get total count for this user
        total_count = session.query(SilverScan).filter(
            SilverScan.user_id == user_id
        ).count()
        
        # Apply pagination
        offset = (page - 1) * limit
        scans = session.query(SilverScan).filter(
            SilverScan.user_id == user_id
        ).order_by(SilverScan.created_at.desc()).offset(offset).limit(limit).all()
        
        # Calculate pagination metadata
        total_pages = (total_count + limit - 1) // limit if total_count > 0 else 0
        
        return {
            "user_id": user_id,
            "scans": [scan.to_dict() for scan in scans],
            "count": len(scans),
            "pagination": {
                "page": page,
                "limit": limit,
                "total_count": total_count,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1
            }
        }
    
    finally:
        session.close()


# =====================
# WebSocket for Real-time Updates
# =====================

class ConnectionManager:
    """Manage WebSocket connections"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"✅ WebSocket connected (total: {len(self.active_connections)})")
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        print(f"👋 WebSocket disconnected (total: {len(self.active_connections)})")
    
    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass


manager = ConnectionManager()


@app.websocket("/ws/live")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time updates
    Sends price updates and narrative changes
    """
    await manager.connect(websocket)
    
    try:
        while True:
            # Send updates every 5 seconds
            await asyncio.sleep(5)
            
            # Get current price
            session = get_session()
            latest_price = session.query(PriceData).order_by(PriceData.timestamp.desc()).first()
            
            # Get active narratives
            narratives = session.query(Narrative).filter(
                Narrative.phase != 'death'
            ).order_by(Narrative.strength.desc()).limit(5).all()
            
            # Send update
            await websocket.send_json({
                "type": "update",
                "price": latest_price.price if latest_price else None,
                "narratives": [n.to_dict() for n in narratives],
                "timestamp": datetime.utcnow().isoformat()
            })
            
            session.close()
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"❌ WebSocket error: {e}")
        manager.disconnect(websocket)


# =====================
# Background Tasks
# =====================

async def run_continuous_monitoring():
    """
    Continuous background monitoring
    Runs data collection, narrative discovery, and lifecycle tracking
    """
    print("🤖 Starting continuous monitoring...")
    
    while True:
        try:
            # Every 5 minutes: check if data needs refresh
            await resource_manager.refresh_data_sources()
            
            # Every 30 minutes: discover new narratives
            if datetime.utcnow().minute % 30 == 0:
                narratives = await pattern_hunter.discover_narratives()
                if narratives:
                    await pattern_hunter.save_narratives(narratives)
            
            # Every 10 minutes: track lifecycle
            if datetime.utcnow().minute % 10 == 0:
                await lifecycle_tracker.track_all_narratives()
            
            # Broadcast updates to WebSocket clients
            signal = await trading_agent.generate_signal()
            await manager.broadcast({
                "type": "signal_update",
                "signal": {
                    "action": signal.action,
                    "confidence": signal.confidence,
                    "reasoning": signal.reasoning
                },
                "timestamp": datetime.utcnow().isoformat()
            })
            
            await asyncio.sleep(300)  # 5 minutes
        
        except Exception as e:
            print(f"❌ Background task error: {e}")
            await asyncio.sleep(300)


if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting SilverSentinel via uvicorn.run on port 7860..."); sys.stdout.flush()
    # Host 0.0.0.0 is crucial for Hugging Face Spaces
    # Pass app object directly to avoid re-importing 'main' module
    uvicorn.run(app, host="0.0.0.0", port=7860)
