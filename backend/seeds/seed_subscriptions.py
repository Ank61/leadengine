"""
Seed data for subscriptions table
Creates test subscriptions for test users
"""
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models import Subscription
from datetime import datetime, timedelta
import uuid


def seed_subscriptions():
    """Create test subscriptions in the database"""
    
    db: Session = SessionLocal()
    
    try:
        print("Seeding subscriptions table...")
        print("-" * 60)
        
        # Test subscriptions to create
        test_subscriptions = [
            {
                "id": uuid.uuid4(),
                "user_id": uuid.UUID("123e4567-e89b-12d3-a456-426614174000"),
                "plan_name": "Pro",
                "monthly_scrape_limit": 10000,
                "monthly_lead_limit": 5000,
                "status": "active",
                "starts_at": datetime.utcnow(),
                "expires_at": datetime.utcnow() + timedelta(days=30)
            },
            {
                "id": uuid.uuid4(),
                "user_id": uuid.UUID("223e4567-e89b-12d3-a456-426614174001"),
                "plan_name": "Enterprise",
                "monthly_scrape_limit": 100000,
                "monthly_lead_limit": 50000,
                "status": "active",
                "starts_at": datetime.utcnow(),
                "expires_at": datetime.utcnow() + timedelta(days=365)
            },
            {
                "id": uuid.uuid4(),
                "user_id": uuid.UUID("323e4567-e89b-12d3-a456-426614174002"),
                "plan_name": "Free",
                "monthly_scrape_limit": 100,
                "monthly_lead_limit": 50,
                "status": "active",
                "starts_at": datetime.utcnow(),
                "expires_at": datetime.utcnow() + timedelta(days=30)
            }
        ]
        
        created_count = 0
        skipped_count = 0
        
        for sub_data in test_subscriptions:
            # Check if subscription already exists for this user
            existing_sub = db.query(Subscription).filter(
                Subscription.user_id == sub_data["user_id"],
                Subscription.status == "active"
            ).first()
            
            if existing_sub:
                print(f"⊘ Active subscription already exists for user {sub_data['user_id']}")
                skipped_count += 1
                continue
            
            # Create new subscription
            subscription = Subscription(
                id=sub_data["id"],
                user_id=sub_data["user_id"],
                plan_name=sub_data["plan_name"],
                monthly_scrape_limit=sub_data["monthly_scrape_limit"],
                monthly_lead_limit=sub_data["monthly_lead_limit"],
                status=sub_data["status"],
                starts_at=sub_data["starts_at"],
                expires_at=sub_data["expires_at"],
                created_at=datetime.utcnow()
            )
            
            db.add(subscription)
            db.commit()
            
            print(f"✓ Created subscription: {sub_data['plan_name']} for user {sub_data['user_id']}")
            created_count += 1
        
        print("-" * 60)
        print(f"\n✓ Seeding complete!")
        print(f"  Created: {created_count} subscriptions")
        print(f"  Skipped: {skipped_count} subscriptions (already exist)")
        
    except Exception as e:
        db.rollback()
        print(f"\n✗ Error seeding subscriptions: {str(e)}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_subscriptions()
