from sqlalchemy import Column, String, Boolean, DateTime, text
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()")
    )
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    role = Column(String(50), default="user", server_default="user")
    is_active = Column(Boolean, default=True, server_default=text("TRUE"))
    created_at = Column(DateTime, default=datetime.utcnow, server_default=text("NOW()"))
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        server_default=text("NOW()")
    )

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"
