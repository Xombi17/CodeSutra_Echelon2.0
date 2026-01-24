"""
Data Collection Module
Fetches news, social media, and price data for narrative analysis
"""
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import requests
import praw
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


class RedditCollector:
    """Collect discussions from Reddit"""
    
    def __init__(self):
        self.client_id = config.data.reddit_client_id
        self.client_secret = config.data.reddit_client_secret
        self.user_agent = config.data.reddit_user_agent
        
        if self.client_id and self.client_secret:
            self.reddit = praw.Reddit(
                client_id=self.client_id,
                client_secret=self.client_secret,
                user_agent=self.user_agent
            )
        else:
            self.reddit = None
    
    async def fetch_posts(
        self,
        subreddits: List[str] = ["wallstreetbets", "investing", "commodities"],
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Fetch Reddit posts about silver
        
        Args:
            subreddits: List of subreddits to search
            limit: Maximum posts per subreddit
        """
        if not self.reddit:
            print("⚠️ Reddit API not configured, using mock data")
            return self._mock_posts()
        
        posts = []
        keywords = ["silver", "SLV", "AG", "silver market"]
        
        try:
            for subreddit_name in subreddits:
                subreddit = self.reddit.subreddit(subreddit_name)
                
                # Search recent posts
                for post in subreddit.search(" OR ".join(keywords), time_filter="week", limit=limit):
                    if any(kw.lower() in post.title.lower() or kw.lower() in post.selftext.lower() 
                           for kw in keywords):
                        posts.append({
                            "title": post.title,
                            "content": post.selftext[:500],  #Truncate
                            "url": f"https://reddit.com{post.permalink}",
                            "source": f"reddit:{subreddit_name}",
                            "published_at": datetime.fromtimestamp(post.created_utc),
                            "author": str(post.author) if post.author else "deleted",
                            "metadata": {
                                "score": post.score,
                                "num_comments": post.num_comments
                            }
                        })
            
            return posts
        
        except Exception as e:
            print(f"❌ Reddit error: {e}")
            return []
    
    def _mock_posts(self) -> List[Dict[str, Any]]:
        """Generate mock Reddit posts"""
        return [
            {
                "title": "Silver to the moon? 🚀",
                "content": "Industrial demand at all-time high, wedding season coming...",
                "url": "https://reddit.com/r/wallstreetbets/mock1",
                "source": "reddit:wallstreetbets",
                "published_at": datetime.now() - timedelta(hours=1),
                "author": "SilverBull2024",
                "metadata": {"score": 245, "num_comments": 89}
            }
        ]


class PriceCollector:
    """Collect silver price data"""
    
    def __init__(self):
        self.symbol = config.data.yfinance_symbol
    
    async def fetch_price_history(
        self,
        period: str = "1mo",
        interval: str = "1h"
    ) -> List[Dict[str, Any]]:
        """
        Fetch historical price data
        
        Args:
            period: Time period (1d, 5d, 1mo, 3mo, 1y)
            interval: Data interval (1m, 5m, 15m, 1h, 1d)
        """
        try:
            ticker = yf.Ticker(self.symbol)
            data = ticker.history(period=period, interval=interval)
            
            prices = []
            for index, row in data.iterrows():
                prices.append({
                    "timestamp": index.to_pydatetime(),
                    "open_price": float(row['Open']),
                    "high_price": float(row['High']),
                    "low_price": float(row['Low']),
                    "close_price": float(row['Close']),
                    "volume": float(row['Volume']),
                    "price": float(row['Close']),  # Use close as main price
                    "source": "yfinance"
                })
            
            return prices
        
        except Exception as e:
            print(f"❌ YFinance error: {e}")
            return []
    
    async def get_current_price(self) -> Optional[float]:
        """Get current silver price"""
        try:
            ticker = yf.Ticker(self.symbol)
            data = ticker.history(period="1d", interval="1m")
            if not data.empty:
                return float(data['Close'].iloc[-1])
            return None
        except Exception as e:
            print(f"❌ Current price error: {e}")
            return None


class DataCollectionOrchestrator:
    """Orchestrates all data collection"""
    
    def __init__(self):
        self.news_collector = NewsCollector()
        self.reddit_collector = RedditCollector()
        self.price_collector = PriceCollector()
    
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
        print("🔄 Collecting data from all sources...")
        
        # Run collections in parallel
        results = await asyncio.gather(
            self.news_collector.fetch_articles(days_back=news_days_back),
            self.reddit_collector.fetch_posts(),
            self.price_collector.fetch_price_history(period=price_period),
            return_exceptions=True
        )
        
        articles = results[0] if not isinstance(results[0], Exception) else []
        posts = results[1] if not isinstance(results[1], Exception) else []
        prices = results[2] if not isinstance(results[2], Exception) else []
        
        print(f"✅ Collected: {len(articles)} articles, {len(posts)} posts, {len(prices)} price points")
        
        return {
            "articles": articles,
            "posts": posts,
            "prices": prices,
            "collected_at": datetime.now()
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
                        metadata=article_data.get("metadata")
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
        
        except Exception as e:
            session.rollback()
            print(f"❌ Database save error: {e}")
        finally:
            session.close()


# Global collector instance
collector = DataCollectionOrchestrator()


if __name__ == "__main__":
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
