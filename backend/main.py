"""
SilverSentinel FastAPI Backend
Main application with REST API and WebSocket support
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
from typing import List, Dict, Any
from datetime import datetime

# Import core modules
from database import init_database, get_session, Narrative, TradingSignal, PriceData
from data_collection import collector
from narrative.resource_manager import resource_manager
from narrative.pattern_hunter import pattern_hunter
from narrative.lifecycle_tracker import lifecycle_tracker
from agent.trading_agent import trading_agent
from agent.stability_monitor import stability_monitor
from orchestrator import orchestrator


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
    # task = asyncio.create_task(run_continuous_monitoring())
    # background_tasks.add(task)
    
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
