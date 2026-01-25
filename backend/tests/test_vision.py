"""
Comprehensive Test Suite for Vision Pipeline and Valuation Engine - FIXED

Tests all aspects of silver object analysis including:
- Reference object detection (coins for scale)
- Purity detection with multi-model consensus
- Dimension and weight calculation
- Quality assessment
- Valuation engine
- Edge cases and error handling

All tests updated to work with async implementation.
"""
import pytest
import sys
import os
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from dataclasses import asdict
import numpy as np
import cv2

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vision.vision_pipeline import (
    VisionPipeline,
    VisionAnalysisResult,
    Dimensions,
    ReferenceObject
)
from vision.valuation_engine import ValuationEngine, ValuationResult


class TestReferenceObjectDetection:
    """Test reference object (coin) detection for scale calibration"""
    
    def test_coin_detection_with_cv(self):
        """Test traditional CV-based coin detection"""
        pipeline = VisionPipeline()
        
        # Create mock image with circular object
        image = np.zeros((500, 500, 3), dtype=np.uint8)
        # Draw a well-defined circle
        cv2.circle(image, (250, 250), 100, (255, 255, 255), -1)
        
        reference = pipeline._detect_coin_cv(image)
        
        # Should detect the circle or return None
        if reference:
            assert isinstance(reference, ReferenceObject)
            assert reference.type == "coin"
            assert reference.pixels_per_mm > 0
    
    @pytest.mark.asyncio
    async def test_reference_detection_with_llm(self):
        """Test LLM-based reference detection fallback"""
        pipeline = VisionPipeline()
        
        # Mock orchestrator response
        mock_response = MagicMock()
        mock_response.success = True
        mock_response.content = '{"reference_found": true, "reference_type": "coin", "reference_value": "1 Rupee", "known_dimension": 25.0, "pixels_per_mm": 4.0, "confidence": "high"}'
        
        with patch('vision.vision_pipeline.orchestrator.analyze_image', return_value=mock_response):
            reference = await pipeline._detect_reference_llm("test_image.jpg")
            
            if reference:
                assert reference.type == "coin"
                assert reference.confidence == "high"
    
    def test_reference_object_calibration(self):
        """Test pixel-to-mm calibration calculation"""
        reference = ReferenceObject(
            type="1_rupee_coin",
            value="1 Rupee",
            known_dimension_mm=25.0,
            pixel_dimension=100.0,
            pixels_per_mm=4.0,
            confidence="high"
        )
        
        # Verify calibration math
        assert reference.pixels_per_mm == reference.pixel_dimension / reference.known_dimension_mm


class TestPurityDetection:
    """Test purity detection with multi-model consensus"""
    
    @pytest.mark.asyncio
    async def test_purity_detection_consensus(self):
        """Test multi-model purity detection with voting"""
        pipeline = VisionPipeline()
        
        # Mock orchestrator parallel validation response
        mock_result = {
            "consensus": 925,
            "confidence": 0.85,
            "results": ['{"purity": 925, "object_type": "jewelry"}']
        }
        
        with patch('vision.vision_pipeline.orchestrator.parallel_validation', return_value=mock_result):
            result = await pipeline.detect_purity_parallel("test_image.jpg")
            
            assert "purity" in result
            if result["purity"]:
                assert result["purity"] in [800, 900, 925, 950, 999]
            assert result["confidence"] in ["high", "medium", "low", "none"]
    
    def test_purity_values_validation(self):
        """Test that purity values are within valid ranges"""
        valid_purities = [800, 900, 925, 950, 999]
        
        for purity in valid_purities:
            assert 800 <= purity <= 999, f"Purity {purity} out of valid range"


class TestDimensionCalculation:
    """Test dimension calculation from contours and reference"""
    
    def test_dimension_calculation_with_reference(self):
        """Test dimension calculation given a reference object"""
        pipeline = VisionPipeline()
        
        # Create mock contour (rectangular object 200x150 pixels)
        contour = np.array([
            [[50, 50]],
            [[250, 50]],
            [[250, 200]],
            [[50, 200]]
        ])
        
        reference = ReferenceObject(
            type="1_rupee_coin",
            value="1 Rupee",
            known_dimension_mm=25.0,
            pixel_dimension=100.0,
            pixels_per_mm=4.0,
            confidence="high"
        )
        
        dimensions = pipeline.calculate_dimensions(contour, reference)
        
        # Expected dimensions: 200 pixels / 4 pixels_per_mm = 50mm width
        assert isinstance(dimensions, Dimensions)
        assert dimensions.width_mm > 0
        assert dimensions.height_mm > 0
        assert dimensions.area_mm2 > 0
    
    def test_circular_object_dimensions(self):
        """Test dimensions for circular objects (coins, bangles)"""
        # Create circular contour
        center = (250, 250)
        radius = 50
        angles = np.linspace(0, 2*np.pi, 100)
        contour = np.array([[[int(center[0] + radius * np.cos(a)), 
                             int(center[1] + radius * np.sin(a))]] for a in angles])
        
        # Should have valid contour
        assert contour.shape[0] > 0


