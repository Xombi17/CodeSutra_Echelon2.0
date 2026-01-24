"""
Sentiment Analysis Pipeline
Uses VADER for fast, rule-based sentiment analysis
"""
from typing import Dict, Any, List, Optional
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from datetime import datetime, timedelta
from database import get_session, Article
import numpy as np


class SentimentAnalyzer:
    """
    Analyzes sentiment of text content using VADER
    Fast, rule-based, no API calls needed
    """
    
    def __init__(self):
        self.analyzer = SentimentIntensityAnalyzer()
    
    def analyze(self, text: str) -> Dict[str, float]:
        """
        Analyze sentiment of text
        
        Args:
            text: Text to analyze
            
        Returns:
            Dict with compound, positive, negative, neutral scores
        """
        scores = self.analyzer.polarity_scores(text)
        
        return {
            "compound": scores['compound'],  # -1 to 1 (overall)
            "positive": scores['pos'],
            "negative": scores['neg'],
            "neutral": scores['neu'],
            "label": self._get_label(scores['compound'])
        }
    
    def _get_label(self, compound: float) -> str:
        """Convert compound score to label"""
        if compound >= 0.05:
            return "positive"
        elif compound <= -0.05:
            return "negative"
        else:
            return "neutral"
    
    def analyze_batch(self, texts: List[str]) -> List[Dict[str, float]]:
        """Analyze multiple texts"""
        return [self.analyze(text) for text in texts]
    
    def analyze_narrative_sentiment(
        self,
        narrative_id: int,
        hours_back: int = 24
    ) -> Dict[str, Any]:
        """
        Analyze sentiment trend for a narrative
        
        Args:
            narrative_id: Narrative ID
            hours_back: Time window to analyze
            
        Returns:
            Dict with current sentiment, trend, and stats
        """
        session = get_session()
        
        try:
            cutoff = datetime.utcnow() - timedelta(hours=hours_back)
            articles = session.query(Article).filter(
                Article.narrative_id == narrative_id,
                Article.published_at >= cutoff
            ).order_by(Article.published_at).all()
            
            if not articles:
                return {
                    "current_sentiment": 0.0,
                    "trend": "stable",
                    "article_count": 0
                }
            
            # Analyze unanalyzed articles
            for article in articles:
                if article.sentiment_score is None:
                    text = f"{article.title} {article.content or ''}"
                    sentiment = self.analyze(text)
                    article.sentiment_score = sentiment['compound']
                    article.sentiment_label = sentiment['label']
            
            session.commit()
            
            # Calculate metrics
            sentiments = [a.sentiment_score for a in articles if a.sentiment_score is not None]
            
            if not sentiments:
                return {
                    "current_sentiment": 0.0,
                    "trend": "stable",
                    "article_count": 0
                }
            
            current_sentiment = np.mean(sentiments)
            
            # Calculate trend (compare first half vs second half)
            mid_point = len(sentiments) // 2
            if mid_point > 0:
                first_half = np.mean(sentiments[:mid_point])
                second_half = np.mean(sentiments[mid_point:])
                sentiment_change = second_half - first_half
                
                if sentiment_change > 0.1:
                    trend = "improving"
                elif sentiment_change < -0.1:
                    trend = "declining"
                else:
                    trend = "stable"
            else:
                trend = "stable"
                sentiment_change = 0.0
            
            return {
                "current_sentiment": float(current_sentiment),
                "trend": trend,
                "sentiment_change": float(sentiment_change),
                "article_count": len(articles),
                "sentiment_std": float(np.std(sentiments)),
                "positive_ratio": sum(1 for s in sentiments if s > 0.05) / len(sentiments),
                "negative_ratio": sum(1 for s in sentiments if s < -0.05) / len(sentiments)
            }
        
        finally:
            session.close()
    
    def detect_sentiment_inflection(
        self,
        narrative_id: int,
        window_hours: int = 48
    ) -> Optional[Dict[str, Any]]:
        """
        Detect if sentiment is at an inflection point
        
        Returns:
            Dict with inflection info or None
        """
        session = get_session()
        
        try:
            cutoff = datetime.utcnow() - timedelta(hours=window_hours)
            articles = session.query(Article).filter(
                Article.narrative_id == narrative_id,
                Article.published_at >= cutoff,
                Article.sentiment_score != None
            ).order_by(Article.published_at).all()
            
            if len(articles) < 10:
                return None
            
            # Split into thirds
            third = len(articles) // 3
            
            first_third = [a.sentiment_score for a in articles[:third]]
            second_third = [a.sentiment_score for a in articles[third:2*third]]
            third_third = [a.sentiment_score for a in articles[2*third:]]
            
            avg1 = np.mean(first_third)
            avg2 = np.mean(second_third)
            avg3 = np.mean(third_third)
            
            # Detect inflection: middle differs significantly from both sides
            if abs(avg2 - avg1) > 0.2 and abs(avg3 - avg2) > 0.2:
                if (avg2 > avg1 and avg2 > avg3) or (avg2 < avg1 and avg2 < avg3):
                    return {
                        "inflection_detected": True,
                        "type": "peak" if avg2 > avg1 else "trough",
                        "strength": abs(avg2 - avg1) + abs(avg3 - avg2)
                    }
            
            return None
        
        finally:
            session.close()


# Global sentiment analyzer
sentiment_analyzer = SentimentAnalyzer()


if __name__ == "__main__":
    # Test sentiment analyzer
    texts = [
        "Silver prices surge on strong industrial demand!",
        "Mining strike threatens silver supply chain",
        "Silver markets remain stable amid uncertainty"
    ]
    
    print("🧪 Testing Sentiment Analyzer...\n")
    
    for text in texts:
        result = sentiment_analyzer.analyze(text)
        print(f"Text: {text}")
        print(f"Sentiment: {result['label']} ({result['compound']:.2f})")
        print(f"Breakdown: +{result['positive']:.2f} -{result['negative']:.2f} ={result['neutral']:.2f}")
        print()
