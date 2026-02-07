import sqlite3

DB = "wardrobe.db"

def migrate():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    try:
        # Ensure PRAGMA foreign_keys is preserved
        c.execute("PRAGMA foreign_keys=OFF;")
        conn.commit()

        # Get existing columns
        c.execute("PRAGMA table_info(predictions)")
        cols = c.fetchall()
        col_names = [col[1] for col in cols]
        print('Existing columns:', col_names)

        # Create new table with user_id nullable and is_guest default 0
        c.execute('''
        CREATE TABLE IF NOT EXISTS predictions_new (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            is_guest BOOLEAN NOT NULL DEFAULT 0,
            outfit_id INTEGER,
            image_url TEXT,
            public_id TEXT,
            predicted_category TEXT,
            confidence REAL,
            weather_data TEXT,
            created_at DATETIME
        );
        ''')

        # Copy existing data into new table where columns match
        # We'll copy id, user_id (if exists), outfit_id, image_url, public_id, predicted_category, confidence, weather_data, created_at
        available = set(col_names)
        copy_cols = [c for c in ['id','user_id','outfit_id','image_url','public_id','predicted_category','confidence','weather_data','created_at'] if c in available]
        if not copy_cols:
            print('No compatible columns to copy; aborting')
            return

        cols_csv = ','.join(copy_cols)
        c.execute(f"INSERT INTO predictions_new ({cols_csv}) SELECT {cols_csv} FROM predictions;")

        # Drop old table and rename new
        c.execute("DROP TABLE predictions;")
        c.execute("ALTER TABLE predictions_new RENAME TO predictions;")

        conn.commit()
        print('Migration complete: predictions.user_id is now nullable')
    except Exception as e:
        print('Migration failed:', e)
    finally:
        c.execute("PRAGMA foreign_keys=ON;")
        conn.commit()
        conn.close()

if __name__ == '__main__':
    migrate()
