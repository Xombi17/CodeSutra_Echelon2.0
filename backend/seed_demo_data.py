"""
Demo Data Seeder
Creates sample narratives, articles, and price data for testing
"""
import asyncio
from datetime import datetime, timedelta
import random
from database import get_session, Narrative, Article, PriceData, init_database
from narrative.sentiment_analyzer import sentiment_analyzer


class DemoDataSeeder:
    """Seed database with realistic demo data"""
    
    def __init__(self):
        self.session = get_session()
    
    async def seed_all(self):
        """Seed all demo data"""
        print("🌱 Seeding demo data...")
        
        # Initialize database
        init_database()
        
        # Clear existing data (for demo purposes)
        self.clear_existing_data()
        
        # Seed data
        await self.seed_price_data()
        await self.seed_articles()
        await self.seed_narratives()
        
        print("✅ Demo data seeded successfully!")
    
    def clear_existing_data(self):
        """Clear existing data"""
        print("🗑️ Clearing existing data...")
        
        try:
            self.session.query(Article).delete()
            self.session.query(Narrative).delete()
            self.session.query(PriceData).delete()
            self.session.commit()
            print("✅ Data cleared")
        except Exception as e:
            self.session.rollback()
            print(f"❌ Error clearing data: {e}")
    
    async def seed_price_data(self):
        """Seed realistic price data for last 30 days"""
        print("💰 Seeding price data...")
        
        base_price = 75000  # ₹75,000 per kg
        prices = []
        
        # Generate 30 days of hourly price data
        for day in range(30):
            for hour in range(24):
                timestamp = datetime.utcnow() - timedelta(days=30-day, hours=24-hour)
                
                # Add some realistic volatility
                volatility = random.gauss(0, 500)  # ±500 variance
                trend = (day - 15) * 50  # Slight upward trend
                price = base_price + volatility + trend
                
                price_data = PriceData(
                    timestamp=timestamp,
                    price=round(price, 2),
                    open_price=round(price * 0.998, 2),
                    high_price=round(price * 1.002, 2),
                    low_price=round(price * 0.997, 2),
                    close_price=round(price, 2),
                    volume=random.randint(100000, 500000),
                    source="demo_seed"
                )
                prices.append(price_data)
        
        self.session.bulk_save_objects(prices)
        self.session.commit()
        print(f"✅ Created {len(prices)} price points")
    
    async def seed_articles(self):
        """Seed sample articles"""
        print("📰 Seeding articles...")
        
        article_templates = [
            # Mining Strike narrative
            {
                "title": "Peru mining strike enters second week, threatens silver supply",
                "content": "Workers at one of Peru's largest silver mines continue their strike over wages...",
                "sentiment": -0.6,
                "narrative": "Mining Strike"
            },
            {
                "title": "Silver production disruption feared as Peru negotiations stall",
                "content": "Union representatives report no progress in talks with mining companies...",
                "sentiment": -0.7,
                "narrative": "Mining Strike"
            },
            # Industrial Demand narrative
            {
                "title": "Solar panel manufacturers increase silver orders by 30%",
                "content": "Renewable energy boom drives unprecedented demand for silver paste...",
                "sentiment": 0.8,
                "narrative": "Industrial Solar Demand"
            },
            {
                "title": "Electric vehicle production boosts silver demand",
                "content": "Each EV requires 25-50 grams of silver for electronics and sensors...",
                "sentiment": 0.7,
                "narrative": "Industrial Solar Demand"
            },
            {
                "title": "Green energy transition to consume record silver volumes in 2024",
                "content": "Industry analysts predict solar and wind installations will drive silver above $30/oz...",
                "sentiment": 0.9,
                "narrative": "Industrial Solar Demand"
            },
            # Wedding Season narrative
            {
                "title": "Indian wedding season drives silver jewelry demand",
                "content": "Retailers report 40% increase in silver ornament sales ahead of wedding season...",
                "sentiment": 0.6,
                "narrative": "Wedding Season Demand"
            },
            {
                "title": "Silver prices surge on festive buying in India",
                "content": "Diwali and wedding season create perfect storm for silver retailers...",
                "sentiment": 0.5,
                "narrative": "Wedding Season Demand"
            },
            # Fed Rate narrative (bearish)
            {
                "title": "Federal Reserve hints at further rate hikes",
                "content": "Fed officials signal continued tightening could pressure precious metals...",
                "sentiment": -0.5,
                "narrative": "Fed Rate Concerns"
            },
            {
                "title": "Rising interest rates weigh on non-yielding assets",
                "content": "Analysts warn higher rates make silver less attractive vs bonds...",
                "sentiment": -0.4,
                "narrative": "Fed Rate Concerns"
            }
        ]
        
        articles = []
        for i, template in enumerate(article_templates):
            # Create multiple articles per template over time
            for day_offset in range(7):
                article = Article(
                    title=template["title"],
                    content=template["content"],
                    url=f"https://example.com/article-{i}-{day_offset}",
                    source="demo_seed:newsapi",
                    published_at=datetime.utcnow() - timedelta(days=14-day_offset, hours=random.randint(0, 23)),
                    sentiment_score=template["sentiment"] + random.gauss(0, 0.1),
                    sentiment_label="positive" if template["sentiment"] > 0 else "negative",
                    author="Demo Author"
                )
                articles.append(article)
        
        self.session.bulk_save_objects(articles)
        self.session.commit()
        print(f"✅ Created {len(articles)} articles")
    
    async def seed_narratives(self):
        """Seed sample narratives"""
        print("📊 Seeding narratives...")
        
        narratives_data = [
            {
                "name": "Industrial Solar Demand",
                "phase": "growth",
                "strength": 85,
                "sentiment": 0.75,
                "age_days": 12
            },
            {
                "name": "Mining Strike",
                "phase": "peak",
                "strength": 72,
                "sentiment": -0.65,
                "age_days": 10
            },
            {
                "name": "Wedding Season Demand",
                "phase": "growth",
                "strength": 68,
                "sentiment": 0.55,
                "age_days": 8
            },
            {
                "name": "Fed Rate Concerns",
                "phase": "birth",
                "strength": 45,
                "sentiment": -0.45,
                "age_days": 3
            }
        ]
        
        for data in narratives_data:
            narrative = Narrative(
                name=data["name"],
                phase=data["phase"],
                strength=data["strength"],
                sentiment=data["sentiment"],
                birth_date=datetime.utcnow() - timedelta(days=data["age_days"]),
                last_updated=datetime.utcnow(),
                article_count=random.randint(15, 40),
                mention_velocity=random.uniform(2.0, 8.0),
                price_correlation=random.uniform(0.3, 0.85),
                cluster_keywords={"keywords": ["silver", "market", "demand"]}
            )
            self.session.add(narrative)
        
        self.session.commit()
        
        # Assign articles to narratives
        narratives = self.session.query(Narrative).all()
        articles = self.session.query(Article).all()
        
        for article in articles:
            # Find matching narrative based on content
            for narrative in narratives:
                if narrative.name.lower().replace(" demand", "").replace(" concerns", "") in article.content.lower():
                    article.narrative_id = narrative.id
                    break
        
        self.session.commit()
        print(f"✅ Created {len(narratives_data)} narratives")
    
    def close(self):
        """Close session"""
        self.session.close()


async def main():
    """Run seeder"""
    seeder = DemoDataSeeder()
    
    try:
        await seeder.seed_all()
        
        # Print summary
        print("\n" + "="*50)
        print("📊 Database Summary")
        print("="*50)
        
        session = get_session()
        
        narrative_count = session.query(Narrative).count()
        article_count = session.query(Article).count()
        price_count = session.query(PriceData).count()
        
        print(f"Narratives: {narrative_count}")
        print(f"Articles: {article_count}")
        print(f"Price Points: {price_count}")
        
        # Show narratives
        print("\n📌 Active Narratives:")
        narratives = session.query(Narrative).order_by(Narrative.strength.desc()).all()
        for n in narratives:
            print(f"  • {n.name} ({n.phase}) - Strength: {n.strength}/100")
        
        session.close()
        
    finally:
        seeder.close()


if __name__ == "__main__":
    asyncio.run(main())
