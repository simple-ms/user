from uuid import UUID
from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from .database import get_db
from .repository import AddressRepository
from .services import AddressService


async def get_address_repository(db: AsyncSession = Depends(get_db)) -> AddressRepository:
    """Dependency to get AddressRepository instance."""
    return AddressRepository(db)


async def get_address_service(
    address_repository: AddressRepository = Depends(get_address_repository)
) -> AddressService:
    """Dependency to get AddressService instance."""
    return AddressService(address_repository)


async def get_current_user_id(x_user_id: str = Header(..., alias="X-User-Id")) -> UUID:
    """
    Extract user ID from X-User-Id header set by Nginx after token validation.
    """
    try:
        return UUID(x_user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID in header"
        )