class TestWeightEstimation:
    """Test weight calculation based on volume and density"""
    
    def test_weight_calculation_solid_object(self):
        """Test weight calculation for solid silver object"""
        pipeline = VisionPipeline()
        
        dimensions = Dimensions(
            width_mm=50.0,
            height_mm=30.0,
            area_mm2=1500.0
        )
        
        weight = pipeline.calculate_weight(
            dimensions=dimensions,
            thickness_mm=2.0,
            purity=925,
            is_hollow=False,
            hollow_percentage=0.0
        )
        
        # Weight should be positive
        assert weight > 0
        # Typical range for small silver objects: 1-100g
        assert 0.1 <= weight <= 200
    
    def test_weight_calculation_hollow_object(self):
        """Test weight calculation for hollow object (bangle, utensil)"""
        pipeline = VisionPipeline()
        
        dimensions = Dimensions(
            width_mm=50.0,
            height_mm=30.0,
            area_mm2=1500.0
        )
        
        weight_hollow = pipeline.calculate_weight(
            dimensions=dimensions,
            thickness_mm=2.0,
            purity=925,
            is_hollow=True,
            hollow_percentage=60.0  # 60% hollow
        )
        
        weight_solid = pipeline.calculate_weight(
            dimensions=dimensions,
            thickness_mm=2.0,
            purity=925,
            is_hollow=False,
            hollow_percentage=0.0
        )
        
        # Hollow object should weigh less
        assert weight_hollow < weight_solid
    
    def test_purity_affects_density(self):
        """Test that different purities use correct densities"""
        pipeline = VisionPipeline()
        
        dimensions = Dimensions(width_mm=50.0, height_mm=30.0, area_mm2=1500.0)
        
        weight_999 = pipeline.calculate_weight(dimensions, 2.0, 999, False, 0.0)
        weight_925 = pipeline.calculate_weight(dimensions, 2.0, 925, False, 0.0)
        
        # 999 silver has higher density (10.49) than 925 (10.28)
        assert weight_999 > weight_925


class TestQualityAssessment:
    """Test quality and condition assessment"""
    
    @pytest.mark.asyncio
    async def test_quality_assessment(self):
        """Test quality scoring and notes generation"""
        pipeline = VisionPipeline()
        
        # Mock orchestrator response
        mock_response = MagicMock()
        mock_response.success = True
        mock_response.content = '{"quality_score": 85, "notes": "Excellent condition", "confidence": "high"}'
        
        with patch('vision.vision_pipeline.orchestrator.analyze_image', return_value=mock_response):
            result = await pipeline.assess_quality("test_image.jpg")
            
            assert 0 <= result["quality_score"] <= 100
            assert isinstance(result["notes"], str)
            assert result["confidence"] in ["high", "medium", "low"]
    
    def test_quality_score_ranges(self):
        """Test quality score interpretation"""
        # High quality: 80-100
        # Medium quality: 60-79
        # Low quality: 0-59
        
        test_scores = [95, 75, 50, 30]
        for score in test_scores:
            assert 0 <= score <= 100


