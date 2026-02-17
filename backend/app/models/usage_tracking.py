from sqlalchemy import Column, Integer, DateTime, ForeignKey, Index, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base import Base


class UsageTracking(Base):
    __tablename__ = "usage_tracking"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()")
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    
    scrapes_used = Column(Integer, default=0, server_default=text("0"))
    leads_generated = Column(Integer, default=0, server_default=text("0"))
    
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    
    # Relationships
    user = relationship("User", backref="usage_tracking")

    def __repr__(self):
        return f"<UsageTracking(id={self.id}, user_id={self.user_id}, scrapes={self.scrapes_used}, leads={self.leads_generated})>"


# Index
Index("idx_usage_user", UsageTracking.user_id)
