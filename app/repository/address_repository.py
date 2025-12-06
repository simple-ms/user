from uuid import UUID
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..models.address import Address


class AddressRepository:
    """Repository for Address database operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_id(self, address_id: UUID, user_id: UUID) -> Address | None:
        """Get address by ID for a specific user."""
        result = await self.db.execute(
            select(Address).filter(
                Address.id == address_id,
                Address.user_id == user_id
            )
        )
        return result.scalar_one_or_none()
    
    async def get_all_by_user(self, user_id: UUID, skip: int = 0, limit: int = 50) -> List[Address]:
        """Get all addresses for a user with pagination."""
        result = await self.db.execute(
            select(Address)
            .filter(Address.user_id == user_id)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def create(self, address: Address) -> Address:
        """Create a new address."""
        self.db.add(address)
        await self.db.commit()
        await self.db.refresh(address)
        return address
    
    async def update(self, address: Address) -> Address:
        """Update an existing address."""
        await self.db.commit()
        await self.db.refresh(address)
        return address
    
    async def delete(self, address: Address) -> None:
        """Delete an address."""
        await self.db.delete(address)
        await self.db.commit()
    
    async def rollback(self) -> None:
        """Rollback the current transaction."""
        await self.db.rollback()

