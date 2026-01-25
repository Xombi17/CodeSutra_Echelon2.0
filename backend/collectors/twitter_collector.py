"""
Twitter Data Collector
Fetches tweets about silver markets from hashtags and influential accounts
"""
import asyncio
import sys
import os
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional
import tweepy

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import config


class TwitterCollector:
    """Collect tweets about silver markets"""
    
    def __init__(self):
        # Try Bearer Token first (recommended for v2 API)
        self.bearer_token = getattr(config.data, 'twitter_bearer_token', None)
        
        # Fallback to OAuth 1.0a credentials
        self.api_key = config.data.twitter_api_key
        self.api_secret = config.data.twitter_api_secret
        self.access_token = config.data.twitter_access_token
        self.access_secret = config.data.twitter_access_secret
        
        # Debug: Show which keys are configured
        print(f"🔑 Twitter Bearer Token: {'✅ Set' if self.bearer_token else '❌ Missing'}")
        print(f"🔑 Twitter API Key: {'✅ Set' if self.api_key else '❌ Missing'}")
        print(f"🔑 Twitter API Secret: {'✅ Set' if self.api_secret else '❌ Missing'}")
        print(f"🔑 Twitter Access Token: {'✅ Set' if self.access_token else '❌ Missing'}")
        print(f"🔑 Twitter Access Secret: {'✅ Set' if self.access_secret else '❌ Missing'}")
        
        self.client = None
        self.api = None
        
        # Try Bearer Token authentication first (simpler and recommended)
        if self.bearer_token:
            try:
                self.client = tweepy.Client(
                    bearer_token=self.bearer_token,
                    wait_on_rate_limit=True
                )
                # Test with a simple search instead of get_me (which requires OAuth)
                test = self.client.search_recent_tweets(
                    query="test",
                    max_results=10
                )
                print("✅ Twitter API client initialized with Bearer Token")
                return  # Success! Exit here
            except tweepy.Unauthorized as e:
                print(f"❌ Bearer Token authentication failed: {e}")
                print("   Your Bearer Token is invalid or expired")
                print("   Please regenerate it at: https://developer.twitter.com/en/portal/dashboard")
                self.client = None
            except tweepy.Forbidden as e:
                print(f"❌ Access forbidden: {e}")
                print("   Your app may not have the required access level")
                self.client = None
            except Exception as e:
                print(f"❌ Bearer Token error: {e}")
                self.client = None
        
        # If Bearer Token failed, try OAuth 1.0a (only if ALL credentials present)
        if not self.client and all([self.api_key, self.api_secret, self.access_token, self.access_secret]):
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
                # Test with search
                test = self.client.search_recent_tweets(query="test", max_results=10)
                print("✅ Twitter API client initialized with OAuth 1.0a")
            except tweepy.Unauthorized as e:
                print(f"❌ OAuth authentication failed: {e}")
                print("   All OAuth credentials are invalid or expired")
                self.api = None
                self.client = None
            except Exception as e:
                print(f"❌ OAuth error: {e}")
                self.api = None
                self.client = None
        
        # If still no client, we'll use mock data
        if not self.client:
            print("⚠️ Twitter API not available, will use mock data")
    
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
            start_time = datetime.now(timezone.utc) - timedelta(days=days_back)
            
            tweets_data = []
            
            # Search tweets using Twitter API v2
            tweets = self.client.search_recent_tweets(
                query=query,
                max_results=min(max_tweets, 100),  # API limit is 100 per request
                start_time=start_time,
                tweet_fields=['created_at', 'public_metrics', 'author_id'],
                expansions=['author_id'],
                user_fields=['username', 'public_metrics']
            )
            
            if tweets.data:
                # Create user lookup dictionary
                users = {}
                if hasattr(tweets, 'includes') and hasattr(tweets.includes, 'users'):
                    users = {user.id: user for user in tweets.includes.users}
                
                for tweet in tweets.data:
                    # Get user info
                    user = users.get(tweet.author_id)
                    username = user.username if user else 'unknown'
                    followers = user.public_metrics.get('followers_count', 0) if user and hasattr(user, 'public_metrics') else 0
                    
                    tweets_data.append({
                        "title": f"@{username}: {tweet.text[:100]}...",
                        "content": tweet.text,
                        "url": f"https://twitter.com/i/web/status/{tweet.id}",
                        "source": f"twitter:@{username}",
                        "published_at": tweet.created_at,
                        "author": username,
                        "metadata": {
                            "retweets": tweet.public_metrics.get('retweet_count', 0) if hasattr(tweet, 'public_metrics') else 0,
                            "likes": tweet.public_metrics.get('like_count', 0) if hasattr(tweet, 'public_metrics') else 0,
                            "followers": followers
                        }
                    })
            
            print(f"✅ Fetched {len(tweets_data)} tweets")
            return tweets_data
        
        except tweepy.Unauthorized as e:
            print(f"❌ Twitter API Unauthorized: {e}")
            return self._mock_tweets()
        except tweepy.TooManyRequests as e:
            print(f"⚠️ Rate limit exceeded: {e}")
            return self._mock_tweets()
        except Exception as e:
            print(f"❌ Twitter API error: {e}")
            return self._mock_tweets()
    
    def _mock_tweets(self) -> List[Dict[str, Any]]:
        """Generate mock tweets for testing"""
        now = datetime.now(timezone.utc)
        
        return [
            {
                "title": "@SilverBull: Silver prices are mooning! 🚀",
                "content": "Silver prices are mooning! 🚀 Industrial demand at all-time high. #silver #silversqueeze",
                "url": "https://twitter.com/i/web/status/mock1",
                "source": "twitter:@SilverBull",
                "published_at": now - timedelta(hours=2),
                "author": "SilverBull",
                "metadata": {"retweets": 45, "likes": 230, "followers": 5000}
            },
            {
                "title": "@KitcoNews: Silver futures climb 3%",
                "content": "Silver futures climb 3% on strong solar panel demand #silver #preciousmetals",
                "url": "https://twitter.com/i/web/status/mock2",
                "source": "twitter:@KitcoNews",
                "published_at": now - timedelta(hours=5),
                "author": "KitcoNews",
                "metadata": {"retweets": 120, "likes": 890, "followers": 500000}
            },
            {
                "title": "@MetalsDaily: Breaking - Silver ETF inflows surge",
                "content": "Breaking: Silver ETF inflows reach highest level in 18 months. Institutional buying accelerating. #silver #investing",
                "url": "https://twitter.com/i/web/status/mock3",
                "source": "twitter:@MetalsDaily",
                "published_at": now - timedelta(hours=8),
                "author": "MetalsDaily",
                "metadata": {"retweets": 78, "likes": 456, "followers": 25000}
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