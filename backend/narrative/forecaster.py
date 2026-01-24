"""
Predictive Narrative Forecasting Engine
Predicts future phase transitions and price impact 48h in advance
"""
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from database import Narrative

class NarrativeForecaster:
    """
    Forecasting engine for narrative lifecycle and market impact
    """
    
    def predict_lifecycle(self, narrative: Narrative) -> Dict[str, Any]:
        """
        Predict the next likely phase transition
        """
        current_phase = narrative.phase
        velocity = narrative.mention_velocity or 0.0
        age_days = (datetime.utcnow() - narrative.birth_date).days if narrative.birth_date else 0
        sentiment = narrative.sentiment or 0.0
        
        prediction = {
            "current_phase": current_phase,
            "next_phase": None,
            "probability": 0.0,
            "timeframe_hours": 48,
            "reasoning": ""
        }
        
        # Logic Matrix
        if current_phase == "birth":
            if velocity > 5.0 and sentiment > 0.1:
                prediction["next_phase"] = "growth"
                prediction["probability"] = 0.85
                prediction["reasoning"] = "High velocity and positive sentiment indicate imminent breakout"
            else:
                prediction["next_phase"] = "death"
                prediction["probability"] = 0.40
                prediction["reasoning"] = "Low momentum may lead to early narrative death"
                
        elif current_phase == "growth":
            if age_days > 7 and velocity < 2.0:
                prediction["next_phase"] = "peak"
                prediction["probability"] = 0.75
                prediction["reasoning"] = "Maturing narrative with slowing momentum suggests peak approaching"
            elif velocity > 10.0:
                prediction["next_phase"] = "peak"
                prediction["probability"] = 0.60
                prediction["reasoning"] = "Explosive velocity often leads to rapid exhaustion/peak"
            else:
                prediction["next_phase"] = "growth"
                prediction["probability"] = 0.90
                prediction["reasoning"] = "Strong steady growth likely to continue"
        
        elif current_phase == "peak":
            if sentiment < 0:
                prediction["next_phase"] = "reversal"
                prediction["probability"] = 0.80
                prediction["reasoning"] = "Negative sentiment following peak strongly signals reversal"
            else:
                prediction["next_phase"] = "reversal"
                prediction["probability"] = 0.65
                prediction["reasoning"] = "Peaks naturally degrade into reversals within 48-72h"
                
        elif current_phase == "reversal":
            prediction["next_phase"] = "death"
            prediction["probability"] = 0.95
            prediction["reasoning"] = "Reversal typically leads to narrative death"
            
        return prediction

    def predict_price_impact(self, narrative: Narrative) -> Dict[str, Any]:
        """
        Predict impact on silver price
        """
        # Simple heuristic model
        strength = narrative.strength or 0
        sentiment = narrative.sentiment or 0.0
        
        impact = {
            "direction": "neutral",
            "magnitude_percentage": 0.0,
            "confidence": 0.0
        }
        
        if strength > 50:
            if sentiment > 0.2:
                impact["direction"] = "up"
                impact["magnitude_percentage"] = (strength / 100) * 5.0  # Max 5% move
                impact["confidence"] = 0.7 + (strength/200)
            elif sentiment < -0.2:
                impact["direction"] = "down"
                impact["magnitude_percentage"] = (strength / 100) * 3.0  # Max 3% move
                impact["confidence"] = 0.6 + (strength/200)
        
        return impact

# Global forecaster
forecaster = NarrativeForecaster()
