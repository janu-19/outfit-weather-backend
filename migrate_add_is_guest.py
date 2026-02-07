"""
Migration: Add is_guest column to predictions table
"""
import sqlite3

conn = sqlite3.connect("wardrobe.db")
cursor = conn.cursor()

try:
    # Check if is_guest column exists
    cursor.execute("PRAGMA table_info(predictions)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if "is_guest" not in columns:
        print("Adding is_guest column to predictions...")
        cursor.execute("ALTER TABLE predictions ADD COLUMN is_guest BOOLEAN DEFAULT 0 NOT NULL")
        conn.commit()
        print("✓ is_guest column added")
    else:
        print("✓ is_guest column already exists")
    
    # Make user_id nullable if needed
    cursor.execute("PRAGMA table_info(predictions)")
    columns_info = {col[1]: col for col in cursor.fetchall()}
    
    # Check if image_url can be nullable
    if "image_url" in columns_info:
        user_id_nullable = columns_info["user_id"][3] == 0  # notnull=0 means nullable
        if not user_id_nullable:
            print("Note: user_id is still NOT NULL. SQLite doesn't support ALTER COLUMN easily.")
            print("Predictions with null user_id may fail. This is OK for guest tracking if we use is_guest=True.")
    
    # Verify
    cursor.execute("PRAGMA table_info(predictions)")
    print("\nPredictions table schema:")
    for col in cursor.fetchall():
        print(f"  {col[1]}: {col[2]}")
    
except Exception as e:
    print(f"Error: {e}")
finally:
    conn.close()
