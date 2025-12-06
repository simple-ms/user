from uuid import UUID
from typing import List
from fastapi import APIRouter, Depends, status

from ..schemas.address import AddressCreate, AddressResponse
from ..services import AddressService
from ..dependencies import get_address_service, get_current_user_id

router = APIRouter(prefix="/users", tags=["Addresses"])


@router.post(
    "/addresses",
    response_model=AddressResponse,
    status_code=status.HTTP_201_CREATED
)
async def add_address(
    address: AddressCreate,
    user_id: UUID = Depends(get_current_user_id),
    address_service: AddressService = Depends(get_address_service)
):
    """
    Add a new address for the authenticated user.
    
    User ID is extracted from X-User-Id header (set by Nginx after token validation).
    """
    return await address_service.create_address(user_id, address)


@router.get(
    "/addresses",
    response_model=List[AddressResponse]
)
async def get_addresses(
    skip: int = 0,
    limit: int = 50,
    user_id: UUID = Depends(get_current_user_id),
    address_service: AddressService = Depends(get_address_service)
):
    """
    Get all addresses for the authenticated user with pagination.
    
    User ID is extracted from X-User-Id header (set by Nginx after token validation).
    """
    return await address_service.get_addresses(user_id, skip, limit)


@router.get(
    "/addresses/{address_id}",
    response_model=AddressResponse
)
async def get_address(
    address_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    address_service: AddressService = Depends(get_address_service)
):
    """Get a specific address by ID."""
    return await address_service.get_address(address_id, user_id)


@router.put(
    "/addresses/{address_id}",
    response_model=AddressResponse
)
async def update_address(
    address_id: UUID,
    address_update: AddressCreate,
    user_id: UUID = Depends(get_current_user_id),
    address_service: AddressService = Depends(get_address_service)
):
    """Update an existing address."""
    return await address_service.update_address(address_id, user_id, address_update)


@router.delete(
    "/addresses/{address_id}",
    status_code=status.HTTP_200_OK
)
async def delete_address(
    address_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    address_service: AddressService = Depends(get_address_service)
):
    """
    Delete a specific address.
    
    Only the owner of the address can delete it.
    """
    return await address_service.delete_address(address_id, user_id)

