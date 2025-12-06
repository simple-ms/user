import re
from pydantic import BaseModel, Field, field_validator
from uuid import UUID


class AddressCreate(BaseModel):
    """Schema for creating an address."""
    title: str = Field(..., min_length=1, max_length=50, description="Address label (e.g., Home, Office)")
    street: str = Field(..., min_length=1, max_length=255, description="Street address")
    city: str = Field(..., min_length=1, max_length=100, description="City name")
    country: str = Field(..., min_length=1, max_length=100, description="Country name")
    zip_code: str = Field(..., min_length=1, max_length=20, description="Postal/ZIP code")
    
    @field_validator('title', 'city', 'country')
    @classmethod
    def validate_text_field(cls, v: str) -> str:
        """Validate and sanitize text fields."""
        v = v.strip()
        if not v:
            raise ValueError('Field cannot be empty or whitespace only')
        return v
    
    @field_validator('zip_code')
    @classmethod
    def validate_zip_code(cls, v: str) -> str:
        """Validate ZIP code format."""
        v = v.strip()
        if not re.match(r'^[A-Za-z0-9\s\-]+$', v):
            raise ValueError('ZIP code contains invalid characters')
        return v


class AddressResponse(AddressCreate):
    """Schema for address response."""
    id: UUID
    user_id: UUID

    class Config:
        from_attributes = True

