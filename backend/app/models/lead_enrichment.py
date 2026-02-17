from sqlalchemy import Column, String, Float, Boolean, DateTime, Text, ForeignKey, Index, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base


class LeadEnrichment(Base):
    __tablename__ = "lead_enrichment"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()")
    )
    lead_id = Column(
        UUID(as_uuid=True),
        ForeignKey("leads.id", ondelete="CASCADE"),
        nullable=False
    )
    
    predicted_score = Column(Float)
    intent_level = Column(String(100))
    ai_summary = Column(Text)
    buying_signal = Column(Boolean, default=False, server_default=text("FALSE"))
    recommended_channel = Column(String(100))
    
    enriched_at = Column(DateTime, default=datetime.utcnow, server_default=text("NOW()"))
    
    # Relationships
    lead = relationship("Lead", back_populates="enrichment")

    def __repr__(self):
        return f"<LeadEnrichment(id={self.id}, lead_id={self.lead_id}, intent_level={self.intent_level})>"


# Index
Index("idx_enrichment_lead", LeadEnrichment.lead_id)
