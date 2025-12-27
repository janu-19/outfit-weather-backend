def rain_rules(rain):
    if not rain or rain == 0:
        return []

    if 0 < rain < 2:
        return ["umbrella"]

    if 2 <= rain < 10:
        return ["umbrella", "water-resistant shoes"]

    if rain >= 10:
        return ["raincoat", "waterproof shoes", "extra socks"]
