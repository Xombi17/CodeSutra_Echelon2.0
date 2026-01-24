"""
StockTwits Data Collector
Fetches messages from StockTwits with built-in sentiment labels
"""
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any
import requests


class StockTwitsCollector:
    """Collect messages from StockTwits"""
    
    def __init__(self):
        self.base_url = "https://api.stocktwits.com/api/2"
        # No API key needed - public API
    
    async def fetch_messages(
        self,
        symbols: List[str] = ["SILVER", "SLV", "AG", "PSLV"],
        limit_per_symbol: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Fetch messages from StockTwits
        
        Args:
            symbols: Stock/commodity symbols to track
            limit_per_symbol: Max messages per symbol
        """
        all_messages = []
        
        for symbol in symbols:
            try:
                url = f"{self.base_url}/streams/symbol/{symbol}.json"
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                data = response.json()
                
                messages = data.get('messages', [])
                
                for msg in messages[:limit_per_symbol]:
                    # Extract sentiment
                    sentiment_data = msg.get('entities', {}).get('sentiment', {})
                    sentiment = sentiment_data.get('basic') if sentiment_data else None
                    
                    all_messages.append({
                        "title": f"${symbol}: {msg.get('body', '')[:100]}...",
                        "content": msg.get('body', ''),
                        "url": f"https://stocktwits.com/message/{msg.get('id')}",
                        "source": f"stocktwits:${symbol}",
                        "published_at": self._parse_timestamp(msg.get('created_at')),
                        "author": msg.get('user', {}).get('username', 'unknown'),
                        "metadata": {
                            "sentiment": sentiment,  # "Bullish" or "Bearish"
                            "likes": msg.get('likes', {}).get('total', 0),
                            "followers": msg.get('user', {}).get('followers', 0),
                            "symbol": symbol
                        }
                    })
                
                print(f"✅ Fetched {len(messages[:limit_per_symbol])} messages for ${symbol}")
                
            except Exception as e:
                print(f"❌ StockTwits error for ${symbol}: {e}")
                continue
        
        return all_messages
    
    def _parse_timestamp(self, timestamp_str: str) -> datetime:
        """Parse StockTwits timestamp format"""
        try:
            # Format: "2024-01-15T10:30:00Z"
            return datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%S%z")
        except:
            return datetime.utcnow()


if __name__ == "__main__":
    # Test collector
    async def test():
        collector = StockTwitsCollector()
        messages = await collector.fetch_messages(symbols=["SILVER", "SLV"], limit_per_symbol=5)
        
        print(f"\n📊 Collected {len(messages)} messages")
        if messages:
            print(f"\n📰 Sample Message:")
            print(f"  {messages[0]['title']}")
            print(f"  Sentiment: {messages[0]['metadata'].get('sentiment', 'N/A')}")
    
    asyncio.run(test())
