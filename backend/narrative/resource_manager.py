"""
Resource Manager (PS 4 Implementation)
Autonomous data collection orchestration based on market conditions
"""
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List
import numpy as np
from database import get_session, PriceData
from data_collection import collector
from config import config


class ResourceManager:
    """
    Autonomously decides which data sources to prioritize based on market volatility
    Implements PS 4: Autonomous Resource Management
    """
    
    def __init__(self):
        self.current_strategy = None
        self.last_refresh = {}  # Track last refresh time per source
        self.source_quality_scores = {
            "newsapi": 0.9,  # High signal-to-noise
            "reddit": 0.6,   # Medium (noisy but fast)
            "twitter": 0.7   # Not yet implemented
        }
    
    def calculate_volatility(self, window_hours: int = 24) -> float:
        """
        Calculate recent price volatility
        
        Args:
            window_hours: Time window to analyze
            
        Returns:
            Volatility as percentage
        """
        session = get_session()
        
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=window_hours)
            prices = session.query(PriceData).filter(
                PriceData.timestamp >= cutoff_time
            ).order_by(PriceData.timestamp).all()
            
            if len(prices) < 10:
                return 1.0  # Medium volatility default
            
            price_values = [p.price for p in prices]
            volatility = np.std(price_values) / np.mean(price_values) * 100
            
            return volatility
        
        except Exception as e:
            print(f"❌ Volatility calculation error: {e}")
            return 1.0
        
        finally:
            session.close()
    
    def decide_scraping_strategy(self, volatility: float = None) -> Dict[str, Any]:
        """
        Decide scraping intervals based on market volatility
        
        Args:
            volatility: Current volatility (will calculate if None)
            
        Returns:
            Strategy dict with intervals and source priorities
        """
        if volatility is None:
            volatility = self.calculate_volatility()
        
        print(f"📊 Current volatility: {volatility:.2f}%")
        
        if volatility > 5.0:
            # HIGH VOLATILITY: Aggressive scraping
            strategy = {
                "mode": "aggressive",
                "news_interval_minutes": config.data.high_volatility_interval,
                "reddit_interval_minutes": 5,
                "price_interval_minutes": 1,
                "sources": ["all"],
                "priority": ["newsapi", "reddit", "twitter"],
                "reason": f"High volatility detected ({volatility:.2f}%)"
            }
        
        elif volatility > 2.0:
            # MEDIUM VOLATILITY: Balanced scraping
            strategy = {
                "mode": "balanced",
                "news_interval_minutes": config.data.medium_volatility_interval,
                "reddit_interval_minutes": 15,
                "price_interval_minutes": 5,
                "sources": ["premium"],  # NewsAPI, major sources only
                "priority": ["newsapi"],
                "reason": f"Medium volatility ({volatility:.2f}%)"
            }
        
        else:
            # LOW VOLATILITY: Conservative scraping
            strategy = {
                "mode": "conservative",
                "news_interval_minutes": config.data.low_volatility_interval,
                "reddit_interval_minutes": 60,
                "price_interval_minutes": 15,
                "sources": ["cached"],  # Use cached data when possible
                "priority": ["newsapi"],
                "reason": f"Low volatility ({volatility:.2f}%) - conserving API calls"
            }
        
        self.current_strategy = strategy
        return strategy
    
    def is_source_stale(self, source: str, strategy: Dict[str, Any]) -> bool:
        """
        Check if a data source needs refresh
        
        Args:
            source: Source name (news, reddit, price)
            strategy: Current scraping strategy
            
        Returns:
            True if source should be refreshed
        """
        if source not in self.last_refresh:
            return True  # Never refreshed
        
        last_refresh_time = self.last_refresh[source]
        time_since_refresh = (datetime.now() - last_refresh_time).total_seconds() / 60
        
        # Get interval for this source
        interval_key = f"{source}_interval_minutes"
        required_interval = strategy.get(interval_key, 30)
        
        return time_since_refresh >= required_interval
    
    async def refresh_data_sources(self, force: bool = False):
        """
        Refresh data sources based on current strategy
        
        Args:
            force: Force refresh regardless of staleness
        """
        strategy = self.decide_scraping_strategy()
        
        tasks = []
        
        # Check which sources need refresh
        if force or self.is_source_stale("news", strategy):
            print(f"🔄 Refreshing news (interval: {strategy['news_interval_minutes']}min)")
            tasks.append(("news", collector.news_collector.fetch_articles()))
            self.last_refresh["news"] = datetime.now()
        
        # Reddit collector removed
        # if force or self.is_source_stale("reddit", strategy):
        #     pass
        
        if force or self.is_source_stale("price", strategy):
            print(f"🔄 Refreshing prices (interval: {strategy['price_interval_minutes']}min)")
            tasks.append(("price", collector.price_collector.fetch_price_history(period="1d")))
            self.last_refresh["price"] = datetime.now()
        
        if not tasks:
            print("✅ All sources are fresh")
            return {"refreshed": []}
        
        # Execute refreshes in parallel
        results = await asyncio.gather(*[task for _, task in tasks], return_exceptions=True)
        
        refreshed_sources = [source for source, _ in tasks]
        
        # Save to database
        data = {
            "articles": [],
            "posts": [],
            "prices": []
        }
        
        for i, (source, _) in enumerate(tasks):
            if not isinstance(results[i], Exception):
                if source == "news":
                    data["articles"] = results[i]
                elif source == "reddit":
                    data["posts"] = results[i]
                elif source == "price":
                    data["prices"] = results[i]
        
        await collector.save_to_database(data)
        
        return {
            "refreshed": refreshed_sources,
            "strategy": strategy,
            "articles_fetched": len(data["articles"]),
            "posts_fetched": len(data["posts"]),
            "prices_fetched": len(data["prices"])
        }
    
    def get_source_budget_allocation(self) -> Dict[str, float]:
        """
        Allocate API call budget based on source quality
        
        Returns:
            Dict mapping source to budget percentage
        """
        total_quality = sum(self.source_quality_scores.values())
        
        allocation = {}
        for source, quality in self.source_quality_scores.items():
            allocation[source] = (quality / total_quality) * 100
        
        return allocation
    
    async def monitor_and_refresh(self, interval_seconds: int = 300):
        """
        Continuous monitoring loop
        Checks volatility and refreshes sources as needed
        
        Args:
            interval_seconds: How often to check (default 5 minutes)
        """
        print(f"🤖 Resource Manager started (check interval: {interval_seconds}s)")
        
        while True:
            try:
                await self.refresh_data_sources()
                await asyncio.sleep(interval_seconds)
            
            except Exception as e:
                print(f"❌ Monitor error: {e}")
                await asyncio.sleep(interval_seconds)
    
    def get_status(self) -> Dict[str, Any]:
        """Get current resource manager status"""
        return {
            "current_strategy": self.current_strategy,
            "last_refresh": {k: v.isoformat() for k, v in self.last_refresh.items()},
            "budget_allocation": self.get_source_budget_allocation(),
            "volatility": self.calculate_volatility()
        }


