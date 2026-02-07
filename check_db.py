import sqlite3

conn = sqlite3.connect("wardrobe.db")
cursor = conn.cursor()

# Check users
cursor.execute("SELECT COUNT(*) FROM users")
user_count = cursor.fetchone()[0]

# Check predictions
try:
    cursor.execute("SELECT COUNT(*) FROM predictions")
    pred_count = cursor.fetchone()[0]
    
    # Check prediction details
    cursor.execute("SELECT id, user_id, is_guest, predicted_category, confidence FROM predictions LIMIT 10")
    preds = cursor.fetchall()
    
    print(f"Users in DB: {user_count}")
    print(f"Predictions in DB: {pred_count}")
    print(f"Prediction rows:")
    for p in preds:
        print(f"  {p}")
except Exception as e:
    print(f"Users in DB: {user_count}")
    print(f"Error checking predictions: {e}")

conn.close()
