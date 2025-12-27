# core/utils.py
import numpy as np

def to_native_types(obj):
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, (np.integer, np.floating)):
        return float(obj) if isinstance(obj, np.floating) else int(obj)
    elif isinstance(obj, dict):
        return {k: to_native_types(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [to_native_types(i) for i in obj]
    return obj


def confidence_message(conf):
    try:
        conf = float(conf)
    except:
        conf = 0.0

    if conf >= 0.75:
        return " Very confident prediction"
    elif conf >= 0.5:
        return " Confident prediction"
    elif conf >= 0.3:
        return " Medium confidence – may vary"
    else:
        return " Low confidence – image unclear"
