"""
Test the /metrics endpoint to verify it's querying the database
"""
from database import SessionLocal
from models import User, Prediction
from sqlalchemy import func

db = SessionLocal()

# Simulate the metrics query
total_predictions = db.query(func.count(Prediction.id)).scalar() or 0
total_users = db.query(func.count(func.distinct(User.id))).scalar() or 0

print(f"Total Users (from DB query): {total_users}")
print(f"Total Predictions (from DB query): {total_predictions}")

# Also check predictions table directly
preds = db.query(Prediction).all()
print(f"\nAll predictions in DB:")
for p in preds:
    print(f"  ID={p.id}, user_id={p.user_id}, is_guest={p.is_guest}, outfit={p.predicted_category}, confidence={p.confidence}")

db.close()
