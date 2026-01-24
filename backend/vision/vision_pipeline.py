"""
Computer Vision Pipeline for Silver Object Analysis
Combines traditional CV (OpenCV) with Vision LLM analysis
"""
import cv2
import numpy as np
import json
import math
from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Tuple
from pathlib import Path
import asyncio

from .prompts import (
    PURITY_DETECTION_PROMPT,
    QUALITY_ASSESSMENT_PROMPT,
    REFERENCE_DETECTION_PROMPT,
    THICKNESS_ESTIMATION_PROMPT,
    OBJECT_SEGMENTATION_PROMPT
)

# Import orchestrator from parent module
import sys
sys.path.append(str(Path(__file__).parent.parent))
from orchestrator import orchestrator


@dataclass
class ReferenceObject:
    """Detected reference object for scale calibration"""
    type: str  # "coin", "ruler", "a4_paper", "card"
    value: str  # e.g., "5 rupee coin", "standard ruler"
    known_dimension_mm: float  # Real-world size in mm
    pixel_dimension: float  # Measured size in pixels
    pixels_per_mm: float  # Calibration ratio
    confidence: str  # "high", "medium", "low"


@dataclass
class Dimensions:
    """Physical dimensions of object"""
    width_mm: float
    height_mm: float
    area_mm2: float
    diameter_mm: Optional[float] = None  # For circular objects
    perimeter_mm: Optional[float] = None


@dataclass
class VisionAnalysisResult:
    """Complete vision analysis result"""
    detected_type: str  # "jewelry", "coin", "bar", "utensil"
    purity: Optional[int]  # 925, 950, 999, etc.
    purity_confidence: str  # "high", "medium", "low", "none"
    estimated_weight_g: float
    dimensions: Dimensions
    quality_score: int  # 0-100
    quality_notes: str
    reference_detected: bool
    reference_object: Optional[ReferenceObject]
    thickness_mm: float
    is_hollow: bool
    overall_confidence: float  # 0.0-1.0


