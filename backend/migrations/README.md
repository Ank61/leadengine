# Database Migrations

## Overview
This folder contains database migration scripts for the LeadEngine application.

## Migration Naming Convention
Migrations should be named using the following format:
```
YYYYMMDD_description.py
```

**Examples:**
- `20260217_add_user_fields.py`
- `20260218_create_analytics_table.py`
- `20260219_add_indexes.py`

## Creating a New Migration

### Step 1: Copy the Template
```bash
cp migrations/migration_template.py migrations/20260217_your_description.py
```

### Step 2: Edit the Migration
Open the new file and modify the `upgrade()` and `downgrade()` functions:

```python
def upgrade():
    """Apply the migration"""
    migrations = [
        """
        ALTER TABLE scrape_jobs 
        ADD COLUMN IF NOT EXISTS priority INTEGER DEFAULT 0;
        """,
    ]
    # ... rest of the code

def downgrade():
    """Rollback the migration"""
    rollbacks = [
        """
        ALTER TABLE scrape_jobs 
        DROP COLUMN IF EXISTS priority;
        """,
    ]
    # ... rest of the code
```

### Step 3: Run the Migration

**Upgrade (apply changes):**
```bash
.\venv\Scripts\python.exe migrations\20260217_your_description.py upgrade
```

**Downgrade (rollback changes):**
```bash
.\venv\Scripts\python.exe migrations\20260217_your_description.py downgrade
```

## Migration Best Practices

### 1. Always Use IF EXISTS / IF NOT EXISTS
```sql
-- Good
ALTER TABLE users ADD COLUMN IF NOT EXISTS phone VARCHAR(50);

-- Bad (will fail if column exists)
ALTER TABLE users ADD COLUMN phone VARCHAR(50);
```

### 2. Make Migrations Reversible
Always provide a `downgrade()` function that undoes the `upgrade()`:

```python
def upgrade():
    # Add column
    ALTER TABLE users ADD COLUMN phone VARCHAR(50);

def downgrade():
    # Remove column
    ALTER TABLE users DROP COLUMN phone;
```

### 3. Test Migrations
Before running in production:
1. Run `upgrade` on a test database
2. Verify the changes
3. Run `downgrade` to ensure rollback works
4. Run `upgrade` again

### 4. Keep Migrations Small
One migration should do one logical thing:
- ✅ Good: `20260217_add_user_phone.py`
- ❌ Bad: `20260217_add_all_new_features.py`

### 5. Never Modify Existing Migrations
Once a migration has been run in production, never modify it. Create a new migration instead.

## Common Migration Examples

### Add a Column
```python
def upgrade():
    migrations = [
        """
        ALTER TABLE users 
        ADD COLUMN IF NOT EXISTS phone VARCHAR(50);
        """
    ]
```

### Create a Table
```python
def upgrade():
    migrations = [
        """
        CREATE TABLE IF NOT EXISTS user_preferences (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID REFERENCES users(id) ON DELETE CASCADE,
            theme VARCHAR(50) DEFAULT 'light',
            notifications_enabled BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT NOW()
        );
        """
    ]
```

### Add an Index
```python
def upgrade():
    migrations = [
        """
        CREATE INDEX IF NOT EXISTS idx_users_email 
        ON users(email);
        """
    ]
```

### Modify a Column Type
```python
def upgrade():
    migrations = [
        """
        ALTER TABLE users 
        ALTER COLUMN bio TYPE TEXT;
        """
    ]
```

### Add a Foreign Key
```python
def upgrade():
    migrations = [
        """
        ALTER TABLE scrape_jobs 
        ADD CONSTRAINT fk_scrape_jobs_user 
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;
        """
    ]
```

## Migration History

| Date | File | Description |
|------|------|-------------|
| 2026-02-17 | `migrate_scrape_jobs.py` | Added industry, geography, keywords, source_types columns |

## Troubleshooting

### Error: "relation does not exist"
**Cause:** Trying to modify a table that doesn't exist
**Solution:** Check table name spelling, or create the table first

### Error: "column already exists"
**Cause:** Not using `IF NOT EXISTS`
**Solution:** Add `IF NOT EXISTS` to your ALTER TABLE statement

### Error: "cannot drop column because other objects depend on it"
**Cause:** Trying to drop a column that's referenced by other tables
**Solution:** Drop the foreign key constraints first, then the column

## Using Alembic (Alternative)

For more advanced migration management, consider using Alembic:

```bash
# Initialize Alembic
alembic init alembic

# Create a migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Files in This Directory

- `migration_template.py` - Template for creating new migrations
- `README.md` - This file
- `YYYYMMDD_*.py` - Actual migration files
