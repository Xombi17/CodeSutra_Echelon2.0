#!/bin/bash

echo "🚀 SilverSentinel Hybrid Intelligence Demo"
echo "=========================================="
echo ""

# Check if backend is running
if ! curl -s http://localhost:8000/ > /dev/null 2>&1; then
    echo "❌ Backend not running. Starting it now..."
    cd backend
    python -m uvicorn main:app --reload &
    BACKEND_PID=$!
    echo "⏳ Waiting for backend to start..."
    sleep 10
    cd ..
else
    echo "✅ Backend is already running"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 Test 1: Multi-Agent Analysis - Solar Demand"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
curl -s -X POST http://localhost:8000/api/narratives/analyze-multi-agent \
  -H "Content-Type: application/json" \
  -d @demo_data/solar_demand.json | python3 -m json.tool

echo ""
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 Test 2: Multi-Agent Analysis - Silver Squeeze"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
curl -s -X POST http://localhost:8000/api/narratives/analyze-multi-agent \
  -H "Content-Type: application/json" \
  -d @demo_data/silver_squeeze.json | python3 -m json.tool

echo ""
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 Test 3: Multi-Agent Analysis - EV Demand"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
curl -s -X POST http://localhost:8000/api/narratives/analyze-multi-agent \
  -H "Content-Type: application/json" \
  -d @demo_data/ev_demand.json | python3 -m json.tool

echo ""
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 Test 4: Get Enhanced Trading Signal"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
curl -s http://localhost:8000/api/trading-signal-enhanced | python3 -m json.tool

echo ""
echo ""
echo "✅ Demo complete!"
echo ""
echo "📚 Next steps:"
echo "   - API docs: http://localhost:8000/docs"
echo "   - Test hybrid analysis: POST /api/narratives/{id}/analyze-hybrid"
echo "   - View agent history: GET /api/narratives/{id}/agent-history"
echo ""

if [ ! -z "$BACKEND_PID" ]; then
    echo "🛑 Stopping backend (PID: $BACKEND_PID)..."
    kill $BACKEND_PID 2>/dev/null
fi
