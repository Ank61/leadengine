"""
Migration script to add new columns to scrape_jobs table
Run this once to update the existing table structure
"""
from sqlalchemy import text
from app.db.session import engine


def migrate_scrape_jobs_table():
    """Add new columns to scrape_jobs table"""
    
    migrations = [
        # Add industry column
        """
        ALTER TABLE scrape_jobs 
        ADD COLUMN IF NOT EXISTS industry VARCHAR(255);
        """,
        
        # Add geography column
        """
        ALTER TABLE scrape_jobs 
        ADD COLUMN IF NOT EXISTS geography VARCHAR(255);
        """,
        
        # Add keywords column (JSONB)
        """
        ALTER TABLE scrape_jobs 
        ADD COLUMN IF NOT EXISTS keywords JSONB;
        """,
        
        # Add source_types column (JSONB)
        """
        ALTER TABLE scrape_jobs 
        ADD COLUMN IF NOT EXISTS source_types JSONB;
        """,
        
        # Drop old source_type column if it exists
        """
        ALTER TABLE scrape_jobs 
        DROP COLUMN IF EXISTS source_type;
        """
    ]
    
    print("Starting migration of scrape_jobs table...")
    
    with engine.connect() as connection:
        for i, migration_sql in enumerate(migrations, 1):
            try:
                print(f"Running migration {i}/{len(migrations)}...")
                connection.execute(text(migration_sql))
                connection.commit()
                print(f"✓ Migration {i} completed")
            except Exception as e:
                print(f"✗ Migration {i} failed: {str(e)}")
                connection.rollback()
                raise
    
    print("\n✓ All migrations completed successfully!")
    print("\nNew columns added:")
    print("  - industry (VARCHAR 255)")
    print("  - geography (VARCHAR 255)")
    print("  - keywords (JSONB)")
    print("  - source_types (JSONB)")
    print("\nRemoved columns:")
    print("  - source_type (VARCHAR 100)")


if __name__ == "__main__":
    migrate_scrape_jobs_table()
