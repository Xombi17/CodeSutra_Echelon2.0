"""
SilverSentinel Configuration Management
Centralized configuration for API keys, model settings, and thresholds
"""
import os
from dataclasses import dataclass
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()


@dataclass
class ModelConfig:
    """Model provider configuration"""
    # Groq API
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")
    groq_rate_limit: int = 30  # requests per minute
    
    # Google Gemini API (alternative to Ollama for vision)
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    
    # HuggingFace
    hf_token: str = os.getenv("HF_TOKEN", "")
    
    # Model selections
    vision_primary: str = "llama-3.2-90b-vision-preview"  # Groq
    vision_backup: str = "gemini-2.0-flash-exp"  # Google Gemini (free)
    vision_validator: str = "Qwen/Qwen2-VL-7B-Instruct"  # HF
    
    text_narrative: str = "llama-3.3-70b-versatile"  # Groq
    text_clustering: str = "mixtral-8x7b-32768"  # Groq
    text_local: str = "gemma-2.0-flash-001"  # Google Gemini fallback


@dataclass
class DataConfig:
    """Data source configuration"""
    # News API
    news_api_key: str = os.getenv("NEWS_API_KEY", "")
    news_base_url: str = "https://newsapi.org/v2"
    
    # Twitter/X API v2 (Bearer Token - RECOMMENDED)
    twitter_bearer_token: str = os.getenv("TWITTER_BEARER_TOKEN", "")
    
    # Twitter/X API (OAuth 1.0a - Fallback)
    twitter_api_key: str = os.getenv("TWITTER_API_KEY", "")
    twitter_api_secret: str = os.getenv("TWITTER_API_SECRET", "")
    twitter_access_token: str = os.getenv("TWITTER_ACCESS_TOKEN", "")
    twitter_access_secret: str = os.getenv("TWITTER_ACCESS_SECRET", "")
    
    
    
    # Telegram API
    telegram_api_id: str = os.getenv("TELEGRAM_API_ID", "")
    telegram_api_hash: str = os.getenv("TELEGRAM_API_HASH", "")
    telegram_phone: str = os.getenv("TELEGRAM_PHONE", "")
    
    # Yahoo Finance (no key needed)
    yfinance_symbol: str = "SLV"  # Silver futures
    
    # Data refresh intervals (minutes)
    high_volatility_interval: int = 10
    medium_volatility_interval: int = 30
    low_volatility_interval: int = 120
    
    # Source weighting for narrative discovery
    source_weights: Dict[str, float] = None
    
    def __post_init__(self):
        if self.source_weights is None:
            self.source_weights = {
                "twitter": 1.5,      # High influence
                "news": 1.2,         # Professional journalism
                "reddit": 1.0,       # Baseline community sentiment
                "telegram": 0.8,     # Early signals but noisy
                   # Trading community sentiment
            }


@dataclass
class NarrativeConfig:
    """Narrative intelligence thresholds"""
    # Clustering
    min_cluster_size: int = 3
    min_articles_for_clustering: int = 50
    
    # Lifecycle phase transitions
    birth_to_growth_velocity_threshold: float = 0.5  # 50% increase
    growth_to_peak_correlation_threshold: float = 0.8
    peak_to_reversal_sentiment_decline: float = 0.3
    reversal_to_death_silence_hours: int = 48
    
    # Strength scoring weights
    social_velocity_weight: float = 0.3
    news_intensity_weight: float = 0.25
    price_correlation_weight: float = 0.25
    institutional_alignment_weight: float = 0.2
    
    # Conflict detection
    min_strength_for_conflict: int = 40
    
    # Discovery Engine Settings
    embedding_model: str = "all-MiniLM-L6-v2"
    theme_extraction_model: str = "llama-3.3-70b-versatile"  # Uses Groq
    
    # Discovery clustering parameters
    discovery_min_cluster_size: int = 3
    discovery_min_samples: int = 2
    
    # Relevance thresholds
    relevance_percentile_threshold: int = 20  # Keep top 80%
    min_articles_for_discovery: int = 3
    
    # Theme extraction
    max_sample_articles_for_themes: int = 20
    target_theme_count: int = 6
    
    # Ranking
    default_top_n: int = 5


