"""
Test Vision Pipeline with User-Provided Real Images

Analyzes silver chain images and generates a detailed report.
"""
import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from vision.vision_pipeline import VisionPipeline
from vision.valuation_engine import ValuationEngine


async def analyze_silver_chain():
    """Analyze the user's silver chain images"""
    
    print("=" * 70)
    print("SILVER CHAIN ANALYSIS - Vision Pipeline Test")
    print("=" * 70)
    print()
    
    pipeline = VisionPipeline()
    valuation_engine = ValuationEngine()
    
    # Test bracelet with ruler images
    test_images = [
        "data/test_images/bracelet_ruler_1.jpg",
        "data/test_images/bracelet_ruler_2.jpg"
    ]
    
    for idx, image_path in enumerate(test_images, 1):
        print(f"\n📸 ANALYZING IMAGE {idx}: {image_path}")
        print("-" * 70)
        
        try:
            # Run full analysis pipeline
            result = await pipeline.analyze_image(image_path)
            
            print(f"\n✅ Analysis Complete!")
            print(f"\n🔍 DETECTION RESULTS:")
            print(f"   Object Type:        {result.detected_type}")
            print(f"   Purity:             {result.purity if result.purity else 'Unknown'} ({result.purity_confidence} confidence)")
            print(f"   Reference Detected: {'Yes' if result.reference_detected else 'No'}")
            
            if result.reference_object:
                print(f"\n📏 REFERENCE OBJECT:")
                print(f"   Type:               {result.reference_object.type}")
                print(f"   Value:              {result.reference_object.value}")
                print(f"   Calibration:        {result.reference_object.pixels_per_mm:.2f} pixels/mm")
                print(f"   Confidence:         {result.reference_object.confidence}")
            
            print(f"\n📐 DIMENSIONS:")
            print(f"   Width:              {result.dimensions.width_mm:.1f} mm")
            print(f"   Height:             {result.dimensions.height_mm:.1f} mm")
            print(f"   Area:               {result.dimensions.area_mm2:.1f} mm²")
            print(f"   Thickness:          {result.thickness_mm:.1f} mm")
            print(f"   Is Hollow:          {'Yes' if result.is_hollow else 'No'}")
            
            print(f"\n⚖️  WEIGHT:")
            print(f"   Estimated Weight:   {result.estimated_weight_g:.2f} grams")
            
            print(f"\n🎨 QUALITY:")
            print(f"   Quality Score:      {result.quality_score}/100")
            print(f"   Notes:              {result.quality_notes}")
            
            print(f"\n🎯 OVERALL CONFIDENCE: {result.overall_confidence * 100:.0f}%")
            
            # Calculate valuation
            print(f"\n💰 VALUATION:")
            valuation = await valuation_engine.calculate_value(result)
            
            print(f"   Spot Price:         ₹{valuation.spot_price_per_gram:.2f}/gram")
            print(f"   Base Value:         ₹{valuation.base_value:,.2f}")
            print(f"   Craftsmanship:      +{valuation.craftsmanship_premium * 100:.0f}%")
            print(f"   Condition Penalty:  -{valuation.condition_penalty * 100:.0f}%")
            print(f"   Adjusted Value:     ₹{valuation.adjusted_value:,.2f}")
            print(f"   Value Range:        ₹{valuation.value_range[0]:,.2f} - ₹{valuation.value_range[1]:,.2f}")
            
            print(f"\n⚠️  MEASUREMENT ISSUES:")
            issues = pipeline.get_measurement_issues(result)
            if issues:
                for issue in issues:
                    print(f"   • {issue}")
            else:
                print(f"   None detected")
            
        except Exception as e:
            print(f"\n❌ Analysis Failed: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 70)
    print("ANALYSIS COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(analyze_silver_chain())
