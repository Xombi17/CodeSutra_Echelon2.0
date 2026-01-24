"""
Twitter Data Collector
Fetches tweets about silver markets from hashtags and influential accounts
"""
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import tweepy
from config import config


class TwitterCollector:
    """Collect tweets about silver markets"""
    
    def __init__(self):
        self.api_key = config.data.twitter_api_key
        self.api_secret = config.data.twitter_api_secret
        self.access_token = config.data.twitter_access_token
        self.access_secret = config.data.twitter_access_secret
        
        if self.api_key and self.api_secret and self.access_token and self.access_secret:
            try:
                auth = tweepy.OAuthHandler(self.api_key, self.api_secret)
                auth.set_access_token(self.access_token, self.access_secret)
                self.api = tweepy.API(auth, wait_on_rate_limit=True)
                self.client = tweepy.Client(
                    consumer_key=self.api_key,
                    consumer_secret=self.api_secret,
                    access_token=self.access_token,
                    access_token_secret=self.access_secret,
                    wait_on_rate_limit=True
                )
            except Exception as e:
                print(f"⚠️ Twitter API initialization error: {e}")
                self.api = None
                self.client = None
        else:
            print("⚠️ Twitter API keys not configured, using mock data")
            self.api = None
            self.client = None
    
    async def fetch_tweets(
        self,
        max_tweets: int = 100,
        days_back: int = 7
    ) -> List[Dict[str, Any]]:
        """
        Fetch tweets about silver
        
        Args:
            max_tweets: Maximum tweets to fetch
            days_back: How many days to look back
        """
        if not self.client:
            print("⚠️ Twitter API not configured, using mock data")
            return self._mock_tweets()
        
        try:
            # Search query combining hashtags and keywords
            query = "#silver OR #silversqueeze OR #silverprice OR #XAGUSD OR \"silver market\" -is:retweet lang:en"
            
            # Calculate start time
            start_time = datetime.utcnow() - timedelta(days=days_back)
            
            tweets_data = []
            
            # Search tweets using Twitter API v2
            tweets = self.client.search_recent_tweets(
                query=query,
                max_results=min(max_tweets, 100),  # API limit is 100 per request
                start_time=start_time,
                tweet_fields=['created_at', 'public_metrics', 'author_id'],
                user_fields=['username', 'public_metrics']
            )
            
            if tweets.data:
                for tweet in tweets.data:
                    # Get user info
                    user = self._get_user_info(tweets.includes, tweet.author_id) if hasattr(tweets, 'includes') else {}
                    
                    tweets_data.append({
                        "title": f"@{user.get('username', 'unknown')}: {tweet.text[:100]}...",
                        "content": tweet.text,
                        "url": f"https://twitter.com/i/web/status/{tweet.id}",
                        "source": f"twitter:@{user.get('username', 'unknown')}",
                        "published_at": tweet.created_at,
                        "author": user.get('username', 'unknown'),
                        "metadata": {
                            "retweets": tweet.public_metrics.get('retweet_count', 0) if hasattr(tweet, 'public_metrics') else 0,
                            "likes": tweet.public_metrics.get('like_count', 0) if hasattr(tweet, 'public_metrics') else 0,
                            "followers": user.get('followers_count', 0)
                        }
                    })
            
            print(f"✅ Fetched {len(tweets_data)} tweets")
            return tweets_data
        
        except Exception as e:
            print(f"❌ Twitter API error: {e}")
            return []
    
    def _get_user_info(self, includes, author_id):
        """Extract user info from includes"""
        if not includes or not hasattr(includes, 'users'):
            return {}
        
        for user in includes.users:
            if user.id == author_id:
                return {
                    'username': user.username,
                    'followers_count': user.public_metrics.get('followers_count', 0) if hasattr(user, 'public_metrics') else 0
                }
        return {}
    
    def _mock_tweets(self) -> List[Dict[str, Any]]:
        """Generate mock tweets for testing"""
        return [
            {
                "title": "@SilverBull: Silver prices are mooning! 🚀",
                "content": "Silver prices are mooning! 🚀 Industrial demand at all-time high. #silver #silversqueeze",
                "url": "https://twitter.com/i/web/status/mock1",
                "source": "twitter:@SilverBull",
                "published_at": datetime.utcnow() - timedelta(hours=2),
                "author": "SilverBull",
                "metadata": {"retweets": 45, "likes": 230, "followers": 5000}
            },
            {
                "title": "@KitcoNews: Silver futures climb 3%",
                "content": "Silver futures climb 3% on strong solar panel demand #silver #preciousmetals",
                "url": "https://twitter.com/i/web/status/mock2",
                "source": "twitter:@KitcoNews",
                "published_at": datetime.utcnow() - timedelta(hours=5),
                "author": "KitcoNews",
                "metadata": {"retweets": 120, "likes": 890, "followers": 500000}
            }
        ]


if __name__ == "__main__":
    # Test collector
    async def test():
        collector = TwitterCollector()
        tweets = await collector.fetch_tweets(max_tweets=10, days_back=3)
        
        print(f"\n📊 Collected {len(tweets)} tweets")
        if tweets:
            print(f"\n📰 Sample Tweet:")
            print(f"  {tweets[0]['title']}")
            print(f"  {tweets[0]['content'][:100]}...")
    
    asyncio.run(test())
