"""
SilverSentinel FastAPI Backend
Main application with REST API and WebSocket support
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
import aiofiles
import uuid
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

# Import core modules
from database import init_database, get_session, Narrative, TradingSignal, PriceData, SilverScan, AgentVote
from data_collection import collector
from narrative.resource_manager import resource_manager
from narrative.pattern_hunter import pattern_hunter
from narrative.lifecycle_tracker import lifecycle_tracker
from narrative.forecaster import forecaster
from agent.trading_agent import trading_agent
from agent.stability_monitor import stability_monitor
from orchestrator import orchestrator

# Import vision module
from vision import VisionPipeline, ValuationEngine

# Import hybrid intelligence system
from hybrid_engine import hybrid_engine
from multi_agent.orchestrator import multi_agent_orchestrator


# Background tasks
background_tasks = set()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    print("🚀 Starting SilverSentinel backend...")
    
    # Initialize database
    init_database()
    print("✅ Database initialized")
    
    # Start background monitoring (optional - uncomment for production)
    # Start background monitoring (optional - uncomment for production)
    task = asyncio.create_task(run_continuous_monitoring())
    background_tasks.add(task)
    
    yield
    
    # Cleanup
    print("👋 Shutting down SilverSentinel...")
    for task in background_tasks:
        task.cancel()


app = FastAPI(
    title="SilverSentinel API",
    description="Autonomous AI-driven silver market intelligence and trading platform",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =====================
# REST API Endpoints
# =====================

@app.get("/")
async def root():
    """Health check"""
    return {
        "status": "online",
        "service": "SilverSentinel",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/api/narratives")
async def get_narratives(active_only: bool = True):
    """
    Get all narratives
    
    Args:
        active_only: If True, only return non-dead narratives
    """
    session = get_session()
    
    try:
        query = session.query(Narrative)
        
        if active_only:
            query = query.filter(Narrative.phase != 'death')
        
        narratives = query.order_by(Narrative.strength.desc()).all()
        
        return {
            "narratives": [n.to_dict() for n in narratives],
            "count": len(narratives),
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
    """Get current silver price"""
    session = get_session()
    
    try:
        latest = session.query(PriceData).order_by(PriceData.timestamp.desc()).first()
        
        if not latest:
            raise HTTPException(status_code=404, detail="No price data available")
        
        return {
            "price": latest.price,
            "timestamp": latest.timestamp.isoformat(),
            "source": latest.source
        }
    
    finally:
        session.close()


@app.get("/api/price/history")
async def get_price_history(hours: int = 24):
    """Get price history"""
    session = get_session()
    
    try:
        from datetime import timedelta
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        
        prices = session.query(PriceData).filter(
            PriceData.timestamp >= cutoff
        ).order_by(PriceData.timestamp).all()
        
        return {
            "prices": [p.to_dict() for p in prices],
            "count": len(prices),
            "hours": hours
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
async def get_signal_history(limit: int = 10):
    """Get trading signal history"""
    session = get_session()
    
    try:
        signals = session.query(TradingSignal).order_by(
            TradingSignal.timestamp.desc()
        ).limit(limit).all()
        
        return {
            "signals": [s.to_dict() for s in signals],
            "count": len(signals)
        }
    finally:
        session.close()


@app.get("/api/prices")
async def get_prices(limit: int = 24):
    """Get recent price data"""
    session = get_session()
    
    try:
        prices = session.query(PriceData).order_by(
            PriceData.timestamp.desc()
        ).limit(limit).all()
        
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
                "consensus": hybrid_analysis["agent_consensus"],
                "minority_opinions": hybrid_analysis["minority_opinions"],
                "agent_confidence": hybrid_analysis["confidence"]
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
async def get_user_scans(user_id: str, limit: int = 10):
    """Get scan history for a user"""
    session = get_session()
    
    try:
        scans = session.query(SilverScan).filter(
            SilverScan.user_id == user_id
        ).order_by(SilverScan.created_at.desc()).limit(limit).all()
        
        return {
            "user_id": user_id,
            "scans": [scan.to_dict() for scan in scans],
            "count": len(scans)
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
            
            session.close()
            
            # Send update
            await websocket.send_json({
                "type": "update",
                "price": latest_price.price if latest_price else None,
                "narratives": [n.to_dict() for n in narratives],
                "timestamp": datetime.utcnow().isoformat()
            })
    
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
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
