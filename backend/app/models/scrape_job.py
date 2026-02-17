from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey, Index, text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base


class ScrapeJob(Base):
    __tablename__ = "scrape_jobs"

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
    
    status = Column(String(50), default="queued", server_default="queued")
    
    # Scrape criteria
    industry = Column(String(255))
    geography = Column(String(255))
    keywords = Column(JSONB)  # Array of keywords
    source_types = Column(JSONB)  # Array of source types (e.g., ["google", "linkedin"])
    search_query = Column(Text)
    filters = Column(JSONB)  # Additional filters
    
    total_found = Column(Integer, default=0, server_default=text("0"))
    total_processed = Column(Integer, default=0, server_default=text("0"))
    
    created_at = Column(DateTime, default=datetime.utcnow, server_default=text("NOW()"))
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    
    # Relationships
    user = relationship("User", backref="scrape_jobs")
    raw_leads = relationship("RawLead", back_populates="scrape_job", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ScrapeJob(id={self.id}, user_id={self.user_id}, status={self.status})>"


# Indexes
Index("idx_scrape_jobs_user", ScrapeJob.user_id)
Index("idx_scrape_jobs_status", ScrapeJob.status)
