import uuid
from typing import Optional
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from .database import Base


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
    zip_code: Mapped[str] = mapped_column(String(20))
    
    def __repr__(self) -> str:
        return f"<Address(id={self.id}, user_id={self.user_id}, title={self.title})>"
