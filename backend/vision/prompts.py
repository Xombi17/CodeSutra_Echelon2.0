"""
Prompt templates for vision LLM analysis
"""

PURITY_DETECTION_PROMPT = """
You are an expert silver appraiser analyzing this image of a silver object.

Your task:
1. Locate and read any purity hallmarks (stamped numbers like 925, 950, 999)
2. Identify the object type (jewelry, coin, bar, utensil)
3. Note any maker's marks or certification stamps

Important hallmark meanings:
- 925 = Sterling Silver (92.5% pure silver)
- 950 = Britannia Silver (95% pure)
- 999 = Fine Silver (99.9% pure)
- Look for microscopic engravings, often on clasps, inner bands, edges, or backs

Respond in JSON format:
{
    "purity": 925,
    "confidence": "high",
    "hallmark_location": "inner band of ring",
    "object_type": "jewelry",
    "other_marks": ["maker mark: 'XYZ'", "country mark: lion passant"],
    "readable": true
}

If no hallmark is visible, set purity to null and confidence to "none".
"""

QUALITY_ASSESSMENT_PROMPT = """
You are a professional silver quality inspector. Analyze this silver object's condition.

Assess the following factors:
1. **Tarnish**: Is there oxidation? (black/yellow discoloration indicating age/exposure)
2. **Scratches**: Surface damage? (light wear vs deep scratches)
3. **Craftsmanship**: Quality of workmanship (intricate detail vs simple construction)
4. **Completeness**: Any missing parts? (broken clasps, missing stones, damage)

Respond in JSON format:
{
    "quality_score": 75,
    "tarnish_level": "moderate",
    "scratch_severity": "light",
    "craftsmanship_rating": "good",
    "issues": ["slight tarnishing on back", "one small scratch near edge"],
    "notes": "Overall good condition, gentle cleaning would improve appearance"
}

Quality score scale:
- 90-100: Mint condition
- 75-89: Good condition, minor wear
- 60-74: Average, noticeable wear
- 40-59: Poor, significant damage
- 0-39: Very poor, extensive damage or corrosion
"""

REFERENCE_DETECTION_PROMPT = """
Identify the reference object in this image that can be used for scale calibration.

Look for common reference objects:
- **Coins** (Indian Rupee coins: 1₹ = 25mm diameter, 2₹ = 27mm, 5₹ = 23mm, 10₹ = 27mm)
- **Ruler** with visible markings (centimeters/millimeters or inches)
- **A4 paper** (210mm × 297mm standard size)
- **Credit card** (85.6mm × 53.98mm ISO standard)
- **US Quarter** (24.26mm diameter)
- **US Penny** (19.05mm diameter)

Respond in JSON format:
{
    "reference_found": true,
    "reference_type": "coin",
    "reference_value": "5 rupee coin",
    "known_dimension": 23,
    "dimension_unit": "mm",
    "confidence": "high"
}

If no reference object is detected, set reference_found to false.
"""

THICKNESS_ESTIMATION_PROMPT = """
Analyze this silver object to estimate its thickness/depth dimension.

Based on the image, look for visual clues:
1. **Edge visibility**: Can you see the side/edge of the object?
2. **Shadow depth**: Does the shadow suggest thickness?
3. **Object type context**: Typical thickness for this type of item

Common thickness ranges:
- Thin chains: 1-2mm
- Thick chains: 3-5mm  
- Rings (band width): 2-4mm
- Coins: 1.5-3mm
- Small bars: 5-10mm
- Jewelry pieces: 2-5mm

Respond in JSON:
{{
    "estimated_thickness_mm": 2.5,
    "thickness_visible": true,
    "is_hollow": false,
    "hollow_percentage": 0,
    "confidence": "medium",
    "reasoning": "Visible edge suggests approximately 2-3mm thickness"
}}

Confidence levels:
- "high": Edge clearly visible or standard known object
- "medium": Partial clues available
- "low": Guessing based on object type only
"""

OBJECT_SEGMENTATION_PROMPT = """
Identify and describe the silver object in this image for segmentation purposes.

Provide:
1. Object type and description
2. Approximate bounding box (as percentage of image dimensions)
3. Whether it's the main/largest metallic object
4. Any challenging segmentation factors

Respond in JSON:
{
    "object_type": "chain",
    "description": "Silver necklace chain with links",
    "bounding_box": {
        "x_percent": 25,
        "y_percent": 30, 
        "width_percent": 50,
        "height_percent": 40
    },
    "is_main_object": true,
    "segmentation_challenges": ["complex background", "multiple silver items"],
    "confidence": "high"
}
"""
