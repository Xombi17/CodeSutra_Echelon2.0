"""
Test hybrid intelligence engine
"""
import pytest
import asyncio
from datetime import datetime, timedelta

from database import init_database, Narrative, Article, get_session
from hybrid_engine import hybrid_engine
from multi_agent.orchestrator import multi_agent_orchestrator


class TestHybridEngine:
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test database"""
        init_database()
        
        # Create test narrative
        session = get_session()
        narrative = Narrative(
            name="Test Solar Demand",
            phase="growth",
            strength=75,
            sentiment=0.8,
            article_count=50,
            mention_velocity=5.5,
            price_correlation=0.75
        )
        session.add(narrative)
        session.commit()
        
        # Add some test articles
        for i in range(5):
            article = Article(
                narrative_id=narrative.id,
                title=f"Test Article {i}: Solar demand rising",
                content="Silver demand from solar panels increasing rapidly",
                url=f"http://test.com/article{i}",
                source="test_news",
                published_at=datetime.utcnow() - timedelta(hours=i),
                sentiment_score=0.7,
                sentiment_label="positive"
            )
            session.add(article)
        
        session.commit()
        self.test_narrative_id = narrative.id
        session.close()
        
        yield
    
    @pytest.mark.asyncio
    async def test_hybrid_analysis_structure(self):
        """Test hybrid analysis returns correct structure"""
        print("\n🧪 Testing hybrid analysis structure...")
        
        session = get_session()
        narrative = session.query(Narrative).first()
        
        if narrative:
            result = await hybrid_engine.analyze_narrative_hybrid(narrative.id)
            
            # Check required fields
            assert "phase" in result
            assert "strength" in result
            assert "confidence" in result
            assert "analysis_method" in result
            assert "agent_consensus" in result
            assert "metrics" in result
            assert "explanation" in result
            
            # Check types
            assert isinstance(result["phase"], str)
            assert isinstance(result["strength"], int)
            assert isinstance(result["confidence"], float)
            assert isinstance(result["agent_consensus"], list)
            
            print(f"✅ Hybrid analysis structure valid")
            print(f"   Phase: {result['phase']}")
            print(f"   Strength: {result['strength']}")
            print(f"   Confidence: {result['confidence']:.2f}")
            print(f"   Method: {result['analysis_method']}")
        
        session.close()
    
    @pytest.mark.asyncio
    async def test_multi_agent_consensus(self):
        """Test multi-agent orchestrator"""
        print("\n🧪 Testing multi-agent consensus...")
        
        test_data = {
            "narrative_id": "test_narrative",
            "narrative_title": "Test Silver Demand",
            "historical_volume_75pct": 50.0,
            "recent_peak_volume": 80.0,
            "evidence": [
                {
                    "source_id": "test_1",
                    "source_type": "news",
                    "timestamp": "2024-01-24T12:00:00Z",
                    "text": "Silver demand surging due to solar panel manufacturing",
                    "author_reputation_score": 0.9,
                    "mention_count": 100,
                    "price_impact_correlation": 0.75
                }
            ]
        }
        
        result = await multi_agent_orchestrator.analyze_narrative_multi(test_data)
        
        # Check required fields
        assert "consensus_lifecycle_phase" in result
        assert "consensus_strength_score" in result
        assert "overall_confidence" in result
        assert "agent_votes" in result
        assert "num_agents" in result
        
        # Check agent votes
        assert len(result["agent_votes"]) == 5
        agent_names = [v["agent_name"] for v in result["agent_votes"]]
        assert "fundamental" in agent_names
        assert "sentiment" in agent_names
        assert "technical" in agent_names
        assert "risk" in agent_names
        assert "macro" in agent_names
        
        print(f"✅ Multi-agent consensus valid")
        print(f"   Consensus phase: {result['consensus_lifecycle_phase']}")
        print(f"   Strength: {result['consensus_strength_score']}")
        print(f"   Confidence: {result['overall_confidence']:.2f}")
        print(f"   Agents: {result['num_agents']}")
    
    @pytest.mark.asyncio
    async def test_confidence_weighting(self):
        """Test that confidence weighting works correctly"""
        print("\n🧪 Testing confidence weighting...")
        
        session = get_session()
        narrative = session.query(Narrative).first()
        
        if narrative:
            result = await hybrid_engine.analyze_narrative_hybrid(narrative.id)
            
            # Check that analysis method makes sense given confidence
            if result["confidence"] > 0.75:
                # High confidence should use agent result
                assert result["analysis_method"] in ["multi-agent", "hybrid"]
                print(f"✅ High confidence ({result['confidence']:.2f}) using agents")
            else:
                # Low confidence may use fallback
                assert result["analysis_method"] in ["multi-agent", "metrics-fallback", "hybrid"]
                print(f"✅ Medium/low confidence ({result['confidence']:.2f}) may use fallback")
        
        session.close()
    
    @pytest.mark.asyncio
    async def test_agent_vote_recording(self):
        """Test that agent votes can be recorded (structure test only)"""
        print("\n🧪 Testing agent vote structure...")
        
        # Just test that the database model exists and can be imported
        from database import AgentVote, NarrativeSnapshot
        
        # These models should be available
        assert AgentVote is not None
        assert NarrativeSnapshot is not None
        
        print("✅ Agent vote and snapshot models available")
    
    @pytest.mark.asyncio
    async def test_evidence_gathering(self):
        """Test evidence gathering for multi-agent analysis"""
        print("\n🧪 Testing evidence gathering...")
        
        session = get_session()
        narrative = session.query(Narrative).first()
        
        if narrative:
            # Test evidence gathering
            evidence = hybrid_engine._gather_evidence(narrative, session)
            
            assert isinstance(evidence, list)
            if len(evidence) > 0:
                # Check evidence structure
                assert "source_id" in evidence[0]
                assert "source_type" in evidence[0]
                assert "text" in evidence[0]
                assert "timestamp" in evidence[0]
                print(f"✅ Evidence gathered: {len(evidence)} items")
        
        session.close()


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "-s"])
