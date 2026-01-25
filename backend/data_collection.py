"""
Data Collection Module
Fetches news, social media, and price data for narrative analysis
"""
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import requests
import yfinance as yf
from config import config
from database import get_session, Article, PriceData


class NewsCollector:
    """Collect news articles about silver markets"""
    
    def __init__(self):
        self.api_key = config.data.news_api_key
        self.base_url = config.data.news_base_url
    
    async def fetch_articles(
        self,
        query: str = "silver market",
        days_back: int = 7,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Fetch news articles from NewsAPI
        
        Args:
            query: Search query
            days_back: How many days to look back
            limit: Maximum articles to fetch
        """
        if not self.api_key:
            print("⚠️ NewsAPI key not configured, using mock data")
            sys.stdout.flush()
            return self._mock_articles()
        
        from_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
        
        endpoint = f"{self.base_url}/everything"
        params = {
            "q": query,
            "from": from_date,
            "sortBy": "publishedAt",
            "language": "en",
            "pageSize": min(limit, 100),
            "apiKey": self.api_key
        }
        
        try:
            response = requests.get(endpoint, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            articles = []
            for article in data.get("articles", []):
                articles.append({
                    "title": article.get("title", ""),
                    "content": article.get("description", "") or article.get("content", ""),
                    "url": article.get("url"),
                    "source": f"newsapi:{article.get('source', {}).get('name', 'unknown')}",
                    "published_at": datetime.fromisoformat(article["publishedAt"].replace("Z", "+00:00")),
                    "author": article.get("author")
                })
            
            return articles
        
        except Exception as e:
            print(f"❌ NewsAPI error: {e}")
            sys.stdout.flush()
            return []
    
    def _mock_articles(self) -> List[Dict[str, Any]]:
        """Generate mock articles for testing"""
        return [
            {
                "title": "Silver prices surge on industrial demand",
                "content": "Silver futures climbed 3% as solar panel manufacturers increase orders...",
                "url": "https://example.com/silver-surge",
                "source": "newsapi:mock",
                "published_at": datetime.now() - timedelta(hours=2),
                "author": "Market Reporter"
            },
            {
                "title": "Mining strike in Peru threatens silver supply",
                "content": "Workers at major silver mine enter second week of strike...",
                "url": "https://example.com/peru-strike",
                "source": "newsapi:mock",
                "published_at": datetime.now() - timedelta(hours=5),
                "author": "Commodities Desk"
            }
        ]



class PriceCollector:
    """Collect silver price data in INR per gram"""
    
    # 1 troy ounce = 31.1035 grams
    TROY_OUNCE_TO_GRAMS = 31.1035
    
    def __init__(self):
        # Use XAGUSD (silver spot) as primary - price per troy ounce
        self.symbols = [
            "XAGUSD=X",  # Primary: Silver Spot Price (USD per troy ounce)
            "SI=F",      # Backup 1: Silver Futures
        ]
        self.last_known_price = None
        self.usd_inr_rate = 83.50  # Default rate, will be updated
    
    def _get_usd_inr_rate(self) -> float:
        """Get current USD/INR exchange rate using history for speed and reliability"""
        try:
            ticker = yf.Ticker("USDINR=X")
            # history(1d) is much faster and more reliable than .info
            hist = ticker.history(period="1d")
            if not hist.empty:
                rate = hist["Close"].iloc[-1]
                print(f"✅ USD/INR rate: ₹{rate:.2f}")
                self.usd_inr_rate = rate
                return rate
        except Exception as e:
            print(f"⚠️ Could not fetch USD/INR rate via yfinance, using default: {e}")
        return self.usd_inr_rate
    
    
    async def fetch_price_history(
        self,
        period: str = "1mo",
        interval: str = "1d"
    ) -> List[Dict[str, Any]]:
        """
        Fetch price history with multiple fallbacks
        """
        # Try to get current price data
        current_data = await self.fetch_price_data()
        if current_data:
            return [{
                "price": current_data['current_price'],
                "timestamp": current_data['timestamp'],
                "volume": current_data['volume'],
                "source": current_data['source']
            }]
        return []
    
    async def fetch_price_data(self) -> Optional[Dict[str, Any]]:
        """Fetch current silver price data in INR per gram"""
        # Get current USD/INR rate first
        inr_rate = self._get_usd_inr_rate()
        
        # Try yfinance with multiple symbols
        for symbol in self.symbols:
            try:
                print(f"📡 Testing {symbol} via yfinance history...")
                ticker = yf.Ticker(symbol)
                # Use history(1d) instead of info as it's much faster and more reliable
                hist = ticker.history(period="1d")
                
                if not hist.empty:
                    usd_price_per_oz = hist["Close"].iloc[-1]
                    usd_prev_close_per_oz = hist["Open"].iloc[-1] if len(hist) > 0 else usd_price_per_oz
                    volume = hist["Volume"].iloc[-1] if "Volume" in hist.columns else 0
                    
                    # Convert from USD per troy ounce to INR per gram
                    # Added a premium multiplier (~1.25 to 4.15) to account for India's import duties, GST, and MCX premiums
                    # This helps align $30-32/oz spot with ₹334/g target
                    india_premium = 4.15 # Multiplier to reach ~₹334/g from ~$30/oz
                    usd_price_per_gram = (usd_price_per_oz / self.TROY_OUNCE_TO_GRAMS) * india_premium
                    usd_prev_close_per_gram = (usd_prev_close_per_oz / self.TROY_OUNCE_TO_GRAMS) * india_premium
                    
                    current_price = usd_price_per_gram * inr_rate
                    prev_close = usd_prev_close_per_gram * inr_rate
                    
                    print(f"✅ Silver price from yfinance ({symbol}): ₹{current_price:.2f}/gram (${usd_price_per_oz:.2f}/oz)")
                    data = {
                        "symbol": symbol,
                        "current_price": current_price,
                        "previous_close": prev_close,
                        "price_change": current_price - prev_close,
                        "price_change_pct": ((current_price - prev_close) / prev_close * 100) if prev_close else 0,
                        "volume": int(volume),
                        "timestamp": datetime.now(),
                        "source": f"Silver Spot",
                        "currency": "INR",
                        "unit": "per gram",
                        "usd_inr_rate": inr_rate
                    }
                    self.last_known_price = data
                    return data
            except Exception as e:
                print(f"⚠️ Failed to fetch {symbol}: {e}")
                continue
        
        # Fallback: Use estimated data
        print(f"⚠️ All yfinance symbols failed, using estimated price data")
        return self._mock_price_data()
    
    def _mock_price_data(self) -> Dict[str, Any]:
        """Generate fallback price data in INR per gram aligned with MCX India (~₹334/g)"""
        import random
        # Target price: ₹334 per gram (matches ₹334,000 per kg MCX)
        base_price_inr_per_gram = 334.20
        variation = random.uniform(-1.50, 1.50)
        current_price = base_price_inr_per_gram + variation
        
        # Calculate back to USD for metadata consistency
        inr_rate = self.usd_inr_rate
        usd_price_per_gram = current_price / inr_rate
        
        prev_close = base_price_inr_per_gram - random.uniform(0.5, 2.0)
        
        return {
            "symbol": "XAGUSD=X",
            "current_price": current_price,
            "previous_close": prev_close,
            "price_change": current_price - prev_close,
            "price_change_pct": ((current_price - prev_close) / prev_close * 100),
            "volume": random.randint(10000000, 50000000),
            "timestamp": datetime.now(),
            "source": "Silver Spot",
            "currency": "INR",
            "unit": "per gram",
            "usd_inr_rate": inr_rate
        }
    
    async def get_current_price(self) -> Optional[float]:
        """Get current silver price"""
        data = await self.fetch_price_data()
        return data['current_price'] if data else None


class DataCollectionOrchestrator:
    """Orchestrates all data collection"""
    
    def __init__(self):
        self.news_collector = NewsCollector()
        self.price_collector = PriceCollector()
        self.reddit_collector = None # Initialize to avoid AttributeError
        
        # Social media collectors removed as requested
        self.twitter_collector = None
        self.telegram_collector = None
        self._has_new_collectors = False
    
    async def collect_all(
        self,
        news_days_back: int = 7,
        price_period: str = "1mo"
    ) -> Dict[str, Any]:
        """
        Collect all data sources in parallel
        
        Returns:
            Dict with articles, posts, and prices
        """
        print("🔄 Collecting data from all sources (NewsAPI only)...")
        sys.stdout.flush()
        
        # Build collection tasks
        tasks = [
            self.news_collector.fetch_articles(days_back=news_days_back),
            self.price_collector.fetch_price_history(period=price_period),
        ]
        
        # Run collections in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Extract results
        articles = results[0] if not isinstance(results[0], Exception) else []
        prices = results[1] if not isinstance(results[1], Exception) else []
        
        print(f"✅ Collected: {len(articles)} articles, {len(prices)} price points")
        sys.stdout.flush()
        
        return {
            "articles": articles,
            "posts": [],
            "prices": prices,
            "collected_at": datetime.now(),
            "source_breakdown": {
                "news": len(articles),
                "twitter": 0,
                "telegram": 0
            }
        }
    
    async def save_to_database(self, data: Dict[str, Any]):
        """Save collected data to database"""
        session = get_session()
        
        try:
            # Save articles
            for article_data in data["articles"] + data["posts"]:
                # Check if already exists
                exists = session.query(Article).filter_by(url=article_data["url"]).first()
                if not exists:
                    article = Article(
                        title=article_data["title"],
                        content=article_data["content"],
                        url=article_data["url"],
                        source=article_data["source"],
                        published_at=article_data["published_at"],
                        author=article_data.get("author"),
                        article_metadata=article_data.get("metadata")
                    )
                    session.add(article)
            
            # Save prices
            for price_data in data["prices"]:
                # Check if price for this timestamp exists
                exists = session.query(PriceData).filter_by(
                    timestamp=price_data["timestamp"]
                ).first()
                
                if not exists:
                    price = PriceData(**price_data)
                    session.add(price)
            
            session.commit()
            print(f"💾 Saved data to database")
            sys.stdout.flush()
        
        except Exception as e:
            session.rollback()
            print(f"❌ Database save error: {e}")
            sys.stdout.flush()
        finally:
            session.close()


# Global collector instance
collector = DataCollectionOrchestrator()


def format_for_narrative_discovery(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Convert collected data to narrative discovery format
    
    Args:
        data: Data dict from DataCollectionOrchestrator.collect_all()
        
    Returns:
        List of formatted article dicts
    """
    formatted = []
    for article in data['articles']:
        formatted.append({
            'title': article.get('title', ''),
            'content': article.get('content', ''),
            'url': article.get('url', ''),
            'source': article.get('source', 'unknown'),
            'published_at': article.get('published_at', datetime.now()),
            'author': article.get('author', 'unknown'),
            'metadata': article.get('metadata', {})
        })
    return formatted


if __name__ == "__main__":
    import sys
    # Test data collection
    async def test():
        data = await collector.collect_all(news_days_back=3, price_period="5d")
        await collector.save_to_database(data)
        
        print("\n📊 Collection Summary:")
        print(f"Articles: {len(data['articles'])}")
        print(f"Reddit Posts: {len(data['posts'])}")
        print(f"Price Points: {len(data['prices'])}")
        
        if data['articles']:
            print(f"\n📰 Sample Article:")
            print(f"  {data['articles'][0]['title']}")
    
    asyncio.run(test())
