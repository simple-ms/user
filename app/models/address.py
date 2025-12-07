import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column
from ..database import Base


class Address(Base):
    """User address model for storing delivery/billing addresses."""
    
    __tablename__ = "addresses"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    # We link this to the Auth User ID manually (no FK since it's in another DB)
    user_id: Mapped[uuid.UUID] = mapped_column(index=True)
    
    title: Mapped[str] = mapped_column(String(50))  # e.g. "Home", "Office"
    street: Mapped[str] = mapped_column(String(255))
    city: Mapped[str] = mapped_column(String(100))
    country: Mapped[str] = mapped_column(String(100))
    postal_code: Mapped[str] = mapped_column(String(20))
    
    # Default address flag
    is_default: Mapped[bool] = mapped_column(default=False, index=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )
    
    # Indexes for efficient queries
    __table_args__ = (
        Index('idx_address_user', 'user_id'),
        Index('idx_address_user_default', 'user_id', 'is_default'),
    )
    
    def __repr__(self) -> str:
        return f"<Address(id={self.id}, user_id={self.user_id}, title={self.title})>"
