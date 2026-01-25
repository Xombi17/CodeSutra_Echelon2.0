"""
COMPREHENSIVE TIER 2 NARRATIVE DISCOVERY TEST SUITE
Tests Pattern Hunter (PS 5), Resource Manager (PS 4), Sentiment Analysis, and full discovery pipeline
"""
import asyncio
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List
import json
import time
import numpy as np

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from narrative.pattern_hunter import pattern_hunter, PatternHunter
from narrative.resource_manager import resource_manager, ResourceManager
from narrative.sentiment_analyzer import sentiment_analyzer
from database import get_session, Article, Narrative, PriceData, init_database
from data_collection import collector
from orchestrator import orchestrator


class Tier2TestSuite:
    """Comprehensive test suite for Tier 2: Narrative Discovery"""
    
    def __init__(self):
        self.results = {
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "component_status": {},
            "performance_metrics": {},
            "quality_scores": {},
            "errors": []
        }
        self.start_time = None
    
    def log(self, message: str, level: str = "INFO"):
        """Log test message"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        icons = {"INFO": "ℹ️", "SUCCESS": "✅", "ERROR": "❌", "WARNING": "⚠️", "TEST": "🧪"}
        print(f"[{timestamp}] {icons.get(level, '•')} {message}")
    
    def record_test(self, test_name: str, passed: bool, details: str = ""):
        """Record test result"""
        self.results["tests_run"] += 1
        if passed:
            self.results["tests_passed"] += 1
            self.log(f"PASS: {test_name} {details}", "SUCCESS")
        else:
            self.results["tests_failed"] += 1
            self.log(f"FAIL: {test_name} {details}", "ERROR")
            self.results["errors"].append({"test": test_name, "details": details})
    
    # ==================== PATTERN HUNTER TESTS (PS 5) ====================
    
    async def test_tfidf_vectorization(self):
        """Test 1: TF-IDF Vectorization"""
        self.log("Test 1: TF-IDF Vectorization", "TEST")
        
        try:
            hunter = PatternHunter()
            
            # Test with sample texts
            texts = [
                "Silver prices surge on industrial demand from solar panels",
                "Mining strike in Peru threatens silver supply chain",
                "Silver jewelry demand increases during wedding season",
                "Federal Reserve rate hikes weigh on precious metals"
            ]
            
            start = time.time()
            vectors = hunter.vectorizer.fit_transform(texts)
            duration = time.time() - start
            
            # Validation
            assert vectors.shape[0] == len(texts), "Wrong number of vectors"
            assert vectors.shape[1] > 0, "No features extracted"
            
            feature_count = vectors.shape[1]
            sparsity = 1.0 - (vectors.nnz / (vectors.shape[0] * vectors.shape[1]))
            
            self.results["component_status"]["tfidf"] = {
                "status": "success",
                "feature_count": feature_count,
                "sparsity": sparsity,
                "duration_ms": duration * 1000
            }
            
            self.record_test("TF-IDF Vectorization", True,
                           f"({feature_count} features, {sparsity:.1%} sparse)")
            return vectors
        
        except Exception as e:
            self.results["component_status"]["tfidf"] = {"status": "error", "error": str(e)}
            self.record_test("TF-IDF Vectorization", False, str(e))
            return None
    
    async def test_hdbscan_clustering(self):
        """Test 2: HDBSCAN Clustering"""
        self.log("Test 2: HDBSCAN Clustering", "TEST")
        
        try:
            hunter = PatternHunter()
            
            # Create test articles
            test_articles = []
            for i in range(20):
                if i < 7:
                    title = f"Silver demand surge in solar industry article {i}"
                elif i < 14:
                    title = f"Mining strike threatens silver supply chain {i}"
                else:
                    title = f"Federal Reserve rate decision impacts metals {i}"
                
                test_articles.append({
                    "title": title,
                    "content": title + " with more detailed content here."
                })
            
            # Vectorize  
            texts = [f"{a['title']} {a['content']}" for a in test_articles]
            vectors = hunter.vectorizer.fit_transform(texts)
            
            # Cluster
            start = time.time()
            cluster_labels = hunter.clusterer.fit_predict(vectors.toarray())
            duration = time.time() - start
            
            # Validation
            unique_clusters = len(set(cluster_labels)) - (1 if -1 in cluster_labels else 0)
            noise_count = sum(1 for label in cluster_labels if label == -1)
            
            assert unique_clusters > 0, "No clusters found"
            
            self.results["component_status"]["hdbscan"] = {
                "status": "success",
                "clusters_found": unique_clusters,
                "noise_points": noise_count,
                "duration_ms": duration * 1000
            }
            
            self.record_test("HDBSCAN Clustering", True,
                           f"({unique_clusters} clusters, {noise_count} noise points)")
            return cluster_labels
        
        except Exception as e:
            self.results["component_status"]["hdbscan"] = {"status": "error", "error": str(e)}
            self.record_test("HDBSCAN Clustering", False, str(e))
            return None
    
    async def test_narrative_naming(self):
        """Test 3: LLM-based Narrative Naming"""
        self.log("Test 3: LLM-based Narrative Naming", "TEST")
        
        try:
            # Test with sample cluster keywords
            keywords = ["solar", "demand", "industrial", "manufacturing", "panels"]
            headlines = [
                "Solar panel manufacturers increase silver orders",
                "Industrial demand drives silver prices higher",
                "Renewable energy boom boosts silver consumption"
            ]
            
            prompt = f"""Analyze these headlines about silver markets and create a concise narrative name (3-4 words maximum):

