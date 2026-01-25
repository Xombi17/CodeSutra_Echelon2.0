"""
Enhanced Vision Pipeline
Adds uncertainty quantification on top of VisionPipeline
"""

from typing import Dict, Any
from pathlib import Path
import sys

# Import base pipeline
sys.path.append(str(Path(__file__).parent))
from vision_pipeline import VisionPipeline, VisionAnalysisResult
from valuation_engine import ValuationEngine, ValuationResult
from vision_uncertainty_analyzer import uncertainty_analyzer


class EnhancedVisionPipeline(VisionPipeline):
    """
    Wrapper pipeline that adds uncertainty + valuation ranges
    """

    async def analyze_image_with_uncertainty(
        self,
        image_path: str
    ) -> Dict[str, Any]:

        try:
            analysis = await self.analyze_image(image_path)
        except ValueError as e:
            return {
                "success": False,
                "error": str(e),
                "recommendation": (
                    "Include a coin, ruler, or A4 paper in the photo."
                )
            }

        analysis_dict = self._analysis_to_dict(analysis)

        # Detect known measurement issues
        detected_issues = self.get_measurement_issues(analysis)
        analysis_dict["detected_issues"] = detected_issues
        analysis_dict["purity_confidence"] = analysis.purity_confidence

        # Uncertainty report
        uncertainty_report = (
            uncertainty_analyzer.generate_comprehensive_report(
                analysis_dict
            )
        )

        # Valuation
        valuation_engine = ValuationEngine()
        valuation = await valuation_engine.calculate_value(analysis)

        enhanced_valuation = self._enhance_valuation(
            valuation,
            uncertainty_report
        )

        return {
            "success": True,
            "measurements": {
                "object_type": analysis.detected_type,
                "purity": analysis.purity,
                "weight_grams": analysis.estimated_weight_g,
                "dimensions": {
                    "width_mm": round(analysis.dimensions.width_mm, 2),
                    "height_mm": round(analysis.dimensions.height_mm, 2),
                    "thickness_mm": round(analysis.thickness_mm, 2),
                    "area_mm2": round(analysis.dimensions.area_mm2, 2)
                },
                "quality_score": analysis.quality_score
            },
            "valuation": enhanced_valuation,
            "uncertainty_analysis": uncertainty_report["uncertainty_analysis"],
            "reference_object": {
                "type": (
                    analysis.reference_object.type
                    if analysis.reference_object else "none"
                ),
                "confidence": (
                    analysis.reference_object.confidence
                    if analysis.reference_object else "none"
                )
            },
            "quality_notes": analysis.quality_notes,
            "overall_confidence": analysis.overall_confidence
        }

    # ---------------- helpers ----------------

    def _analysis_to_dict(
        self,
        analysis: VisionAnalysisResult
    ) -> Dict[str, Any]:
        return {
            "detected_type": analysis.detected_type,
            "purity": analysis.purity,
            "estimated_weight": analysis.estimated_weight_g,
            "estimated_dimensions": {
                "width": analysis.dimensions.width_mm,
                "height": analysis.dimensions.height_mm,
                "thickness": analysis.thickness_mm
            },
            "reference_object": (
                analysis.reference_object.type
                if analysis.reference_object else None
            )
        }

    def _enhance_valuation(
        self,
        valuation: ValuationResult,
        uncertainty_report: Dict[str, Any]
    ) -> Dict[str, Any]:

        weight_uncertainty = (
            uncertainty_report["uncertainty_analysis"]
            .get("measurements", {})
            .get("weight", {})
        )

        if weight_uncertainty:
            w_min = weight_uncertainty["value_range"]["min"]
            w_max = weight_uncertainty["value_range"]["max"]
            price = valuation.spot_price_per_gram

            min_value = w_min * price * 0.75
            max_value = w_max * price * 1.05
        else:
            min_value, max_value = valuation.value_range

        return {
            "base_value": round(valuation.base_value, 2),
            "adjusted_value": round(valuation.adjusted_value, 2),
            "value_range": {
                "min": round(min_value, 2),
                "max": round(max_value, 2),
                "note": (
                    "Includes weight (±15–25%), purity (±25%), "
                    "and market price uncertainty"
                )
            },
            "currency": valuation.currency,
            "spot_price_per_gram": round(
                valuation.spot_price_per_gram, 2
            ),
            "confidence": valuation.overall_confidence,
            "timestamp": valuation.calculation_timestamp
        }


# -------- API helper --------

async def scan_silver_object(image_path: str) -> Dict[str, Any]:
    pipeline = EnhancedVisionPipeline()
    return await pipeline.analyze_image_with_uncertainty(image_path)
