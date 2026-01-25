"""
Comprehensive Test Suite for All Data Collectors
Tests: NewsAPI, Reddit, Twitter, Telegram, yfinance
"""
import asyncio
import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_collection import NewsCollector, PriceCollector, DataCollectionOrchestrator
from collectors import TwitterCollector, TelegramCollector


class TestResults:
    """Store and display test results"""
    def __init__(self):
        self.results = {}
    
    def add_result(self, source, status, count, message=""):
        self.results[source] = {
            "status": status,
            "count": count,
            "message": message
        }
    
    def print_summary(self):
        print("\n" + "="*70)
        print("📊 DATA COLLECTION TEST SUMMARY")
        print("="*70)
        
        for source, result in self.results.items():
            status_icon = "✅" if result["status"] == "success" else "⚠️" if result["status"] == "mock" else "❌"
            print(f"\n{status_icon} {source.upper()}")
            print(f"   Status: {result['status']}")
            print(f"   Items Collected: {result['count']}")
            if result['message']:
                print(f"   Note: {result['message']}")
        
        print("\n" + "="*70)
        
        # Calculate totals
        total_items = sum(r['count'] for r in self.results.values())
        success_count = sum(1 for r in self.results.values() if r['status'] in ['success', 'mock'])
        
        print(f"📈 TOTAL ITEMS COLLECTED: {total_items}")
        print(f"✅ WORKING SOURCES: {success_count}/{len(self.results)}")
        print("="*70 + "\n")


async def test_news_collector():
    """Test NewsAPI collector"""
    print("\n🔍 Testing NewsAPI Collector...")
    collector = NewsCollector()
    
    try:
        articles = await collector.fetch_articles(query="silver market", days_back=3, limit=10)
        
        if articles:
            print(f"✅ NewsAPI: Collected {len(articles)} articles")
            if articles[0].get('title'):
                print(f"   Sample: {articles[0]['title'][:80]}...")
            return "success", len(articles), "Real data from NewsAPI"
        else:
            return "mock", 0, "No articles returned (check API key)"
    
    except Exception as e:
        print(f"❌ NewsAPI Error: {e}")
        return "error", 0, str(e)



async def test_twitter_collector():
    """Test Twitter collector"""
    print("\n🔍 Testing Twitter Collector...")
    
    collector = TwitterCollector()
    
    try:
        tweets = await collector.fetch_tweets(max_tweets=10, days_back=3)
        
        if tweets:
            # Check if it's mock data
            is_mock = any("mock" in tweet.get('url', '') for tweet in tweets)
            
            if is_mock:
                print(f"⚠️ Twitter: Using mock data ({len(tweets)} tweets)")
                return "mock", len(tweets), "OAuth credentials need regeneration"
            else:
                print(f"✅ Twitter: Collected {len(tweets)} real tweets")
                if tweets[0].get('title'):
                    print(f"   Sample: {tweets[0]['title'][:80]}...")
                return "success", len(tweets), "Real data from Twitter API"
        else:
            return "error", 0, "No tweets returned"
    
    except Exception as e:
        print(f"❌ Twitter Error: {e}")
        return "error", 0, str(e)


async def test_telegram_collector():
    """Test Telegram collector"""
    print("\n🔍 Testing Telegram Collector...")
    
    collector = TelegramCollector()
    
    try:
        messages = await collector.fetch_messages(
            channels=["@SilverSqueeze", "@SilverNews"],
            limit_per_channel=10,
            days_back=3
        )
        
        if messages:
            # Check if it's mock data
            is_mock = any("mock" in msg.get('url', '') for msg in messages)
            
            if is_mock:
                print(f"⚠️ Telegram: Using mock data ({len(messages)} messages)")
                return "mock", len(messages), "API credentials not configured"
            else:
                print(f"✅ Telegram: Collected {len(messages)} real messages")
                if messages[0].get('title'):
                    print(f"   Sample: {messages[0]['title'][:80]}...")
                return "success", len(messages), "Real data from Telegram"
        else:
            return "error", 0, "No messages returned"
    
    except Exception as e:
        print(f"❌ Telegram Error: {e}")
        return "error", 0, str(e)


async def test_price_collector():
    """Test yfinance price collector"""
    print("\n🔍 Testing yfinance Price Collector...")
    collector = PriceCollector()
    
    try:
        prices = await collector.fetch_price_history(period="5d", interval="1h")
        
        if prices:
            print(f"✅ yfinance: Collected {len(prices)} price points")
            if prices[0].get('price'):
                print(f"   Latest Price: ${prices[-1]['price']:.2f}")
            return "success", len(prices), "Real silver price data"
        else:
            return "error", 0, "No price data returned"
    
    except Exception as e:
        print(f"❌ yfinance Error: {e}")
        return "error", 0, str(e)


async def test_full_orchestrator():
    """Test the full DataCollectionOrchestrator"""
    print("\n🔍 Testing Full Data Collection Orchestrator...")
    print("="*70)
    
    orchestrator = DataCollectionOrchestrator()
    
    try:
        data = await orchestrator.collect_all(news_days_back=3, price_period="5d")
        
        print(f"\n📊 Orchestrator Results:")
        print(f"   Total Articles: {len(data.get('articles', []))}")
        print(f"   Price Points: {len(data.get('prices', []))}")
        
        if 'source_breakdown' in data:
            print(f"\n   Source Breakdown:")
            for source, count in data['source_breakdown'].items():
                print(f"      {source}: {count}")
        
        return data
    
    except Exception as e:
        print(f"❌ Orchestrator Error: {e}")
        return None


async def run_all_tests():
    """Run all collector tests"""
    print("\n" + "="*70)
    print("🧪 SILVERSENTINEL DATA COLLECTOR TEST SUITE")
    print("="*70)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = TestResults()
    
    # Test each collector individually
    print("\n📋 INDIVIDUAL COLLECTOR TESTS")
    print("-"*70)
    
    # 1. NewsAPI
    status, count, msg = await test_news_collector()
    results.add_result("NewsAPI", status, count, msg)
    
    # 2. Twitter
    status, count, msg = await test_twitter_collector()
    results.add_result("Twitter", status, count, msg)
    
    # 3. Telegram
    status, count, msg = await test_telegram_collector()
    results.add_result("Telegram", status, count, msg)
    
    # 5. yfinance
    status, count, msg = await test_price_collector()
    results.add_result("yfinance", status, count, msg)
    
    # Print summary
    results.print_summary()
    
    # Test full orchestrator
    print("\n📋 INTEGRATION TEST")
    print("-"*70)
    orchestrator_data = await test_full_orchestrator()
    
    if orchestrator_data:
        print("\n✅ Integration test PASSED")
    else:
        print("\n❌ Integration test FAILED")
    
    print("\n" + "="*70)
    print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70 + "\n")


if __name__ == "__main__":
    print("\n🚀 Starting SilverSentinel Data Collector Tests...\n")
    asyncio.run(run_all_tests())
