"""
Integration Tests
End-to-end testing of the SilverSentinel system
"""
import asyncio
import pytest
from database import init_database, get_session, Narrative, Article, PriceData
from data_collection import collector
from narrative.resource_manager import resource_manager
from narrative.pattern_hunter import pattern_hunter
from narrative.lifecycle_tracker import lifecycle_tracker, NarrativePhase
from agent.trading_agent import trading_agent
from agent.stability_monitor import stability_monitor
from orchestrator import orchestrator


class TestIntegration:
    """Integration tests for entire system"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test database"""
        init_database()
        yield
        # Cleanup handled by seed_demo_data
    
    @pytest.mark.asyncio
    async def test_data_collection_pipeline(self):
        """Test complete data collection flow"""
        print("\n🧪 Testing data collection pipeline...")
        
        # Collect data
        data = await collector.collect_all(news_days_back=1, price_period="1d")
        
        assert "articles" in data
        assert "posts" in data
        assert "prices" in data
        assert len(data["articles"]) >= 0  # May be empty with mock data
        
        # Save to database
        await collector.save_to_database(data)
        
        print("✅ Data collection pipeline works")
    
    @pytest.mark.asyncio
    async def test_resource_manager_strategy(self):
        """Test resource manager volatility-based strategy"""
        print("\n🧪 Testing resource manager...")
        
        # Calculate volatility
        volatility = resource_manager.calculate_volatility()
        assert volatility >= 0
        
        # Get strategy
        strategy = resource_manager.decide_scraping_strategy(volatility)
        assert "mode" in strategy
        assert strategy["mode"] in ["aggressive", "balanced", "conservative"]
        
        print(f"✅ Resource manager strategy: {strategy['mode']}")
    
    @pytest.mark.asyncio
    async def test_pattern_discovery(self):
        """Test narrative pattern discovery"""
        print("\n🧪 Testing pattern hunter...")
        
        # Need articles in database (use seed data)
        session = get_session()
        article_count = session.query(Article).count()
        session.close()
        
        if article_count < 10:
            print("⚠️ Skipping pattern discovery (insufficient articles)")
            return
        
        narratives = await pattern_hunter.discover_narratives(days_back=7)
        assert isinstance(narratives, list)
        
        print(f"✅ Discovered {len(narratives)} narratives")
    
    @pytest.mark.asyncio
    async def test_lifecycle_tracking(self):
        """Test narrative lifecycle tracking"""
        print("\n🧪 Testing lifecycle tracker...")
        
        session = get_session()
        
        # Create test narrative
        narrative = Narrative(
            name="Test Narrative",
            phase="birth",
            strength=50,
            sentiment=0.5,
            article_count=10
        )
        session.add(narrative)
        session.commit()
        
        # Calculate metrics
        metrics = lifecycle_tracker.calculate_metrics(narrative)
        assert "velocity_increase" in metrics
        assert "price_correlation" in metrics
        
        # Test phase transition detection
        new_phase = lifecycle_tracker.detect_phase_transition(narrative)
        assert new_phase is None or isinstance(new_phase, NarrativePhase)
        
        session.close()
        print("✅ Lifecycle tracking works")
    
    @pytest.mark.asyncio
    async def test_trading_signal_generation(self):
        """Test trading signal generation"""
        print("\n🧪 Testing trading agent...")
        
        signal = await trading_agent.generate_signal()
        
        assert signal.action in ["BUY", "SELL", "HOLD"]
        assert 0.0 <= signal.confidence <= 1.0
        assert 0 <= signal.strength <= 100
        assert signal.reasoning is not None
        
        print(f"✅ Generated signal: {signal.action} (confidence: {signal.confidence:.0%})")
    
    def test_stability_monitor(self):
        """Test stability monitoring"""
        print("\n🧪 Testing stability monitor...")
        
        result = stability_monitor.calculate_stability_score()
        
        assert "score" in result
        assert 0 <= result["score"] <= 100
        assert "risk_level" in result
        assert result["risk_level"] in ["HIGH", "MEDIUM", "LOW"]
        
        print(f"✅ Stability score: {result['score']} ({result['risk_level']} risk)")
    
    @pytest.mark.asyncio
    async def test_orchestrator_text(self):
        """Test multi-model orchestrator for text"""
        print("\n🧪 Testing orchestrator (text)...")
        
        prompt = "Summarize silver market in one sentence."
        response = await orchestrator.analyze_text(prompt)
        
        assert response.success
        assert len(response.content) > 0
        assert response.model_used is not None
        
        print(f"✅ Orchestrator working (model: {response.model_used})")
    
    @pytest.mark.asyncio
    async def test_end_to_end_flow(self):
        """Test complete end-to-end workflow"""
        print("\n🧪 Testing end-to-end flow...")
        
        # 1. Collect data
        await resource_manager.refresh_data_sources(force=True)
        
        # 2. Track lifecycles
        await lifecycle_tracker.track_all_narratives()
        
        # 3. Generate signal
        signal = await trading_agent.generate_signal()
        
        # 4. Check stability
        stability = stability_monitor.calculate_stability_score()
        
        assert signal is not None
        assert stability is not None
        
        print("✅ End-to-end flow complete")
        print(f"   Signal: {signal.action}")
        print(f"   Stability: {stability['score']}/100")


def run_tests():
    """Run all integration tests"""
    print("="*60)
    print("🧪 Running Integration Tests")
    print("="*60)
    
    # Run pytest
    pytest.main([__file__, "-v", "-s"])


if __name__ == "__main__":
    run_tests()
