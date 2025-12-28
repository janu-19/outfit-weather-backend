import sys
import os
import requests
import io
import pickle
import numpy as np
from PIL import Image
from collections import defaultdict

# Add parent dir to sys.path to import apps modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models import UserUpload
from ml.extract_features import extract_features
from ml.classifier import REFERENCE_DIR, VECTORS_FILE, LABELS_FILE

def train():
    print("Starting offline retraining...")
    
    # Data structure: category -> list of feature vectors
    class_features = defaultdict(list)
    
    # 1. Load Existing Reference Images (Baseline)
    if os.path.exists(REFERENCE_DIR):
        print(f"Scanning base reference images in {REFERENCE_DIR}...")
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
                    print(f"Skipping base image {img_name}: {e}")

    # 2. Load Verified User Uploads (New Knowledge)
    db = SessionLocal()
    try:
        # Get all verified uploads
        verified_uploads = db.query(UserUpload).filter(UserUpload.is_verified == 1).all()
        print(f"Found {len(verified_uploads)} verified user uploads.")
        
        for upload in verified_uploads:
            if not upload.user_label or not upload.image_url:
                continue
                
            label = upload.user_label.lower()
            
            try:
                # Download image
                print(f"Downloading verified image (ID: {upload.id}, Label: {label})...")
                response = requests.get(upload.image_url, timeout=10)
                if response.status_code == 200:
                    img = Image.open(io.BytesIO(response.content)).convert("RGB")
                    feats = extract_features(img)
                    class_features[label].append(feats)
                else:
                    print(f"Failed to download ID {upload.id}: Status {response.status_code}")
            except Exception as e:
                print(f"Error processing ID {upload.id}: {e}")
                
    finally:
        db.close()
        
    # 3. Compute Prototypes
    print("Computing new prototypes...")
    class_prototypes = {}
    for label, feats in class_features.items():
        if len(feats) > 0:
            class_prototypes[label] = np.mean(feats, axis=0)
            
    if not class_prototypes:
        print("No data found! Keeping existing model.")
        return

    # 4. Save to Disk
    labels = list(class_prototypes.keys())
    vectors = np.array(list(class_prototypes.values()))
    
    print(f"Saving model with {len(labels)} categories to disk...")
    np.save(VECTORS_FILE, vectors)
    with open(LABELS_FILE, "wb") as f:
        pickle.dump(labels, f)
        
    print("Retraining complete! Restart the application to apply changes.")

if __name__ == "__main__":
    train()
