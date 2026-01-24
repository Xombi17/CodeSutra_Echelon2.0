"""
Database Models and Schema
SQLAlchemy ORM models for SilverSentinel
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, JSON, ForeignKey, CheckConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from config import config

Base = declarative_base()


class Narrative(Base):
    """Market narrative with lifecycle tracking"""
    __tablename__ = "narratives"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False, index=True)
    phase = Column(String(20), nullable=False, default="birth")
    strength = Column(Integer, nullable=False, default=0)
    sentiment = Column(Float, nullable=False, default=0.0)
    
    # Lifecycle timestamps
    birth_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    last_updated = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    death_date = Column(DateTime, nullable=True)
    
    # Metrics
    article_count = Column(Integer, default=0)
    mention_velocity = Column(Float, default=0.0)  # mentions per hour
    price_correlation = Column(Float, default=0.0)
    
    # Metadata
    parent_narrative_id = Column(Integer, ForeignKey("narratives.id"), nullable=True)
    cluster_keywords = Column(JSON, nullable=True)  # Top keywords from clustering
    
    # Relationships
    children = relationship("Narrative", backref="parent", remote_side=[id])
    articles = relationship("Article", back_populates="narrative")
    
    __table_args__ = (
        CheckConstraint("phase IN ('birth', 'growth', 'peak', 'reversal', 'death')", name="valid_phase"),
        CheckConstraint("strength >= 0 AND strength <= 100", name="valid_strength"),
        CheckConstraint("sentiment >= -1.0 AND sentiment <= 1.0", name="valid_sentiment"),
    )
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "phase": self.phase,
            "strength": self.strength,
            "sentiment": self.sentiment,
            "birth_date": self.birth_date.isoformat() if self.birth_date else None,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None,
            "age_days": (datetime.utcnow() - self.birth_date).days if self.birth_date else 0,
            "article_count": self.article_count,
            "mention_velocity": self.mention_velocity,
            "price_correlation": self.price_correlation,
            "parent_id": self.parent_narrative_id,
            "cluster_keywords": self.cluster_keywords
        }


class Article(Base):
    """News articles and social media posts"""
    __tablename__ = "articles"
    
    id = Column(Integer, primary_key=True)
    narrative_id = Column(Integer, ForeignKey("narratives.id"), nullable=True)
    
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=True)
    url = Column(String(1000), nullable=True, unique=True)
    source = Column(String(100), nullable=False)  # newsapi, reddit, twitter
    
    published_at = Column(DateTime, nullable=False)
    fetched_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Sentiment analysis
    sentiment_score = Column(Float, nullable=True)
    sentiment_label = Column(String(20), nullable=True)  # positive, negative, neutral
    
    # Metadata
    author = Column(String(200), nullable=True)
    article_metadata = Column(JSON, nullable=True)  # Additional source-specific data
    
    # Relationships
    narrative = relationship("Narrative", back_populates="articles")
    
    def to_dict(self):
        return {
            "id": self.id,
            "narrative_id": self.narrative_id,
            "title": self.title,
            "url": self.url,
            "source": self.source,
            "published_at": self.published_at.isoformat() if self.published_at else None,
            "sentiment_score": self.sentiment_score,
            "sentiment_label": self.sentiment_label
        }


class PriceData(Base):
    """Silver price history"""
    __tablename__ = "price_history"
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    price = Column(Float, nullable=False)
    
    # OHLCV data
    open_price = Column(Float, nullable=True)
    high_price = Column(Float, nullable=True)
    low_price = Column(Float, nullable=True)
    close_price = Column(Float, nullable=True)
    volume = Column(Float, nullable=True)
    
    source = Column(String(50), nullable=False, default="yfinance")
    
    def to_dict(self):
        return {
            "timestamp": self.timestamp.isoformat(),
            "price": self.price,
            "open": self.open_price,
            "high": self.high_price,
            "low": self.low_price,
            "close": self.close_price,
            "volume": self.volume
        }


class TradingSignal(Base):
    """Trading signals generated by the agent"""
    __tablename__ = "trading_signals"
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    action = Column(String(10), nullable=False)  # BUY, SELL, HOLD
    confidence = Column(Float, nullable=False)
    strength = Column(Integer, nullable=False)
    
    # Reasoning
    dominant_narrative_id = Column(Integer, ForeignKey("narratives.id"), nullable=True)
    reasoning = Column(Text, nullable=True)
    position_size = Column(Float, nullable=True)
    
    # Market context
    price_at_signal = Column(Float, nullable=True)
    volatility = Column(Float, nullable=True)
    
    # Metadata
    signal_metadata = Column(JSON, nullable=True)
    
    __table_args__ = (
        CheckConstraint("action IN ('BUY', 'SELL', 'HOLD')", name="valid_action"),
        CheckConstraint("confidence >= 0.0 AND confidence <= 1.0", name="valid_confidence"),
    )
    
    def to_dict(self):
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "action": self.action,
            "confidence": self.confidence,
            "strength": self.strength,
            "reasoning": self.reasoning,
            "position_size": self.position_size,
            "price": self.price_at_signal
        }


class Portfolio(Base):
    """User portfolio holdings"""
    __tablename__ = "portfolio"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String(100), nullable=False, index=True)
    
    # Holdings
    physical_silver_grams = Column(Float, default=0.0)
    paper_silver_grams = Column(Float, default=0.0)  # ETF equivalent
    
    # Valuation
    average_buy_price = Column(Float, nullable=True)
    current_value = Column(Float, nullable=True)
    
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SilverScan(Base):
    """Physical silver scans (CV feature - Phase 8)"""
    __tablename__ = "scans"
    
    id = Column(String(100), primary_key=True)  # UUID string
    user_id = Column(String(100), nullable=False)

    
    image_path = Column(String(500), nullable=False)
    detected_type = Column(String(100), nullable=True)  # chain, coin, bar, jewelry
    
    # Analysis results
    purity = Column(Integer, nullable=True)  # 925, 999, etc.
    estimated_weight = Column(Float, nullable=True)
    estimated_dimensions = Column(JSON, nullable=True)  # {length, width, thickness}
    
    valuation_min = Column(Float, nullable=True)
    valuation_max = Column(Float, nullable=True)
    confidence = Column(Float, nullable=True)
    
    # Market context
    narrative_context = Column(JSON, nullable=True)  # Active narratives at scan time
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            "id": self.id,
            "detected_type": self.detected_type,
            "purity": self.purity,
            "weight": self.estimated_weight,
            "valuation_range": {
                "min": self.valuation_min,
                "max": self.valuation_max
            },
            "confidence": self.confidence,
            "created_at": self.created_at.isoformat()
        }


class AgentVote(Base):
    """Store multi-agent voting history"""
    __tablename__ = "agent_votes"
    
    id = Column(Integer, primary_key=True)
    narrative_id = Column(Integer, ForeignKey("narratives.id"))
    agent_name = Column(String(50), nullable=False)  # "fundamental", "sentiment", etc.
    
    # Vote details
    phase_vote = Column(String(20), nullable=False)
    strength_vote = Column(Integer, nullable=False)
    confidence = Column(Float, nullable=False)
    reasoning = Column(Text, nullable=True)
    
    # Metadata
    timestamp = Column(DateTime, default=datetime.utcnow)
    debate_round = Column(Integer, default=1)
    
    # Relationships
    narrative = relationship("Narrative", backref="agent_votes")
    
    def to_dict(self):
        return {
            "id": self.id,
            "agent_name": self.agent_name,
            "phase_vote": self.phase_vote,
            "strength_vote": self.strength_vote,
            "confidence": self.confidence,
            "reasoning": self.reasoning,
            "timestamp": self.timestamp.isoformat(),
            "debate_round": self.debate_round
        }


class NarrativeSnapshot(Base):
    """Track narrative evolution over time"""
    __tablename__ = "narrative_snapshots"
    
    id = Column(Integer, primary_key=True)
    narrative_id = Column(Integer, ForeignKey("narratives.id"))
    
    # Snapshot data
    phase = Column(String(20), nullable=False)
    strength = Column(Integer, nullable=False)
    sentiment = Column(Float, nullable=False)
    
    # Metrics at this point
    velocity = Column(Float)
    price_correlation = Column(Float)
    article_count = Column(Integer)
    
    # Analysis details
    analysis_method = Column(String(20))  # "metrics", "multi-agent", "hybrid"
    confidence = Column(Float)
    agent_consensus_data = Column(JSON, nullable=True)  # Store agent votes
    
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    narrative = relationship("Narrative", backref="snapshots")
    
    def to_dict(self):
        return {
            "id": self.id,
            "phase": self.phase,
            "strength": self.strength,
            "sentiment": self.sentiment,
            "velocity": self.velocity,
            "price_correlation": self.price_correlation,
            "analysis_method": self.analysis_method,
            "confidence": self.confidence,
            "timestamp": self.timestamp.isoformat()
        }


# Database initialization
def init_database():
    """Initialize database and create tables"""
    engine = create_engine(f"sqlite:///{config.database.sqlite_path}")
    Base.metadata.create_all(engine)
    return engine


def get_session():
    """Get database session"""
    engine = create_engine(f"sqlite:///{config.database.sqlite_path}")
    Session = sessionmaker(bind=engine)
    return Session()


if __name__ == "__main__":
    # Test database creation
    engine = init_database()
    print(f"✅ Database initialized at: {config.database.sqlite_path}")
    print(f"📊 Tables created: {list(Base.metadata.tables.keys())}")