# Global resource manager instance
resource_manager = ResourceManager()


if __name__ == "__main__":
    # Test resource manager
    async def test():
        print("🧪 Testing Resource Manager (PS 4)...\n")
        
        # Test volatility calculation
        volatility = resource_manager.calculate_volatility()
        print(f"Current volatility: {volatility:.2f}%\n")
        
        # Test strategy decision
        strategy = resource_manager.decide_scraping_strategy(volatility)
        print(f"Selected strategy: {strategy['mode']}")
        print(f"Reason: {strategy['reason']}")
        print(f"News interval: {strategy['news_interval_minutes']} minutes")
        print(f"Reddit interval: {strategy['reddit_interval_minutes']} minutes\n")
        
        # Test budget allocation
        budget = resource_manager.get_source_budget_allocation()
        print("Budget allocation:")
        for source, pct in budget.items():
            print(f"  {source}: {pct:.1f}%")
        
        # Test data refresh
        print("\n🔄 Testing data refresh...")
        result = await resource_manager.refresh_data_sources(force=True)
        print(f"Refreshed sources: {result['refreshed']}")
        print(f"Articles: {result['articles_fetched']}")
        print(f"Posts: {result['posts_fetched']}")
        print(f"Prices: {result['prices_fetched']}")
    
    asyncio.run(test())
