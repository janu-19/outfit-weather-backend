def outfit_weather_check(outfit, temp, rain, min_temp=None, max_temp=None, rain_prob=0):
    outfit = outfit.lower()
    
    # Use range or fallback to current temp
    low_temp = min_temp if min_temp is not None else temp
    high_temp = max_temp if max_temp is not None else temp
    is_rainy = rain_prob > 40 or rain > 0 # Rain prob > 40% or current rain > 0mm
    
    reasons = []
    status = "✅"

    # 1. COLD CHECKS (based on daily minimum)
    if low_temp <= 5:
        if outfit not in ["jacket", "coat", "sweater", "hoodie"]:
            reasons.append("Extreme cold expected – thermal wear and heavy jacket required")
            status = "❌"
    elif 6 <= low_temp <= 12:
        if outfit in ["t-shirt", "dress", "kurti", "shirt", "polo", "top"]:
            reasons.append("Cold morning/evening – add jacket or sweater")
            status = "❌" if status == "✅" else status

    # 2. HEAT CHECKS (based on daily maximum)
    if high_temp >= 37:
        if outfit in ["jeans", "jacket", "coat", "hoodie", "sweater"]:
            reasons.append("Extreme heat likely – wear loose, light cotton clothes")
            status = "❌"
    elif 31 <= high_temp <= 36:
        if outfit in ["jacket", "coat", "sweater", "hoodie"]:
             reasons.append("Afternoon will be hot – avoid heavy layers")
             status = "❌" if status == "✅" else status

    # 3. RAIN CHECKS
    if is_rainy:
        if outfit in ["sandals", "white shoes", "suede shoes", "long skirt", "maxi dress"]:
            reasons.append("Rain expected – avoid open footwear or long trailing clothes")
            status = "❌" if status == "✅" else status
        elif outfit in ["white t-shirt", "white shirt", "white dress"]:
            reasons.append("Rain risk – white clothes may become transparent")
            status = "⚠" if status == "✅" else status

    # 4. GENERAL COMFORT (Average feel)
    # If no extreme warnings, give general advice based on current temp
    if not reasons:
        if 19 <= temp <= 24:
             return "✅ Comfortable weather for this outfit"
        elif 13 <= temp <= 18 and outfit in ["shorts", "skirt"]:
             return "⚠ Might be slightly cool for shorts/skirt"

    if not reasons:
        return "✅ Good choice for today's weather"

    return f"{status} {'; '.join(reasons)}"
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
