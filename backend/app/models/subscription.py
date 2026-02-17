from sqlalchemy import Column, String, Boolean, DateTime, text, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from app.db.base import Base

class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()")
    )
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    plan_name = Column(String(100), nullable=False)
    monthly_scrape_limit = Column(Integer, default=1000, server_default=text("1000"))
    monthly_lead_limit = Column(Integer, default=500, server_default=text("500"))
    status = Column(String(50))
    starts_at = Column(DateTime, default=datetime.utcnow, server_default=text("NOW()"))
    expires_at = Column(DateTime, default=datetime.utcnow, server_default=text("NOW()"))
    created_at = Column(DateTime, default=datetime.utcnow, server_default=text("NOW()"))

    def __repr__(self):
        return f"<Subscription(id={self.id}, user_id={self.user_id}, plan_name={self.plan_name})>"  