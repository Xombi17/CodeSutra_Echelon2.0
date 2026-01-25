"""
Telegram Data Collector
Fetches messages from public Telegram channels
"""
import asyncio
import sys
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any
from telethon import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import config


class TelegramCollector:
    """Collect messages from Telegram channels"""
    
    def __init__(self):
        self.api_id = config.data.telegram_api_id
        self.api_hash = config.data.telegram_api_hash
        self.session_name = "silversentinel_session"
        
        if not self.api_id or not self.api_hash:
            print("⚠️ Telegram API credentials not configured, using mock data")
            self.client = None
        else:
            try:
                self.client = TelegramClient(self.session_name, self.api_id, self.api_hash)
            except Exception as e:
                print(f"⚠️ Telegram client initialization error: {e}")
                self.client = None
    
    async def fetch_messages(
        self,
        channels: List[str] = ["@SilverSqueeze", "@SilverNews", "@PreciousMetalsNews"],
        limit_per_channel: int = 50,
        days_back: int = 7
    ) -> List[Dict[str, Any]]:
        """
        Fetch messages from Telegram channels
        
        Args:
            channels: List of channel usernames
            limit_per_channel: Max messages per channel
            days_back: How many days to look back
        """
        if not self.client:
            print("⚠️ Telegram API not configured, using mock data")
            return self._mock_messages()
        
        all_messages = []
        
        try:
            await self.client.start()
            
            cutoff_date = datetime.utcnow() - timedelta(days=days_back)
            
            for channel_username in channels:
                try:
                    # Get channel entity
                    channel = await self.client.get_entity(channel_username)
                    
                    # Fetch message history
                    history = await self.client(GetHistoryRequest(
                        peer=channel,
                        limit=limit_per_channel,
                        offset_date=None,
                        offset_id=0,
                        max_id=0,
                        min_id=0,
                        add_offset=0,
                        hash=0
                    ))
                    
                    for message in history.messages:
                        # Skip if message is too old
                        if message.date and message.date.replace(tzinfo=None) < cutoff_date:
                            continue
                        
                        # Skip if no text
                        if not message.message:
                            continue
                        
                        all_messages.append({
                            "title": f"{channel_username}: {message.message[:100]}...",
                            "content": message.message,
                            "url": f"https://t.me/{channel_username.replace('@', '')}/{message.id}",
                            "source": f"telegram:{channel_username}",
                            "published_at": message.date.replace(tzinfo=None) if message.date else datetime.utcnow(),
                            "author": channel_username,
                            "metadata": {
                                "views": message.views if hasattr(message, 'views') else 0,
                                "forwards": message.forwards if hasattr(message, 'forwards') else 0,
                                "channel": channel_username
                            }
                        })
                    
                    print(f"✅ Fetched {len(history.messages)} messages from {channel_username}")
                    
                except Exception as e:
                    print(f"❌ Telegram error for {channel_username}: {e}")
                    continue
            
            return all_messages
        
        except Exception as e:
            print(f"❌ Telegram API error: {e}")
            return []
        
        finally:
            if self.client:
                await self.client.disconnect()
    
    def _mock_messages(self) -> List[Dict[str, Any]]:
        """Generate mock Telegram messages for testing"""
        return [
            {
                "title": "@SilverSqueeze: Major silver supply shortage incoming",
                "content": "Major silver supply shortage incoming 🚨 Peru mine strike continues, wedding season demand surging!",
                "url": "https://t.me/SilverSqueeze/mock1",
                "source": "telegram:@SilverSqueeze",
                "published_at": datetime.utcnow() - timedelta(hours=3),
                "author": "@SilverSqueeze",
                "metadata": {"views": 15000, "forwards": 450, "channel": "@SilverSqueeze"}
            },
            {
                "title": "@SilverNews: Central banks increasing silver reserves",
                "content": "Central banks increasing silver reserves for the first time in 20 years. Bullish signal for precious metals.",
                "url": "https://t.me/SilverNews/mock2",
                "source": "telegram:@SilverNews",
                "published_at": datetime.utcnow() - timedelta(hours=8),
                "author": "@SilverNews",
                "metadata": {"views": 8500, "forwards": 190, "channel": "@SilverNews"}
            }
        ]


if __name__ == "__main__":
    # Test collector
    async def test():
        collector = TelegramCollector()
        messages = await collector.fetch_messages(
            channels=["@SilverSqueeze", "@SilverNews"],
            limit_per_channel=10,
            days_back=3
        )
        
        print(f"\n📊 Collected {len(messages)} messages")
        if messages:
            print(f"\n📰 Sample Message:")
            print(f"  {messages[0]['title']}")
            print(f"  Views: {messages[0]['metadata'].get('views', 0)}")
    
    asyncio.run(test())
