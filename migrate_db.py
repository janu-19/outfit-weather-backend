"""
Database migration script to add user authentication.
This script will:
1. Create the users table
2. Add owner_id column to outfits table (for existing databases)
3. For existing outfits, you'll need to assign them to a user manually
"""
from sqlalchemy import text
from database import engine, Base
from models import User, Outfit

def migrate_database():
    """
    Migrate database to add user support.
    """
    print("Starting database migration...")
    
    # Create all tables (will create users table if it doesn't exist)
    Base.metadata.create_all(bind=engine)
    print("[OK] Created/verified all tables")
    
    # Check if outfits table already exists and if owner_id column exists
    with engine.connect() as conn:
        # Check if outfits table exists
        result = conn.execute(text("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='outfits'
        """))
        table_exists = result.fetchone() is not None
        
        if table_exists:
            # Check if owner_id column exists
            result = conn.execute(text("PRAGMA table_info(outfits)"))
            columns = [row[1] for row in result.fetchall()]
            
            if 'owner_id' not in columns:
                print("Adding owner_id column to outfits table...")
                try:
                    # SQLite doesn't support ALTER TABLE ADD COLUMN with NOT NULL without a default
                    # We'll add it as nullable. New entries via the API will require owner_id
                    conn.execute(text("ALTER TABLE outfits ADD COLUMN owner_id INTEGER"))
                    conn.commit()
                    print("[OK] Added owner_id column to outfits table")
                    print("[WARNING] Existing outfits have owner_id = NULL")
                    print("   These outfits will NOT be accessible via the API.")
                    print("   Options:")
                    print("   1. Delete them: DELETE FROM outfits WHERE owner_id IS NULL;")
                    print("   2. Assign to a user (after creating one via registration)")
                except Exception as e:
                    print(f"[ERROR] Error adding owner_id column: {e}")
                    print("   If the column already exists, this is normal.")
            else:
                print("[OK] owner_id column already exists in outfits table")
        else:
            print("✓ outfits table will be created with owner_id column")
    
    print("\nMigration complete!")
    print("\nNext steps:")
    print("1. Register a new user via POST /auth/register")
    print("2. Login to get your JWT token via POST /auth/login")
    print("3. Use the token in the Authorization header: 'Bearer <token>'")
    print("4. All wardrobe endpoints now require authentication")

if __name__ == "__main__":
    migrate_database()

