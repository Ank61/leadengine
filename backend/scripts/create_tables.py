"""
Script to create all database tables defined in SQLAlchemy models.
Run this script to initialize your database schema.
"""
from app.db.base import Base
from app.db.session import engine
# Import all models to register them with SQLAlchemy
from app.models import (
    User,
    Subscription,
    ScrapeJob,
    RawLead,
    Lead,
    LeadEnrichment,
    UsageTracking,
)


def create_tables():
    """Create all tables in the database."""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ All tables created successfully!")


if __name__ == "__main__":
    create_tables()
