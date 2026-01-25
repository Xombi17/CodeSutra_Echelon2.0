"""
Vision Uncertainty Analyzer
Quantifies uncertainty for all CV + LLM derived measurements
"""

from typing import Dict, Any, List
import math
from datetime import datetime


class VisionUncertaintyAnalyzer:
    """
    Central uncertainty quantification engine
    """

    def generate_comprehensive_report(
        self,
        analysis_dict: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate full uncertainty analysis report
        """

        measurements = {}
        critical_warnings = []

        # --- Weight uncertainty ---
        weight = analysis_dict.get("estimated_weight")
        detected_type = analysis_dict.get("detected_type")

        if weight:
            if detected_type in ["chain", "bracelet", "jewelry", "ring"]:
                error_pct = 0.25
                confidence = "low"
            else:
                error_pct = 0.15
                confidence = "medium"

            measurements["weight"] = {
                "value": weight,
                "error_margin": f"±{int(error_pct * 100)}%",
                "confidence_level": confidence,
                "value_range": {
                    "min": round(weight * (1 - error_pct), 2),
                    "max": round(weight * (1 + error_pct), 2),
                }
            }

        # --- Purity uncertainty ---
        purity = analysis_dict.get("purity")
        purity_confidence = analysis_dict.get("purity_confidence", "none")

        if purity:
            if purity_confidence == "high":
                error = "±5%"
                confidence = "high"
            elif purity_confidence == "medium":
                error = "±15%"
                confidence = "medium"
            else:
                error = "±25%"
                confidence = "low"
                critical_warnings.append(
                    "Purity not confirmed by hallmark"
                )

            measurements["purity"] = {
                "value": purity,
                "error_margin": error,
                "confidence_level": confidence
            }

        # --- Dimension uncertainty ---
        dims = analysis_dict.get("estimated_dimensions")
        if dims:
            measurements["dimensions"] = {
                "value": dims,
                "error_margin": "±10–15%",
                "confidence_level": "medium"
            }

        # --- Reference object uncertainty ---
        if analysis_dict.get("reference_object") is None:
            critical_warnings.append(
                "No reference object – scale accuracy reduced"
            )

        # --- Aggregate confidence ---
        confidence_score = self._calculate_overall_confidence(
            measurements,
            analysis_dict.get("detected_issues", [])
        )

        return {
            "uncertainty_analysis": {
                "overall_confidence": round(confidence_score, 2),
                "overall_confidence_level": self._confidence_label(confidence_score),
                "measurements": measurements,
                "critical_warnings": critical_warnings,
                "recommendation": self._recommendation(
                    confidence_score,
                    critical_warnings
                ),
                "generated_at": datetime.now().isoformat()
            }
        }

    # ----------------- helpers -----------------

    def _calculate_overall_confidence(
        self,
        measurements: Dict[str, Any],
        issues: List[str]
    ) -> float:
        """
        Conservative weighted confidence aggregation
        """
        weights = {
            "weight": 0.35,
            "purity": 0.35,
            "dimensions": 0.20,
            "reference": 0.10
        }

        confidence_map = {
            "high": 1.0,
            "medium": 0.7,
            "low": 0.4
        }

        score = 0.0
        used_weight = 0.0

        for key, data in measurements.items():
            if "confidence_level" in data and key in weights:
                score += (
                    confidence_map.get(data["confidence_level"], 0.5)
                    * weights[key]
                )
                used_weight += weights[key]

        if used_weight > 0:
            score /= used_weight

        # Penalize known issues
        score -= min(0.15, 0.03 * len(issues))

        return max(0.0, min(1.0, score))

    def _confidence_label(self, score: float) -> str:
        if score >= 0.8:
            return "high"
        if score >= 0.6:
            return "medium"
        return "low"

    def _recommendation(
        self,
        score: float,
        warnings: List[str]
    ) -> str:
        if score < 0.6:
            return (
                "Retake photo with clear lighting and a known reference "
                "(coin or ruler). Hallmark visibility is critical."
            )
        if warnings:
            return (
                "Results usable but not definitive. "
                "Physical verification recommended for resale."
            )
        return "Confidence acceptable for indicative valuation."


# Singleton instance (import-safe)
uncertainty_analyzer = VisionUncertaintyAnalyzer()
