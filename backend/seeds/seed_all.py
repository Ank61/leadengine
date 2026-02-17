"""
Master seed script - runs all seed scripts in order
"""
import sys
import os

# Add parent directory to path so we can import from app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from seeds.seed_users import seed_users
from seeds.seed_subscriptions import seed_subscriptions


def seed_all():
    """Run all seed scripts in the correct order"""
    
    print("=" * 60)
    print("SEEDING DATABASE WITH TEST DATA")
    print("=" * 60)
    print()
    
    try:
        # 1. Seed users (must be first due to foreign key constraints)
        seed_users()
        print()
        
        # 2. Seed subscriptions (depends on users)
        seed_subscriptions()
        print()
        
        print("=" * 60)
        print("✓ ALL SEEDING COMPLETE!")
        print("=" * 60)
        print()
        print("🎉 Your database is now populated with test data!")
        print()
        print("📝 Test User for API:")
        print("  User ID: 123e4567-e89b-12d3-a456-426614174000")
        print("  Email: test@example.com")
        print("  Password: password123")
        print("  Plan: Pro (10,000 scrapes/month)")
        print()
        print("🚀 You can now test the API in Swagger:")
        print("  http://localhost:8000/docs")
        print()
        
    except Exception as e:
        print()
        print("=" * 60)
        print("✗ SEEDING FAILED")
        print("=" * 60)
        print(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    seed_all()
