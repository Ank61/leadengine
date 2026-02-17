from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Index, text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base


class RawLead(Base):
    __tablename__ = "raw_leads"

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
    scrape_job_id = Column(
        UUID(as_uuid=True),
        ForeignKey("scrape_jobs.id", ondelete="CASCADE"),
        nullable=False
    )
    
    raw_payload = Column(JSONB, nullable=False)
    source_url = Column(Text)
    data_hash = Column(Text, unique=True, nullable=False)
    
    scraped_at = Column(DateTime, default=datetime.utcnow, server_default=text("NOW()"))
    
    # Relationships
    user = relationship("User", backref="raw_leads")
    scrape_job = relationship("ScrapeJob", back_populates="raw_leads")

    def __repr__(self):
        return f"<RawLead(id={self.id}, scrape_job_id={self.scrape_job_id}, data_hash={self.data_hash[:8]}...)>"


# Indexes
Index("idx_raw_leads_user", RawLead.user_id)
Index("idx_raw_leads_job", RawLead.scrape_job_id)
Index("idx_raw_leads_payload", RawLead.raw_payload, postgresql_using="gin")