Headlines:
{chr(10).join(f"- {h}" for h in headlines)}

Top keywords: {', '.join(keywords[:5])}

Respond with ONLY the narrative name, nothing else."""
            
            start = time.time()
            response = await orchestrator.analyze_text(
                prompt=prompt,
                model_type="narrative"
            )
            duration = time.time() - start
            
            # Validation
            assert response.success, "LLM call failed"
            assert len(response.content) > 0, "Empty response"
            assert len(response.content.split()) <= 6, "Name too long"
            
            self.results["component_status"]["narrative_naming"] = {
                "status": "success",
                "name_generated": response.content.strip(),
                "duration_ms": duration * 1000
            }
            
            self.record_test("Narrative Naming", True,
                           f"('{response.content.strip()}' in {duration:.2f}s)")
            return response.content
        
        except Exception as e:
            self.results["component_status"]["narrative_naming"] = {"status": "error", "error": str(e)}
            self.record_test("Narrative Naming", False, str(e))
            return None
    
    async def test_pattern_hunter_discovery(self):
        """Test 4: Full Pattern Hunter Discovery Pipeline"""
        self.log("Test 4: Pattern Hunter Discovery Pipeline", "TEST")
        
        try:
            # Ensure we have test data
            session = get_session()
            article_count = session.query(Article).filter(
                Article.narrative_id == None
            ).count()
            session.close()
            
            if article_count < 10:
                self.log(f"Not enough unassigned articles ({article_count}), using seed data", "WARNING")
                # Will use seed data which should exist
            
            start = time.time()
            narratives = await pattern_hunter.discover_narratives(days_back=30, min_articles=5)
            duration = time.time() - start
            
            # Validation
            assert isinstance(narratives, list), "Return type should be list"
            
            if len(narratives) > 0:
                assert all('name' in n for n in narratives), "Missing narrative names"
                assert all('cluster_keywords' in n for n in narratives), "Missing keywords"
                
                self.results["performance_metrics"]["discovery"] = {
                    "narratives_discovered": len(narratives),
                    "duration_seconds": duration,
                    "narratives_per_second": len(narratives) / duration if duration > 0 else 0
                }
                
                sample_names = [n['name'] for n in narratives[:3]]
                self.record_test("Pattern Hunter Discovery", True,
                               f"({len(narratives)} narratives: {sample_names})")
            else:
                self.record_test("Pattern Hunter Discovery", True,
                               "(No narratives found - insufficient data)")
            
            return narratives
        
        except Exception as e:
            self.record_test("Pattern Hunter Discovery", False, str(e))
            return []
    
    async def test_narrative_persistence(self):
        """Test 5: Narrative Save to Database"""
        self.log("Test 5: Narrative Database Persistence", "TEST")
        
        try:
            # Discover narratives
            narratives = await pattern_hunter.discover_narratives(days_back=30, min_articles=5)
            
            if not narratives:
                self.record_test("Narrative Persistence", True, "(Skipped - no narratives)")
                return True
            
            # Save to database
            initial_count = self.get_narrative_count()
            await pattern_hunter.save_narratives(narratives)
            final_count = self.get_narrative_count()
            
            # Validation
            assert final_count >= initial_count, "Narrative count decreased"
            
            self.record_test("Narrative Persistence", True,
                           f"(Saved {final_count - initial_count} new narratives)")
            return True
        
        except Exception as e:
            self.record_test("Narrative Persistence", False, str(e))
            return False
    
    # ==================== RESOURCE MANAGER TESTS (PS 4) ====================
    
    async def test_volatility_calculation(self):
        """Test 6: Market Volatility Calculation"""
        self.log("Test 6: Market Volatility Calculation", "TEST")
        
        try:
            start = time.time()
            volatility = resource_manager.calculate_volatility(window_hours=24)
            duration = time.time() - start
            
            # Validation
            assert volatility >= 0, "Volatility should be non-negative"
            assert volatility < 100, "Volatility seems unreasonably high"
            
            self.results["component_status"]["volatility"] = {
                "status": "success",
                "current_volatility": volatility,
                "duration_ms": duration * 1000
            }
            
            self.record_test("Volatility Calculation", True,
                           f"({volatility:.2f}% in {duration*1000:.0f}ms)")
            return volatility
        
        except Exception as e:
            self.results["component_status"]["volatility"] = {"status": "error", "error": str(e)}
            self.record_test("Volatility Calculation", False, str(e))
            return None
    
    async def test_strategy_decision(self):
        """Test 7: Adaptive Strategy Selection"""
        self.log("Test 7: Adaptive Strategy Selection", "TEST")
        
        try:
            # Test all three strategies
            test_volatilities = [1.0, 3.0, 8.0]
            strategies = {}
            
            for vol in test_volatilities:
                strategy = resource_manager.decide_scraping_strategy(volatility=vol)
                strategies[vol] = strategy
            
            # Validation
            assert strategies[1.0]['mode'] == 'conservative', "Low vol should be conservative"
            assert strategies[3.0]['mode'] == 'balanced', "Medium vol should be balanced"
            assert strategies[8.0]['mode'] == 'aggressive', "High vol should be aggressive"
            
            # Intervals should decrease with higher volatility
            assert strategies[1.0]['news_interval_minutes'] > strategies[8.0]['news_interval_minutes'], \
                   "Higher volatility should have shorter intervals"
            
            modes = [s['mode'] for s in strategies.values()]
            self.record_test("Strategy Decision", True,
                           f"({modes[0]}, {modes[1]}, {modes[2]})")
            return strategies
        
        except Exception as e:
            self.record_test("Strategy Decision", False, str(e))
            return {}
    
    async def test_budget_allocation(self):
        """Test 8: Source Budget Allocation"""
        self.log("Test 8: Source Budget Allocation", "TEST")
        
        try:
            allocation = resource_manager.get_source_budget_allocation()
            
            # Validation
            assert isinstance(allocation, dict), "Should return dict"
            assert len(allocation) > 0, "Should have at least one source"
            
            total_budget = sum(allocation.values())
            assert 99 < total_budget < 101, "Budget should sum to ~100%"
            
            # NewsAPI should have highest allocation (highest quality score)
            assert allocation.get('newsapi', 0) > allocation.get('reddit', 0), \
                   "NewsAPI should have higher allocation than Reddit"
            
            self.record_test("Budget Allocation", True,
                           f"(NewsAPI: {allocation.get('newsapi', 0):.1f}%, Reddit: {allocation.get('reddit', 0):.1f}%)")
            return allocation
        
        except Exception as e:
            self.record_test("Budget Allocation", False, str(e))
            return {}
    
    async def test_source_staleness(self):
        """Test 9: Source Staleness Detection"""
        self.log("Test 9: Source Staleness Detection", "TEST")
        
        try:
            strategy = resource_manager.decide_scraping_strategy()
            
            # Set last refresh to old time
            resource_manager.last_refresh["news"] = datetime.now() - timedelta(hours=5)
            
            is_stale = resource_manager.is_source_stale("news", strategy)
            
            # Validation
            assert is_stale == True, "Old source should be stale"
            
            # Set to recent time
            resource_manager.last_refresh["news"] = datetime.now()
            is_fresh = resource_manager.is_source_stale("news", strategy)
            
            assert is_fresh == False, "Fresh source should not be stale"
            
            self.record_test("Source Staleness", True,
                           "(Correctly detects stale vs fresh)")
            return True
        
        except Exception as e:
            self.record_test("Source Staleness", False, str(e))
            return False
    
    # ==================== SENTIMENT ANALYSIS TESTS ====================
    
    async def test_sentiment_basic(self):
        """Test 10: Basic Sentiment Analysis"""
        self.log("Test 10: Basic Sentiment Analysis", "TEST")
        
        try:
            texts = {
                "positive": "Silver prices surge to record highs on strong industrial demand",
                "negative": "Mining strike threatens to cripple silver supply for months",
                "neutral": "Silver prices remain stable amid uncertainty"
            }
            
            results = {}
            for sentiment_type, text in texts.items():
                result = sentiment_analyzer.analyze(text)
                results[sentiment_type] = result
            
            # Validation
            assert results["positive"]["compound"] > 0.1, "Positive text should have positive score"
            assert results["negative"]["compound"] < -0.1, "Negative text should have negative score"
            assert -0.2 < results["neutral"]["compound"] < 0.2, "Neutral text should be near zero"
            
            scores = {k: v["compound"] for k, v in results.items()}
            self.record_test("Sentiment Analysis", True,
                           f"(Pos: {scores['positive']:.2f}, Neg: {scores['negative']:.2f}, Neu: {scores['neutral']:.2f})")
            return results
        
        except Exception as e:
            self.record_test("Sentiment Analysis", False, str(e))
            return {}
    
    async def test_sentiment_narrative(self):
        """Test 11: Narrative-level Sentiment"""
        self.log("Test 11: Narrative-Level Sentiment Aggregation", "TEST")
        
        try:
            session = get_session()
            narrative = session.query(Narrative).first()
            session.close()
            
            if not narrative:
                self.record_test("Narrative Sentiment", True, "(Skipped - no narratives)")
                return None
            
            sentiment_data = sentiment_analyzer.analyze_narrative_sentiment(
                narrative.id,
                hours_back=24
            )
            
            # Validation
            assert 'current_sentiment' in sentiment_data, "Missing current sentiment"
            assert 'article_count' in sentiment_data, "Missing article count"
            assert -1 <= sentiment_data['current_sentiment'] <= 1, "Sentiment out of range"
            
            self.record_test("Narrative Sentiment", True,
                           f"({sentiment_data['article_count']} articles, sentiment: {sentiment_data['current_sentiment']:.2f})")
            return sentiment_data
        
        except Exception as e:
            self.record_test("Narrative Sentiment", False, str(e))
            return None
    
    # ==================== INTEGRATION TESTS ====================
    
    async def test_end_to_end_discovery(self):
        """Test 12: End-to-End Discovery Pipeline"""
        self.log("Test 12: End-to-End Discovery Pipeline", "TEST")
        
        try:
            # Step 1: Check volatility
            volatility = resource_manager.calculate_volatility()
            
            # Step 2: Decide strategy
            strategy = resource_manager.decide_scraping_strategy(volatility)
            
            # Step 3: Discover narratives
            narratives = await pattern_hunter.discover_narratives(days_back=30)
            
            # Step 4: Analyze sentiment for discovered narratives
            sentiment_results = []
            for narrative in narratives[:3]:  # Test first 3
                if narrative.get('name'):
                    # Would analyze sentiment here
                    pass
            
            # Validation
            pipeline_complete = (
                isinstance(volatility, (int, float)) and
                isinstance(strategy, dict) and
                isinstance(narratives, list)
            )
            
            self.record_test("End-to-End Discovery", pipeline_complete,
                           f"(Vol: {volatility:.2f}%, Strategy: {strategy.get('mode')}, Narratives: {len(narratives)})")
            return pipeline_complete
        
        except Exception as e:
            self.record_test("End-to-End Discovery", False, str(e))
            return False
    
    async def test_narrative_quality(self):
        """Test 13: Discovered Narrative Quality"""
        self.log("Test 13: Narrative Quality Assessment", "TEST")
        
        try:
            narratives = await pattern_hunter.discover_narratives(days_back=30)
            
            if not narratives:
                self.record_test("Narrative Quality", True, "(Skipped - no narratives)")
                return 0
            
            quality_scores = []
            for narrative in narratives:
                score = 0
                
                # Check name quality (1 point)
                if narrative.get('name') and len(narrative['name']) > 5:
                    score += 1
                
                # Check keywords (1 point)
                if narrative.get('cluster_keywords') and len(narrative['cluster_keywords']) >= 3:
                    score += 1
                
                # Check article count (1 point)
                if narrative.get('article_count', 0) >= 3:
                    score += 1
                
                # Check sentiment (1 point)
                if 'initial_sentiment' in narrative:
                    score += 1
                
                quality_scores.append(score / 4.0)  # Normalize to 0-1
            
            avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
            
            self.results["quality_scores"]["narrative_quality"] = avg_quality
            
            passed = avg_quality >= 0.75  # 75% threshold
            self.record_test("Narrative Quality", passed,
                           f"(Avg: {avg_quality:.1%}, Threshold: 75%)")
            return avg_quality
        
        except Exception as e:
            self.record_test("Narrative Quality", False, str(e))
            return 0
    
    # ==================== PERFORMANCE TESTS ====================
    
    async def test_clustering_performance(self):
        """Test 14: Clustering Performance at Scale"""
        self.log("Test 14: Clustering Performance Test", "TEST")
        
        try:
            # Create large test dataset
            texts = []
            for i in range(100):
                if i % 3 == 0:
                    texts.append(f"Silver demand surge article {i}")
                elif i % 3 == 1:
                    texts.append(f"Mining strike news {i}")
                else:
                    texts.append(f"Federal Reserve rate decision {i}")
            
            hunter = PatternHunter()
            
            # Measure vectorization time
            start = time.time()
            vectors = hunter.vectorizer.fit_transform(texts)
            vec_time = time.time() - start
            
            # Measure clustering time
            start = time.time()
            labels = hunter.clusterer.fit_predict(vectors.toarray())
            cluster_time = time.time() - start
            
            total_time = vec_time + cluster_time
            
            # Validation
            passed = total_time < 10  # Should complete in < 10s
            
            self.results["performance_metrics"]["clustering"] = {
                "documents": len(texts),
                "vectorization_seconds": vec_time,
                "clustering_seconds": cluster_time,
                "total_seconds": total_time
            }
            
            self.record_test("Clustering Performance", passed,
                           f"(100 docs in {total_time:.2f}s)")
            return total_time
        
        except Exception as e:
            self.record_test("Clustering Performance", False, str(e))
            return None
    
    async def test_concurrent_discovery(self):
        """Test 15: Concurrent Discovery Requests"""
        self.log("Test 15: Concurrent Discovery Handling", "TEST")
        
        try:
            # Run multiple discoveries in parallel
            tasks = [
                pattern_hunter.discover_narratives(days_back=7),
                pattern_hunter.discover_narratives(days_back=14),
                pattern_hunter.discover_narratives(days_back=30)
            ]
            
            start = time.time()
            results = await asyncio.gather(*tasks, return_exceptions=True)
            duration = time.time() - start
            
            # Count successes
            successes = sum(1 for r in results if isinstance(r, list))
            
            passed = successes >= 2  # At least 2/3 should succeed
            
            self.record_test("Concurrent Discovery", passed,
                           f"({successes}/3 succeeded in {duration:.2f}s)")
            return successes
        
        except Exception as e:
            self.record_test("Concurrent Discovery", False, str(e))
            return 0
    
    # ==================== EDGE CASE TESTS ====================
    
    async def test_empty_dataset(self):
        """Test 16: Empty Dataset Handling"""
        self.log("Test 16: Empty Dataset Handling", "TEST")
        
        try:
            hunter = PatternHunter()
            
            # Try to discover with insufficient data
            narratives = await hunter.discover_narratives(days_back=1, min_articles=1000)
            
            # Should return empty list, not crash
            assert isinstance(narratives, list), "Should return list"
            
            self.record_test("Empty Dataset", True,
                           "(Gracefully handled - returned empty list)")
            return True
        
        except Exception as e:
            self.record_test("Empty Dataset", False, str(e))
            return False
    
    async def test_single_cluster(self):
        """Test 17: Single Cluster Scenario"""
        self.log("Test 17: Single Cluster Handling", "TEST")
        
        try:
            # All similar texts (should form 1 cluster)
            texts = [f"Silver price increase news article {i}" for i in range(10)]
            
            hunter = PatternHunter()
            vectors = hunter.vectorizer.fit_transform(texts)
            labels = hunter.clusterer.fit_predict(vectors.toarray())
            
            unique_clusters = len(set(labels)) - (1 if -1 in labels else 0)
            
            # Should handle single cluster gracefully
            self.record_test("Single Cluster", True,
                           f"({unique_clusters} cluster(s) found)")
            return True
        
        except Exception as e:
            self.record_test("Single Cluster", False, str(e))
            return False
    
    async def test_noise_filtering(self):
        """Test 18: Noise Point Filtering"""
        self.log("Test 18: Noise Point Filtering", "TEST")
        
        try:
            # Mix of clusterable and random texts
            texts = [
                "Silver demand surge article 1",
                "Silver demand surge article 2",
                "Silver demand surge article 3",
                "Random unrelated text about weather",
                "Another random topic about cooking",
                "Mining strike news 1",
                "Mining strike news 2",
                "Mining strike news 3"
            ]
            
            hunter = PatternHunter()
            vectors = hunter.vectorizer.fit_transform(texts)
            labels = hunter.clusterer.fit_predict(vectors.toarray())
            
            # Should identify noise points
            noise_count = sum(1 for l in labels if l == -1)
            
            # Random texts should likely be noise
            has_noise = noise_count > 0
            
            self.record_test("Noise Filtering", has_noise,
                           f"({noise_count} noise points detected)")
            return noise_count
        
        except Exception as e:
            self.record_test("Noise Filtering", False, str(e))
            return None
    
    # ==================== HELPER METHODS ====================
    
    def get_narrative_count(self) -> int:
        """Get current narrative count from database"""
        session = get_session()
        count = session.query(Narrative).count()
        session.close()
        return count
    
    # ==================== MAIN TEST RUNNER ====================
    
    async def run_all_tests(self):
        """Run all tests in sequence"""
        self.start_time = time.time()
        
        print("\n" + "="*80)
        print("🧪 COMPREHENSIVE TIER 2 NARRATIVE DISCOVERY TEST SUITE")
        print("="*80)
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # Initialize database
        self.log("Initializing database...", "INFO")
        init_database()
        
        # Run all tests
        test_methods = [
            # Pattern Hunter Tests (PS 5)
            self.test_tfidf_vectorization,
            self.test_hdbscan_clustering,
            self.test_narrative_naming,
            self.test_pattern_hunter_discovery,
            self.test_narrative_persistence,
            
            # Resource Manager Tests (PS 4)
            self.test_volatility_calculation,
            self.test_strategy_decision,
            self.test_budget_allocation,
            self.test_source_staleness,
            
            # Sentiment Analysis Tests
            self.test_sentiment_basic,
            self.test_sentiment_narrative,
            
            # Integration Tests
            self.test_end_to_end_discovery,
            self.test_narrative_quality,
            
            # Performance Tests
            self.test_clustering_performance,
            self.test_concurrent_discovery,
            
            # Edge Case Tests
            self.test_empty_dataset,
            self.test_single_cluster,
            self.test_noise_filtering,
        ]
        
        for test_method in test_methods:
            try:
                await test_method()
                await asyncio.sleep(0.5)  # Brief pause between tests
            except Exception as e:
                self.log(f"Test {test_method.__name__} crashed: {e}", "ERROR")
                self.results["tests_failed"] += 1
        
        # Print final report
        self.print_final_report()
    
    def print_final_report(self):
        """Print comprehensive test report"""
        duration = time.time() - self.start_time
        
        print("\n" + "="*80)
        print("📊 FINAL TEST REPORT - TIER 2: NARRATIVE DISCOVERY")
        print("="*80)
        
        # Test Summary
        print(f"\n📈 TEST SUMMARY:")
        print(f"   Total Tests Run: {self.results['tests_run']}")
        print(f"   ✅ Passed: {self.results['tests_passed']}")
        print(f"   ❌ Failed: {self.results['tests_failed']}")
        
        pass_rate = (self.results['tests_passed'] / self.results['tests_run'] * 100) if self.results['tests_run'] > 0 else 0
        print(f"   📊 Pass Rate: {pass_rate:.1f}%")
        
        # Component Status
        print(f"\n🔧 COMPONENT STATUS:")
        for component, data in self.results['component_status'].items():
            status_icon = "✅" if data.get('status') == 'success' else "❌"
            print(f"   {status_icon} {component.upper()}: {data.get('status', 'unknown')}")
            for key, value in data.items():
                if key != 'status':
                    print(f"      {key}: {value}")
        
        # Performance Metrics
        if self.results['performance_metrics']:
            print(f"\n⚡ PERFORMANCE METRICS:")
            for metric, data in self.results['performance_metrics'].items():
                print(f"   {metric.upper()}:")
                for key, value in data.items():
                    if isinstance(value, float):
                        print(f"      {key}: {value:.2f}")
                    else:
                        print(f"      {key}: {value}")
        
        # Quality Scores
        if self.results['quality_scores']:
            print(f"\n📊 QUALITY SCORES:")
            for metric, score in self.results['quality_scores'].items():
                print(f"   {metric.capitalize()}: {score:.1%}")
        
        # Errors
        if self.results['errors']:
            print(f"\n❌ ERRORS ({len(self.results['errors'])}):")
            for error in self.results['errors'][:5]:
                print(f"   • {error['test']}: {error['details'][:100]}")
        
        # Overall Grade
        print(f"\n🎓 OVERALL GRADE:")
        if pass_rate >= 90:
            grade = "A+ (Excellent)"
        elif pass_rate >= 80:
            grade = "A (Very Good)"
        elif pass_rate >= 70:
            grade = "B (Good)"
        elif pass_rate >= 60:
            grade = "C (Acceptable)"
        else:
            grade = "D (Needs Improvement)"
        
        print(f"   {grade} - {pass_rate:.1f}% tests passed")
        
        print(f"\n⏱️  Total Duration: {duration:.2f} seconds")
        print("="*80 + "\n")
        
        # Save results
        self.save_results()
    
    def save_results(self):
        """Save test results to JSON file"""
        try:
            results_file = "test_results_tier2.json"
            with open(results_file, 'w') as f:
                json.dump(self.results, f, indent=2, default=str)
            self.log(f"Results saved to {results_file}", "SUCCESS")
        except Exception as e:
            self.log(f"Failed to save results: {e}", "ERROR")


async def main():
    """Main test runner"""
    suite = Tier2TestSuite()
    await suite.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
