"""
Verify scrape_jobs table structure
"""
from sqlalchemy import text, inspect
from app.db.session import engine


def verify_table_structure():
    """Check the current structure of scrape_jobs table"""
    
    print("Checking scrape_jobs table structure...\n")
    
    inspector = inspect(engine)
    columns = inspector.get_columns('scrape_jobs')
    
    print("Current columns in scrape_jobs table:")
    print("-" * 60)
    
    for column in columns:
        col_type = str(column['type'])
        nullable = "NULL" if column['nullable'] else "NOT NULL"
        default = f" DEFAULT {column['default']}" if column.get('default') else ""
        
        print(f"  {column['name']:20} {col_type:20} {nullable:10}{default}")
    
    print("-" * 60)
    print(f"\nTotal columns: {len(columns)}")
    
    # Check for required new columns
    column_names = [col['name'] for col in columns]
    required_columns = ['industry', 'geography', 'keywords', 'source_types']
    
    print("\n✓ Required new columns:")
    for col in required_columns:
        status = "✓ Present" if col in column_names else "✗ Missing"
        print(f"  {col:20} {status}")
    
    # Check if old column is removed
    print("\n✓ Removed columns:")
    if 'source_type' in column_names:
        print("  source_type          ✗ Still exists (should be removed)")
    else:
        print("  source_type          ✓ Removed successfully")


if __name__ == "__main__":
    verify_table_structure()
