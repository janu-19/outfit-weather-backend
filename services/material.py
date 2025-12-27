MATERIAL_RULES = {
    "cotton": {
        "hot": {
            "verdict": "✅ Excellent choice for hot weather",
            "reason": "Cotton is breathable and absorbs sweat"
        },
        "warm": {
            "verdict": "✅ Comfortable for warm weather",
            "reason": "Allows airflow and keeps body cool"
        },
        "cold": {
            "verdict": "⚠ Needs layering in cold weather",
            "reason": "Cotton does not retain heat well"
        },
        "rain": {
            "verdict": "❌ Not ideal for rain",
            "reason": "Cotton absorbs water and dries slowly"
        }
    },

    "polyester": {
        "hot": {
            "verdict": "⚠ Can feel uncomfortable in heat",
            "reason": "Polyester traps heat and sweat"
        },
        "warm": {
            "verdict": "✅ Acceptable for warm weather",
            "reason": "Light polyester can still be worn"
        },
        "cold": {
            "verdict": "✅ Suitable for cold weather",
            "reason": "Provides better insulation than cotton"
        },
        "rain": {
            "verdict": "✅ Good for rain",
            "reason": "Quick-dry and water resistant"
        }
    },

    "wool": {
        "hot": {
            "verdict": "❌ Too warm for hot weather",
            "reason": "Wool traps heat"
        },
        "warm": {
            "verdict": "⚠ May feel heavy",
            "reason": "Better suited for cooler climates"
        },
        "cold": {
            "verdict": "✅ Excellent for cold weather",
            "reason": "Wool provides strong insulation"
        },
        "rain": {
            "verdict": "⚠ Avoid heavy rain",
            "reason": "Becomes heavy when wet"
        }
    },

    "silk": {
        "hot": {
            "verdict": "⚠ Depends on humidity",
            "reason": "Light but not sweat-friendly"
        },
        "warm": {
            "verdict": "✅ Comfortable for warm weather",
            "reason": "Lightweight and smooth fabric"
        },
        "cold": {
            "verdict": "❌ Not suitable for cold",
            "reason": "Provides little insulation"
        },
        "rain": {
            "verdict": "❌ Avoid rain",
            "reason": "Silk is delicate and stains easily"
        }
    },

    "nylon": {
        "hot": {
            "verdict": "❌ Uncomfortable in heat",
            "reason": "Poor breathability"
        },
        "warm": {
            "verdict": "⚠ Slightly uncomfortable",
            "reason": "Traps body heat"
        },
        "cold": {
            "verdict": "✅ Good for cold & wind",
            "reason": "Wind-resistant material"
        },
        "rain": {
            "verdict": "✅ Excellent for rain",
            "reason": "Water-resistant and quick-dry"
        }
    }
}


def material_analysis(material, temperature):
    """Temperature-aware material comfort analysis"""
    material = material.lower().strip()

    # Cotton analysis
    if material == "cotton":
        if temperature >= 25:
            return {
                "verdict": "✅ Excellent choice for hot weather",
                "reason": "Cotton is breathable and absorbs sweat"
            }
        elif 20 <= temperature < 25:
            return {
                "verdict": "⚠ Slightly cool",
                "reason": "Cotton may feel cool in breeze; consider layering"
            }
        else:
            return {
                "verdict": "❌ Not ideal",
                "reason": "Cotton does not retain heat in cool weather"
            }

    # Wool analysis
    if material == "wool":
        if temperature < 15:
            return {
                "verdict": "✅ Excellent for cold weather",
                "reason": "Wool provides strong insulation"
            }
        elif 15 <= temperature < 20:
            return {
                "verdict": "✅ Ideal",
                "reason": "Retains warmth in cool weather"
            }
        elif 20 <= temperature < 25:
            return {
                "verdict": "⚠ May feel warm",
                "reason": "Suitable but may cause overheating in mild weather"
            }
        else:
            return {
                "verdict": "❌ Too warm for hot weather",
                "reason": "Wool traps heat; avoid in hot temperatures"
            }

    # Polyester analysis
    if material == "polyester":
        if temperature >= 25:
            return {
                "verdict": "⚠ Can feel uncomfortable in heat",
                "reason": "Polyester traps heat and sweat"
            }
        elif 15 <= temperature < 25:
            return {
                "verdict": "✅ Acceptable choice",
                "reason": "Good insulation without excessive warmth"
            }
        else:
            return {
                "verdict": "✅ Suitable for cold weather",
                "reason": "Provides better insulation than cotton"
            }

    # Acrylic analysis
    if material == "acrylic":
        if temperature < 20:
            return {
                "verdict": "✅ Ideal",
                "reason": "Retains warmth in cool weather"
            }
        elif 20 <= temperature < 25:
            return {
                "verdict": "✅ Good choice",
                "reason": "Comfortable with light layering"
            }
        else:
            return {
                "verdict": "⚠ May feel warm",
                "reason": "Better for cool to mild temperatures"
            }

    # Silk analysis
    if material == "silk":
        if temperature >= 25:
            return {
                "verdict": "⚠ Depends on humidity",
                "reason": "Lightweight but not ideal for sweat absorption"
            }
        elif 20 <= temperature < 25:
            return {
                "verdict": "✅ Comfortable",
                "reason": "Lightweight and smooth fabric"
            }
        else:
            return {
                "verdict": "❌ Not suitable for cold",
                "reason": "Provides minimal insulation"
            }

    # Nylon analysis
    if material == "nylon":
        if temperature >= 25:
            return {
                "verdict": "❌ Uncomfortable in heat",
                "reason": "Poor breathability; traps body heat"
            }
        elif 10 <= temperature < 25:
            return {
                "verdict": "✅ Good for cool & wind",
                "reason": "Wind-resistant and decent insulation"
            }
        else:
            return {
                "verdict": "✅ Ideal for extreme cold",
                "reason": "Wind-resistant synthetic material"
            }

    # Linen analysis
    if material == "linen":
        if temperature >= 25:
            return {
                "verdict": "✅ Excellent for hot weather",
                "reason": "Highly breathable and moisture-wicking"
            }
        elif 20 <= temperature < 25:
            return {
                "verdict": "✅ Comfortable",
                "reason": "Breathable and lightweight"
            }
        else:
            return {
                "verdict": "⚠ Cool",
                "reason": "Minimal insulation; needs layering"
            }

    # Default for unrecognized materials
    return {
        "verdict": "⚠ Material not recognized",
        "reason": "No specific rules available for this material"
    }