@dataclass
class TradingConfig:
    """Trading agent settings"""
    # Signal generation
    high_conviction_strength: int = 75
    high_conviction_confidence: float = 0.8
    low_confidence_threshold: float = 0.6
    
    # Risk management
    max_position_size: float = 1.5  # 150% max
    conflict_size_reduction: float = 0.5  # 50% reduction
    
    # Stability monitoring
    stability_window_days: int = 30
    high_stability_volatility_threshold: float = 0.5
    medium_stability_volatility_threshold: float = 1.0


@dataclass
class DatabaseConfig:
    """Database configuration"""
    sqlite_path: str = "silversentinel.db"  # In current working directory
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    cache_ttl_seconds: int = 3600  # 1 hour


@dataclass
class MultiAgentConfig:
    """Multi-agent system configuration"""
    # Agent settings
    num_agents: int = 5
    debate_rounds_max: int = 3
    consensus_threshold: float = 0.6  # 60% agreement needed
    
    # LLM settings
    agent_temperature: float = 0.3  # Lower = more consistent
    max_tokens_per_agent: int = 500
    
    # Fallback behavior
    use_metrics_fallback: bool = True  # Use main's metrics if agents fail
    fallback_confidence: float = 0.65


@dataclass
class HybridConfig:
    """Hybrid engine configuration"""
    # Weighting between methods
    agent_weight: float = 0.6   # 60% weight on multi-agent
    metrics_weight: float = 0.4  # 40% weight on metrics
    
    # Confidence thresholds
    high_confidence_threshold: float = 0.75
    use_agents_above_threshold: bool = True
    
    # Performance
    enable_parallel_analysis: bool = True
    cache_agent_results: bool = True
    cache_ttl_minutes: int = 15


@dataclass
class AppConfig:
    """Main application configuration"""
    model: ModelConfig
    data: DataConfig
    narrative: NarrativeConfig
    trading: TradingConfig
    database: DatabaseConfig
    multi_agent: MultiAgentConfig
    hybrid: HybridConfig
    
    # Application settings
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    
    # WebSocket
    websocket_ping_interval: int = 30
    websocket_max_connections: int = 100


def load_config() -> AppConfig:
    """Load and return application configuration"""
    return AppConfig(
        model=ModelConfig(),
        data=DataConfig(),
        narrative=NarrativeConfig(),
        trading=TradingConfig(),
        database=DatabaseConfig(),
        multi_agent=MultiAgentConfig(),
        hybrid=HybridConfig()
    )


# Global config instance
config = load_config()


def validate_config() -> Dict[str, Any]:
    """Validate configuration and return status"""
    issues = []
    
    # Check critical API keys
    if not config.model.groq_api_key:
        issues.append("GROQ_API_KEY not set")
    
    if not config.data.news_api_key:
        issues.append("NEWS_API_KEY not set (optional but recommended)")
    
    if not config.data.reddit_client_id or not config.data.reddit_client_secret:
        issues.append("Reddit credentials not set (optional)")
    
    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "warnings": [i for i in issues if "optional" in i.lower()],
        "errors": [i for i in issues if "optional" not in i.lower()]
    }


if __name__ == "__main__":
    # Test configuration
    validation = validate_config()
    print(f"Configuration validation: {'✅ PASS' if validation['valid'] else '❌ FAIL'}")
    
    if validation['errors']:
        print("\n🔴 Errors:")
        for error in validation['errors']:
            print(f"  - {error}")
    
    if validation['warnings']:
        print("\n🟡 Warnings:")
        for warning in validation['warnings']:
            print(f"  - {warning}")
    
    print(f"\n📊 Configuration loaded:")
    print(f"  - Vision model: {config.model.vision_primary}")
    print(f"  - Text model: {config.model.text_narrative}")
    print(f"  - Database: {config.database.sqlite_path}")
    print(f"  - Debug mode: {config.debug}")
