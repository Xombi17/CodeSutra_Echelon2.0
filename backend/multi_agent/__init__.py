"""
Multi-Agent System for SilverSentinel
5 specialized agents debate narrative lifecycle phases
"""

from .orchestrator import MultiAgentOrchestrator
from .agents import (
    FundamentalAnalyst,
    SentimentAnalyst,
    TechnicalAnalyst,
    RiskAnalyst,
    MacroAnalyst
)

__all__ = [
    'MultiAgentOrchestrator',
    'FundamentalAnalyst',
    'SentimentAnalyst',
    'TechnicalAnalyst',
    'RiskAnalyst',
    'MacroAnalyst'
]
