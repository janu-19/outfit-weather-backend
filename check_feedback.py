import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import UserUpload

# Add parent dir to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SQLALCHEMY_DATABASE_URL

def check_feedback():
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    try:
        print("\n--- Checking User Uploads & Feedback ---\n")
        
        # 1. Check Total Uploads
        total = db.query(UserUpload).count()
        print(f"Total uploads in DB: {total}")
        
        # 2. Check Verified Feedback
        verified = db.query(UserUpload).filter(UserUpload.is_verified == 1).all()
        print(f"Verified feedback entries: {len(verified)}")
        
        if verified:
            print("\nLatest 5 verified entries:")
            print("-" * 60)
            print(f"{'ID':<5} | {'Prediction':<15} | {'User Label':<15} | {'Confidence'}")
            print("-" * 60)
            for v in verified[-5:]:
                pred = v.predicted_category or "None"
                label = v.user_label or "None"
                conf = f"{v.confidence:.2f}" if v.confidence else "0.00"
                print(f"{v.id:<5} | {pred:<15} | {label:<15} | {conf}")
            print("-" * 60)
        else:
            print("\nNo verified feedback found yet.")
            
    except Exception as e:
        print(f"Error reading database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_feedback()
