"""
Seed data for users table
Creates test users for development and testing
"""
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models import User
from datetime import datetime
import uuid


def seed_users():
    """Create test users in the database"""
    
    db: Session = SessionLocal()
    
    try:
        print("Seeding users table...")
        print("-" * 60)
        
        # Test users to create
        test_users = [
            {
                "id": uuid.UUID("123e4567-e89b-12d3-a456-426614174000"),
                "email": "test@example.com",
                "password_hash": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqNx8qKqKu",  # hashed "password123"
                "role": "user",
                "is_active": True
            },
            {
                "id": uuid.UUID("223e4567-e89b-12d3-a456-426614174001"),
                "email": "admin@example.com",
                "password_hash": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqNx8qKqKu",  # hashed "password123"
                "role": "admin",
                "is_active": True
            },
            {
                "id": uuid.UUID("323e4567-e89b-12d3-a456-426614174002"),
                "email": "demo@example.com",
                "password_hash": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqNx8qKqKu",  # hashed "password123"
                "role": "user",
                "is_active": True
            }
        ]
        
        created_count = 0
        skipped_count = 0
        
        for user_data in test_users:
            # Check if user already exists
            existing_user = db.query(User).filter(User.id == user_data["id"]).first()
            
            if existing_user:
                print(f"⊘ User {user_data['email']} already exists (ID: {user_data['id']})")
                skipped_count += 1
                continue
            
            # Create new user
            user = User(
                id=user_data["id"],
                email=user_data["email"],
                password_hash=user_data["password_hash"],
                role=user_data["role"],
                is_active=user_data["is_active"],
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            db.add(user)
            db.commit()
            
            print(f"✓ Created user: {user_data['email']} (ID: {user_data['id']}, Role: {user_data['role']})")
            created_count += 1
        
        print("-" * 60)
        print(f"\n✓ Seeding complete!")
        print(f"  Created: {created_count} users")
        print(f"  Skipped: {skipped_count} users (already exist)")
        
        if created_count > 0:
            print("\n📝 Test User Credentials:")
            print("  Email: test@example.com")
            print("  Password: password123")
            print("  User ID: 123e4567-e89b-12d3-a456-426614174000")
            print("\n  Email: admin@example.com")
            print("  Password: password123")
            print("  User ID: 223e4567-e89b-12d3-a456-426614174001")
        
    except Exception as e:
        db.rollback()
        print(f"\n✗ Error seeding users: {str(e)}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_users()
