from pydantic import BaseModel
from uuid import UUID
from typing import List

class AddressCreate(BaseModel):
    title: str
    street: str
    city: str
    country: str
    zip_code: str

class AddressResponse(AddressCreate):
    id: UUID
    user_id: UUID

    class Config:
        from_attributes = True