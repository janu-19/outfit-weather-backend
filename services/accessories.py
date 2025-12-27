def outfit_accessories(outfit):
    mapping = {
        "t-shirt": [
            "watch", "sunglasses", "cap", "crossbody bag"
        ],
        "shirt": [
            "watch", "belt", "formal shoes", "wallet"
        ],
        "blouse": [
            "handbag", "earrings", "light necklace"
        ],
        "top": [
            "sling bag", "bracelet", "watch"
        ],

        "dress": [
            "handbag", "earrings", "heels", "clutch"
        ],
        "kurti": [
            "dupatta", "jhumkas", "bangles", "ethnic bag"
        ],
        "saree": [
            "blouse jewelry", "bangles", "clutch", "hair accessories"
        ],
        "lehenga": [
            "heavy jewelry", "clutch", "bangles", "hair pins"
        ],

        "jeans": [
            "belt", "wallet", "sneakers"
        ],
        "trousers": [
            "belt", "formal shoes", "watch"
        ],
        "shorts": [
            "cap", "sunglasses", "waist pouch"
        ],
        "skirt": [
            "handbag", "anklet", "bracelet"
        ],

        "jacket": [
            "scarf", "gloves", "beanie"
        ],
        "coat": [
            "leather gloves", "scarf", "formal shoes"
        ],
        "hoodie": [
            "backpack", "cap", "earphones"
        ],
        "sweater": [
            "scarf", "watch"
        ],

        "sneakers": [
            "ankle socks", "shoe cleaner"
        ],
        "sandals": [
            "footwear spray", "sunscreen"
        ],
        "heels": [
            "foot cushions", "clutch"
        ],
        "boots": [
            "thermal socks", "shoe spray"
        ],

        "travel": [
            "backpack", "power bank", "sunglasses"
        ],
        "gym wear": [
            "gym bag", "water bottle", "fitness band"
        ]
    }

    return mapping.get(outfit.lower(), ["watch", "wallet"])


def occasion_accessories(occasion):
    mapping = {
        "office": ["watch", "formal belt", "laptop bag"],
        "party": ["clutch", "statement jewelry"],
        "travel": ["backpack", "power bank", "sunglasses"],
        "gym": ["gym bag", "water bottle"],
        "college": ["backpack", "earphones"]
    }
    return mapping.get(occasion.lower(), [])


def rain_accessories(rain):
    acc = []

    if not rain or rain == 0:
        return acc

    if 0 < rain < 2:
        acc += ["umbrella"]
    elif 2 <= rain < 10:
        acc += ["umbrella", "waterproof bag cover"]
    else:
        acc += ["raincoat", "waterproof backpack", "quick-dry towel"]

    return acc


def temperature_accessories(temp):
    acc = []

    if temp <= 5:
        acc += ["woolen gloves", "beanie", "thermal socks", "scarf"]
    elif temp <= 12:
        acc += ["scarf", "gloves"]
    elif temp <= 18:
        acc += ["light scarf"]
    elif temp >= 30:
        acc += ["sunglasses", "cap"]
    
    return acc


def get_all_accessories(outfit, temp, rain, occasion=None):
    accessories = set()

    accessories.update(outfit_accessories(outfit))
    accessories.update(temperature_accessories(temp))
    accessories.update(rain_accessories(rain))

    if occasion:
        accessories.update(occasion_accessories(occasion))

    return list(accessories)