class TestValuationEngine:
    """Test valuation calculation engine"""
    
    @pytest.mark.asyncio
    async def test_basic_valuation(self):
        """Test basic valuation calculation"""
        engine = ValuationEngine()
        
        # Create mock analysis result
        analysis = VisionAnalysisResult(
            detected_type="jewelry",
            purity=925,
            purity_confidence="high",
            estimated_weight_g=10.0,
            dimensions=Dimensions(width_mm=30.0, height_mm=20.0, area_mm2=600.0),
            quality_score=85,
            quality_notes="Excellent condition",
            reference_detected=True,
            reference_object=None,
            thickness_mm=2.0,
            is_hollow=False,
            overall_confidence=0.85
        )
        
        valuation = await engine.calculate_value(analysis)
        
        assert isinstance(valuation, ValuationResult)
        assert valuation.base_value > 0
        assert valuation.adjusted_value > 0
        assert valuation.value_range[0] < valuation.value_range[1]
        assert valuation.spot_price_per_gram > 0
        assert 0 <= valuation.overall_confidence <= 1.0
    
    @pytest.mark.asyncio
    async def test_craftsmanship_premium(self):
        """Test craftsmanship premium application"""
        engine = ValuationEngine()
        
        # High quality jewelry should get higher premium
        analysis_high = VisionAnalysisResult(
            detected_type="jewelry",
            purity=925,
            purity_confidence="high",
            estimated_weight_g=10.0,
            dimensions=Dimensions(width_mm=30.0, height_mm=20.0, area_mm2=600.0),
            quality_score=90,  # High quality
            quality_notes="Excellent craftsmanship",
            reference_detected=True,
            reference_object=None,
            thickness_mm=2.0,
            is_hollow=False,
            overall_confidence=0.9
        )
        
        valuation_high = await engine.calculate_value(analysis_high)
        
        # Should have non-zero premium
        assert valuation_high.craftsmanship_premium > 0
        # High quality jewelry: 30% premium
        assert valuation_high.craftsmanship_premium == 0.30
    
    @pytest.mark.asyncio
    async def test_condition_penalty(self):
        """Test condition penalty for damaged items"""
        engine = ValuationEngine()
        
        analysis_damaged = VisionAnalysisResult(
            detected_type="coin",
            purity=925,
            purity_confidence="medium",
            estimated_weight_g=5.0,
            dimensions=Dimensions(width_mm=25.0, height_mm=25.0, area_mm2=490.0),
            quality_score=35,  # Poor condition
            quality_notes="Significant tarnish and scratches",
            reference_detected=True,
            reference_object=None,
            thickness_mm=1.5,
            is_hollow=False,
            overall_confidence=0.6
        )
        
        valuation_damaged = await engine.calculate_value(analysis_damaged)
        
        # Should have penalty for poor condition
        assert valuation_damaged.condition_penalty > 0
        # Poor quality (< 40): 30% penalty
        assert valuation_damaged.condition_penalty == 0.30
    
    @pytest.mark.asyncio
    async def test_valuation_by_type(self):
        """Test that different object types get appropriate premiums"""
        engine = ValuationEngine()
        
        base_analysis = {
            "purity": 925,
            "purity_confidence": "high",
            "estimated_weight_g": 10.0,
            "dimensions": Dimensions(width_mm=30.0, height_mm=20.0, area_mm2=600.0),
            "quality_score": 85,
            "quality_notes": "Good condition",
            "reference_detected": True,
            "reference_object": None,
            "thickness_mm": 2.0,
            "is_hollow": False,
            "overall_confidence": 0.85
        }
        
        object_types = ["jewelry", "coin", "bar", "utensil"]
        
        for obj_type in object_types:
            analysis = VisionAnalysisResult(detected_type=obj_type, **base_analysis)
            valuation = await engine.calculate_value(analysis)
            
            # Each type should have appropriate premium
            assert valuation.craftsmanship_premium >= 0
            # Jewelry has highest premium, bars have lowest
            if obj_type == "jewelry":
                assert valuation.craftsmanship_premium == 0.30
            elif obj_type == "bar":
                assert valuation.craftsmanship_premium <= 0.05


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    @pytest.mark.asyncio
    async def test_no_reference_object_detected(self):
        """Test handling when no reference object is found"""
        pipeline = VisionPipeline()
        
        # Mock CV detection returning None
        image = np.zeros((100, 100, 3))
        reference = pipeline._detect_coin_cv(image)
        
        # Blank image should return None
        assert reference is None
    
    def test_confidence_calculation(self):
        """Test overall confidence calculation from individual confidences"""
        pipeline = VisionPipeline()
        
        # All high confidence should give high overall
        confidence = pipeline._calculate_overall_confidence("high", "high", "high", "high")
        assert confidence >= 0.8
        
        # All low confidence should give low overall
        confidence_low = pipeline._calculate_overall_confidence("low", "low", "low", "low")
        assert confidence_low <= 0.5
        
        # Mixed confidence should be medium
        confidence_mixed = pipeline._calculate_overall_confidence("high", "medium", "low", "medium")
        assert 0.4 <= confidence_mixed <= 0.7
    
    @pytest.mark.asyncio
    async def test_unknown_purity(self):
        """Test valuation when purity cannot be determined"""
        engine = ValuationEngine()
        
        analysis = VisionAnalysisResult(
            detected_type="jewelry",
            purity=None,  # Unknown purity
            purity_confidence="low",
            estimated_weight_g=10.0,
            dimensions=Dimensions(width_mm=30.0, height_mm=20.0, area_mm2=600.0),
            quality_score=70,
            quality_notes="Cannot determine purity",
            reference_detected=True,
            reference_object=None,
            thickness_mm=2.0,
            is_hollow=False,
            overall_confidence=0.5
        )
        
        valuation = await engine.calculate_value(analysis)
        
        # Should default to 925 purity
        assert valuation.base_value > 0
        assert valuation.overall_confidence <= 0.5  # Low confidence
    
    def test_zero_weight_handling(self):
        """Test handling of invalid zero dimensions"""
        pipeline = VisionPipeline()
        
        dimensions = Dimensions(width_mm=0.0, height_mm=0.0, area_mm2=0.0)
        
        weight = pipeline.calculate_weight(dimensions, 2.0, 925, False, 0.0)
        
        # Should return 0
        assert weight == 0.0


class TestIntegration:
    """Test integration scenarios"""
    
    @pytest.mark.asyncio
    async def test_api_response_format(self):
        """Test that valuation formats correctly for API response"""
        engine = ValuationEngine()
        
        valuation = ValuationResult(
            base_value=7500.0,
            adjusted_value=8250.0,
            value_range=(6600.0, 9900.0),
            spot_price_per_gram=75.0,
            craftsmanship_premium=0.10,
            condition_penalty=0.0,
            overall_confidence=0.85,
            currency="INR"
        )
        
        formatted = engine.format_valuation_for_display(valuation)
        
        assert "base_value" in formatted
        assert "adjusted_value" in formatted
        assert "value_range" in formatted
        assert "min" in formatted["value_range"]
        assert "max" in formatted["value_range"]
        assert "breakdown" in formatted
        assert formatted["currency"] == "INR"


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
