def outfit_weather_check(outfit, temp, rain):
    outfit = outfit.lower()

    #  EXTREME COLD
    if temp <= 5:
        if outfit not in ["jacket", "coat", "sweater", "hoodie"]:
            return "❌ Extreme cold – thermal wear and heavy jacket required"
        return "✅ Suitable for extreme cold"

    #  COLD
    if 6 <= temp <= 12:
        if outfit in ["t-shirt", "dress", "kurti", "shirt"]:
            return "❌ Cold weather – add jacket or sweater"
        return "✅ Suitable for cold weather"

    #  COOL
    if 13 <= temp <= 18:
        if outfit in ["shorts", "sandals"]:
            return "❌ Cool weather – avoid open footwear"
        return "✅ Suitable for cool weather"

    #  MILD
    if 19 <= temp <= 24:
        if rain >= 10 and outfit in ["sandals"]:
            return "❌ Rainy – avoid sandals"
        return "✅ Comfortable weather for this outfit"

    #  WARM
    if 25 <= temp <= 30:
        if outfit in ["jacket", "coat", "sweater"]:
            return "❌ Too warm – avoid heavy clothing"
        return "✅ Suitable for warm weather"

    #  HOT
    if 31 <= temp <= 36:
        if outfit not in ["t-shirt", "cotton shirt", "dress"]:
            return "❌ Hot weather – wear light cotton clothes"
        return "✅ Suitable for hot weather"

    #  EXTREME HOT
    if temp >= 37:
        if outfit in ["jeans", "jacket", "coat"]:
            return "❌ Extreme heat – wear loose cotton clothes"
        return "✅ Suitable but stay hydrated"

    return "⚠ Weather condition unclear"
def combine_verdicts(outfit_verdict, material_verdict):
    """
    Combines outfit type verdict and material verdict into a final comfort verdict.
    
    Logic: If EITHER verdict is bad, final verdict should warn.
    - ❌ + ❌ → ❌ Both unsuitable
    - ❌ + ⚠  → ❌ Outfit unsuitable
    - ❌ + ✅ → ❌ Outfit unsuitable
    - ⚠  + ❌ → ❌ Material unsuitable
    - ⚠  + ⚠  → ⚠ Both need attention
    - ⚠  + ✅ → ⚠ Check outfit
    - ✅ + ❌ → ❌ Material unsuitable
    - ✅ + ⚠  → ⚠ Check material
    - ✅ + ✅ → ✅ Excellent choice
    """
    
    # Extract emoji/status from verdicts
    outfit_status = "✅" if "✅" in outfit_verdict else ("❌" if "❌" in outfit_verdict else "⚠")
    material_status = "✅" if "✅" in material_verdict else ("❌" if "❌" in material_verdict else "⚠")
    
    # Priority: ❌ > ⚠ > ✅
    # If either is ❌, final is ❌
    if outfit_status == "❌" or material_status == "❌":
        reasons = []
        if outfit_status == "❌":
            reasons.append("outfit type not ideal for this weather")
        if material_status == "❌":
            reasons.append("material not suitable for this temperature")
        reason_text = " and ".join(reasons)
        return f"❌ Not recommended – {reason_text}"
    
    # If either is ⚠, final is ⚠
    if outfit_status == "⚠" or material_status == "⚠":
        reasons = []
        if outfit_status == "⚠":
            reasons.append("outfit type has mixed compatibility")
        if material_status == "⚠":
            reasons.append("material comfort may vary")
        reason_text = " and ".join(reasons)
        return f"⚠ Proceed with caution – {reason_text}"
    
    # Both are ✅
    return "✅ Excellent choice – outfit and material are well-suited for this weather"