class VisionPipeline:
    """
    End-to-end vision pipeline for silver object analysis
    """
    
    # Known reference object dimensions (in mm)
    REFERENCE_DIMENSIONS = {
        "1_rupee_coin": 25.0,
        "2_rupee_coin": 27.0,
        "5_rupee_coin": 23.0,
        "10_rupee_coin": 27.0,
        "a4_paper_width": 210.0,
        "a4_paper_height": 297.0,
        "credit_card_width": 85.6,
        "credit_card_height": 53.98,
        "us_quarter": 24.26,
        "us_penny": 19.05,
    }
    
    # Silver density (g/cm³)
    SILVER_DENSITY = {
        999: 10.49,  # Pure silver
        950: 10.41,  # Britannia silver
        925: 10.28,  # Sterling (92.5% Ag + 7.5% Cu)
    }
    
    def __init__(self):
        """Initialize vision pipeline"""
        pass
    
    async def analyze_image(self, image_path: str) -> VisionAnalysisResult:
        """
        Complete analysis pipeline
        
        Args:
            image_path: Path to uploaded image file
            
        Returns:
            VisionAnalysisResult with all analysis data
        """
        # Load image
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Failed to load image: {image_path}")
        
        # Step 1: Detect reference object for scale
        reference = await self.detect_reference_object(image_path, image)
        
        if not reference:
            raise ValueError(
                "No reference object detected. Please include a coin, ruler, or A4 paper in the image."
            )
        
        # Step 2: Segment silver object (traditional CV + LLM guidance)
        contour, mask = await self.segment_silver_object(image_path, image)
        
        # Step 3: Measure dimensions using reference scale
        dimensions = self.calculate_dimensions(contour, reference)
        
        # Step 4: Detect purity with multi-model consensus
        purity_result = await self.detect_purity_parallel(image_path)
        
        # Step 5: Estimate thickness (critical for weight calculation)
        thickness_result = await self.estimate_thickness(image_path, dimensions)
        
        # Step 6: Calculate weight
        weight = self.calculate_weight(
            dimensions=dimensions,
            thickness_mm=thickness_result["estimated_thickness_mm"],
            purity=purity_result.get("purity", 925),
            is_hollow=thickness_result.get("is_hollow", False),
            hollow_percentage=thickness_result.get("hollow_percentage", 0)
        )
        
        # Step 7: Assess quality
        quality_result = await self.assess_quality(image_path)
        
        # Step 8: Calculate overall confidence
        overall_confidence = self._calculate_overall_confidence(
            reference_confidence=reference.confidence,
            purity_confidence=purity_result.get("confidence", "low"),
            thickness_confidence=thickness_result.get("confidence", "low"),
            quality_confidence=quality_result.get("confidence", "medium")
        )
        
        return VisionAnalysisResult(
            detected_type=purity_result.get("object_type", "unknown"),
            purity=purity_result.get("purity"),
            purity_confidence=purity_result.get("confidence", "none"),
            estimated_weight_g=weight,
            dimensions=dimensions,
            quality_score=quality_result.get("quality_score", 50),
            quality_notes=quality_result.get("notes", ""),
            reference_detected=True,
            reference_object=reference,
            thickness_mm=thickness_result["estimated_thickness_mm"],
            is_hollow=thickness_result.get("is_hollow", False),
            overall_confidence=overall_confidence
        )
    
    async def detect_reference_object(
        self, 
        image_path: str, 
        image: np.ndarray
    ) -> Optional[ReferenceObject]:
        """
        Detect reference object for scale calibration
        
        Strategy: Try traditional CV first (faster), fallback to LLM
        """
        # Try CV-based coin detection (circles)
        reference = self._detect_coin_cv(image)
        if reference:
            return reference
        
        # Fallback: Use vision LLM
        reference = await self._detect_reference_llm(image_path)
        return reference
    
    def _detect_coin_cv(self, image: np.ndarray) -> Optional[ReferenceObject]:
        """Traditional CV circle detection for coins"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (9, 9), 2)
        
        # Detect circles using Hough Transform
        circles = cv2.HoughCircles(
            blurred,
            cv2.HOUGH_GRADIENT,
            dp=1,
            minDist=50,
            param1=50,
            param2=30,
            minRadius=80,  # Typical coin at reasonable distance
            maxRadius=250
        )
        
        if circles is None:
            return None
        
        # Take the largest circle (likely the reference coin)
        circles = np.round(circles[0, :]).astype("int")
        largest_circle = max(circles, key=lambda c: c[2])  # Max radius
        
        x, y, radius = largest_circle
        pixel_diameter = radius * 2
        
        # Assume 5 rupee coin (most common) - 23mm diameter
        # In production, use LLM to confirm coin type
        known_diameter_mm = self.REFERENCE_DIMENSIONS["5_rupee_coin"]
        pixels_per_mm = pixel_diameter / known_diameter_mm
        
        return ReferenceObject(
            type="coin",
            value="5_rupee_coin (assumed)",
            known_dimension_mm=known_diameter_mm,
            pixel_dimension=pixel_diameter,
            pixels_per_mm=pixels_per_mm,
            confidence="medium"  # Medium because we assumed coin type
        )
    
    async def _detect_reference_llm(self, image_path: str) -> Optional[ReferenceObject]:
        """Use vision LLM to detect and identify reference object"""
        try:
            response = await orchestrator.analyze_image(
                image_path=image_path,
                prompt=REFERENCE_DETECTION_PROMPT
            )
            
            if not response.success:
                return None
            
            # Parse JSON response
            result = json.loads(response.content)
            
            if not result.get("reference_found", False):
                return None
            
            # Calculate pixels per mm (LLM should provide this or we calculate)
            pixels_per_mm = result.get("pixels_per_mm", 15.0)  # Default fallback
            
            return ReferenceObject(
                type=result["reference_type"],
                value=result["reference_value"],
                known_dimension_mm=result["known_dimension"],
                pixel_dimension=pixels_per_mm * result["known_dimension"],
                pixels_per_mm=pixels_per_mm,
                confidence=result.get("confidence", "medium")
            )
        
        except Exception as e:
            print(f"LLM reference detection failed: {e}")
            return None
    
    async def segment_silver_object(
        self, 
        image_path: str, 
        image: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Segment silver object from background
        
        Returns:
            (contour, mask) - largest contour and binary mask
        """
        # Traditional CV approach
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # Silver color range (gray/metallic)
        lower_silver = np.array([0, 0, 100])
        upper_silver = np.array([180, 50, 255])
        
        # Create mask
        mask = cv2.inRange(hsv, lower_silver, upper_silver)
        
        # Morphological operations to clean up
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        
        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            raise ValueError("No silver object detected in image")
        
        # Get largest contour (main silver object)
        largest_contour = max(contours, key=cv2.contourArea)
        
        return largest_contour, mask
    
    def calculate_dimensions(
        self, 
        contour: np.ndarray, 
        reference: ReferenceObject
    ) -> Dimensions:
        """Calculate real-world dimensions using reference scale"""
        # Bounding rectangle
        x, y, width_px, height_px = cv2.boundingRect(contour)
        
        # Convert to millimeters
        width_mm = width_px / reference.pixels_per_mm
        height_mm = height_px / reference.pixels_per_mm
        
        # Area
        area_px = cv2.contourArea(contour)
        area_mm2 = area_px / (reference.pixels_per_mm ** 2)
        
        # For circular objects, calculate diameter
        (cx, cy), radius_px = cv2.minEnclosingCircle(contour)
        diameter_mm = (radius_px * 2) / reference.pixels_per_mm
        
        # Perimeter
        perimeter_px = cv2.arcLength(contour, True)
        perimeter_mm = perimeter_px / reference.pixels_per_mm
        
        return Dimensions(
            width_mm=width_mm,
            height_mm=height_mm,
            area_mm2=area_mm2,
            diameter_mm=diameter_mm,
            perimeter_mm=perimeter_mm
        )
    
    async def detect_purity_parallel(self, image_path: str) -> Dict[str, Any]:
        """
        Multi-model purity detection with consensus voting
        Critical for valuation accuracy
        """
        try:
            # Use orchestrator's parallel validation
            result = await orchestrator.parallel_validation(
                image_path=image_path,
                prompt=PURITY_DETECTION_PROMPT
            )
            
            # Parse consensus result
            if result.get("consensus"):
                purity = int(result["consensus"])
            else:
                # Parse from first valid result
                for res in result.get("results", []):
                    try:
                        parsed = json.loads(res)
                        if parsed.get("purity"):
                            purity = parsed["purity"]
                            break
                    except:
                        continue
                else:
                    purity = None
            
            # Extract additional info from first result
            try:
                first_result = json.loads(result["results"][0]) if result.get("results") else {}
            except:
                first_result = {}
            
            return {
                "purity": purity,
                "confidence": "high" if result.get("confidence", 0) > 0.7 else "medium",
                "object_type": first_result.get("object_type", "unknown"),
                "hallmark_location": first_result.get("hallmark_location", ""),
                "other_marks": first_result.get("other_marks", [])
            }
        
        except Exception as e:
            print(f"Purity detection failed: {e}")
            return {
                "purity": None,
                "confidence": "none",
                "object_type": "unknown"
            }
    
    async def estimate_thickness(
        self, 
        image_path: str, 
        dimensions: Dimensions
    ) -> Dict[str, Any]:
        """Estimate thickness using vision LLM"""
        try:
            prompt = THICKNESS_ESTIMATION_PROMPT.format(
                width_mm=dimensions.width_mm,
                height_mm=dimensions.height_mm
            )
            
            response = await orchestrator.analyze_image(image_path, prompt)
            
            if response.success:
                return json.loads(response.content)
            else:
                # Default fallback based on typical sizes
                return {
                    "estimated_thickness_mm": 2.5,
                    "is_hollow": False,
                    "hollow_percentage": 0,
                    "confidence": "low"
                }
        
        except Exception as e:
            print(f"Thickness estimation failed: {e}")
            return {
                "estimated_thickness_mm": 2.5,
                "is_hollow": False,
                "hollow_percentage": 0,
                "confidence": "low"
            }
    
    async def assess_quality(self, image_path: str) -> Dict[str, Any]:
        """Assess object quality and condition"""
        try:
            response = await orchestrator.analyze_image(
                image_path=image_path,
                prompt=QUALITY_ASSESSMENT_PROMPT
            )
            
            if response.success:
                return json.loads(response.content)
            else:
                return {
                    "quality_score": 50,
                    "notes": "Unable to assess quality",
                    "confidence": "low"
                }
        
        except Exception as e:
            print(f"Quality assessment failed: {e}")
            return {
                "quality_score": 50,
                "notes": "Assessment failed",
                "confidence": "low"
            }
    
    def calculate_weight(
        self,
        dimensions: Dimensions,
        thickness_mm: float,
        purity: int,
        is_hollow: bool,
        hollow_percentage: float
    ) -> float:
        """
        Calculate weight based on volume and density
        
        Note: This is an estimation with ±15-25% error due to:
        - Thickness estimation uncertainty
        - Complex shapes not captured in 2D
        - Hollow sections not visible
        """
        # Get silver density based on purity
        if purity in self.SILVER_DENSITY:
            density_g_cm3 = self.SILVER_DENSITY[purity]
        else:
            # Interpolate or default to 925
            density_g_cm3 = self.SILVER_DENSITY[925]
        
        # Simplified volume calculation (rectangular approximation)
        # In reality, jewelry is complex 3D shapes
        volume_mm3 = dimensions.area_mm2 * thickness_mm
        
        # Adjust for hollow sections
        if is_hollow:
            volume_mm3 *= (1 - hollow_percentage / 100)
        
        # Convert to cm³
        volume_cm3 = volume_mm3 / 1000
        
        # Calculate weight
        weight_g = volume_cm3 * density_g_cm3
        
        return round(weight_g, 2)
    
    def _calculate_overall_confidence(
        self,
        reference_confidence: str,
        purity_confidence: str,
        thickness_confidence: str,
        quality_confidence: str
    ) -> float:
        """Calculate overall confidence score (0.0-1.0)"""
        confidence_map = {
            "high": 1.0,
            "medium": 0.7,
            "low": 0.4,
            "none": 0.0
        }
        
        # Weighted average (reference and purity are most critical)
        weights = {
            "reference": 0.35,
            "purity": 0.35,
            "thickness": 0.20,
            "quality": 0.10
        }
        
        score = (
            weights["reference"] * confidence_map.get(reference_confidence, 0.5) +
            weights["purity"] * confidence_map.get(purity_confidence, 0.5) +
            weights["thickness"] * confidence_map.get(thickness_confidence, 0.5) +
            weights["quality"] * confidence_map.get(quality_confidence, 0.5)
        )
        
        return round(score, 2)
