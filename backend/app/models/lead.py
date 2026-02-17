from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Index, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base


class Lead(Base):
    __tablename__ = "leads"

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
    
    # Company information
    company_name = Column(String(255))
    domain = Column(String(255))
    industry = Column(String(255))
    company_size = Column(String(100))
    location = Column(String(255))
    
    # Contact information
    first_name = Column(String(255))
    last_name = Column(String(255))
    job_title = Column(String(255))
    seniority = Column(String(100))
    
    # Contact details
    email = Column(String(255))
    phone = Column(String(100))
    linkedin_url = Column(String)
    
    # Metadata
    confidence_score = Column(Float, default=0.0, server_default=text("0.0"))
    source = Column(String(255))
    
    created_at = Column(DateTime, default=datetime.utcnow, server_default=text("NOW()"))
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        server_default=text("NOW()")
    )
    
    # Relationships
    user = relationship("User", backref="leads")
    enrichment = relationship("LeadEnrichment", back_populates="lead", uselist=False, cascade="all, delete-orphan")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint("user_id", "email", name="unique_user_email"),
    )

    def __repr__(self):
        return f"<Lead(id={self.id}, email={self.email}, company={self.company_name})>"


# Indexes
Index("idx_leads_user", Lead.user_id)
Index("idx_leads_email", Lead.email)
Index("idx_leads_domain", Lead.domain)
