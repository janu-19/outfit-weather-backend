import os
from collections import defaultdict
import numpy as np
from PIL import Image
from sklearn.metrics.pairwise import cosine_similarity
from ml.extract_features import extract_features


REFERENCE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "reference_images")

# placeholders
class_features = defaultdict(list)
class_prototypes = {}
class_labels = []
class_vectors = np.array([])


def load_reference_prototypes():
    global class_features, class_prototypes, class_labels, class_vectors
    class_features = defaultdict(list)

    if not os.path.isdir(REFERENCE_DIR):
        class_prototypes = {}
        class_labels = []
        class_vectors = np.array([])
        return

    for label in os.listdir(REFERENCE_DIR):
        label_path = os.path.join(REFERENCE_DIR, label)
        if not os.path.isdir(label_path):
            continue
        for img_name in os.listdir(label_path):
            img_path = os.path.join(label_path, img_name)
            try:
                img = Image.open(img_path).convert("RGB")
                feats = extract_features(img)
                class_features[label].append(feats)
            except Exception as e:
                print(f"Skipping {img_path}: {e}")

    class_prototypes = {}
    for label, feats in class_features.items():
        if len(feats) > 0:
            class_prototypes[label] = np.mean(feats, axis=0)

    class_labels = list(class_prototypes.keys())
    class_vectors = np.array(list(class_prototypes.values())) if class_prototypes else np.array([])


load_reference_prototypes()


def predict_outfit_type(query_features):
    if class_vectors.size == 0:
        return "unknown", 0.0

    similarities = cosine_similarity([query_features], class_vectors)[0]
    best_idx = int(np.argmax(similarities))
    best_label = class_labels[best_idx]
    best_score = float(similarities[best_idx])

    top3_idx = similarities.argsort()[-3:][::-1]
    top3_labels = [class_labels[i] for i in top3_idx]
    final_label = max(set(top3_labels), key=top3_labels.count)
    confidence = round(best_score, 2)
    return final_label, confidence


def get_available_categories():
    """
    Get all available outfit categories for manual selection.
    """
    if class_labels:
        return sorted(class_labels)
    
    # Fallback: get from reference_images directory
    if os.path.isdir(REFERENCE_DIR):
        categories = [d for d in os.listdir(REFERENCE_DIR) 
                     if os.path.isdir(os.path.join(REFERENCE_DIR, d))]
        return sorted(categories)
    
    return []











