"""
Database Migration Template
Create a copy of this file with a descriptive name: YYYYMMDD_description.py
Example: 20260217_add_user_fields.py
"""
from sqlalchemy import text
from app.db.session import engine


def upgrade():
    """
    Apply the migration
    Add your SQL statements here to modify the database schema
    """
    migrations = [
        # Example: Add a new column
        """
        ALTER TABLE table_name 
        ADD COLUMN IF NOT EXISTS column_name VARCHAR(255);
        """,
        
        # Example: Create a new table
        """
        CREATE TABLE IF NOT EXISTS new_table (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            name VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT NOW()
        );
        """,
        
        # Example: Create an index
        """
        CREATE INDEX IF NOT EXISTS idx_table_column 
        ON table_name(column_name);
        """,
        
        # Example: Modify a column
        """
        ALTER TABLE table_name 
        ALTER COLUMN column_name TYPE TEXT;
        """,
    ]
    
    print("Running upgrade migration...")
    
    with engine.connect() as connection:
        for i, migration_sql in enumerate(migrations, 1):
            try:
                print(f"  Executing migration {i}/{len(migrations)}...")
                connection.execute(text(migration_sql))
                connection.commit()
                print(f"  ✓ Migration {i} completed")
            except Exception as e:
                print(f"  ✗ Migration {i} failed: {str(e)}")
                connection.rollback()
                raise
    
    print("✓ Upgrade completed successfully!")


def downgrade():
    """
    Rollback the migration
    Add your SQL statements here to undo the changes
    """
    rollbacks = [
        # Example: Drop a column
        """
        ALTER TABLE table_name 
        DROP COLUMN IF EXISTS column_name;
        """,
        
        # Example: Drop a table
        """
        DROP TABLE IF EXISTS new_table;
        """,
        
        # Example: Drop an index
        """
        DROP INDEX IF EXISTS idx_table_column;
        """,
    ]
    
    print("Running downgrade migration...")
    
    with engine.connect() as connection:
        for i, rollback_sql in enumerate(rollbacks, 1):
            try:
                print(f"  Executing rollback {i}/{len(rollbacks)}...")
                connection.execute(text(rollback_sql))
                connection.commit()
                print(f"  ✓ Rollback {i} completed")
            except Exception as e:
                print(f"  ✗ Rollback {i} failed: {str(e)}")
                connection.rollback()
                raise
    
    print("✓ Downgrade completed successfully!")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python migration_file.py [upgrade|downgrade]")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "upgrade":
        upgrade()
    elif command == "downgrade":
        downgrade()
    else:
        print(f"Unknown command: {command}")
        print("Usage: python migration_file.py [upgrade|downgrade]")
        sys.exit(1)
