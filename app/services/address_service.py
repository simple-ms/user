from uuid import UUID
from typing import List, Dict
from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError

from ..models.address import Address
from ..schemas.address import AddressCreate, AddressResponse
from ..repository import AddressRepository
from ..logger import logger


class AddressService:
    """Service for address business logic."""
    
    def __init__(self, address_repository: AddressRepository):
        self.address_repository = address_repository
    
    async def create_address(self, user_id: UUID, address_data: AddressCreate) -> Address:
        """Create a new address for a user."""
        logger.info(f"Adding address for user {user_id}: {address_data.title}")
        
        try:
            new_address = Address(
                user_id=user_id,
                title=address_data.title,
                street=address_data.street,
                city=address_data.city,
                country=address_data.country,
                zip_code=address_data.zip_code
            )
            address = await self.address_repository.create(new_address)
            logger.info(f"Address created successfully: {address.id} for user {user_id}")
            return address
        except SQLAlchemyError as e:
            await self.address_repository.rollback()
            logger.error(f"Database error while adding address: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred"
            )
    
    async def get_addresses(self, user_id: UUID, skip: int = 0, limit: int = 50) -> List[Address]:
        """Get all addresses for a user."""
        limit = min(limit, 50)  # Cap at 50 addresses
        
        logger.info(f"Fetching addresses for user {user_id}: skip={skip}, limit={limit}")
        
        try:
            addresses = await self.address_repository.get_all_by_user(user_id, skip, limit)
            logger.info(f"Found {len(addresses)} addresses for user {user_id}")
            return addresses
        except SQLAlchemyError as e:
            logger.error(f"Database error while fetching addresses: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred"
            )
    
    async def get_address(self, address_id: UUID, user_id: UUID) -> Address:
        """Get a specific address by ID for a user."""
        logger.info(f"Fetching address {address_id} for user {user_id}")
        
        try:
            address = await self.address_repository.get_by_id(address_id, user_id)
            
            if not address:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Address not found"
                )
            
            return address
        except HTTPException:
            raise
        except SQLAlchemyError as e:
            logger.error(f"Database error while fetching address: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred"
            )
    
    async def update_address(
        self, 
        address_id: UUID, 
        user_id: UUID, 
        address_data: AddressCreate
    ) -> Address:
        """Update an existing address."""
        logger.info(f"Updating address {address_id} for user {user_id}")
        
        try:
            address = await self.address_repository.get_by_id(address_id, user_id)
            
            if not address:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Address not found"
                )
            
            address.title = address_data.title
            address.street = address_data.street
            address.city = address_data.city
            address.country = address_data.country
            address.zip_code = address_data.zip_code
            
            updated_address = await self.address_repository.update(address)
            logger.info(f"Address updated successfully: {address_id}")
            return updated_address
        except HTTPException:
            raise
        except SQLAlchemyError as e:
            await self.address_repository.rollback()
            logger.error(f"Database error while updating address: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred"
            )
    
    async def delete_address(self, address_id: UUID, user_id: UUID) -> Dict[str, str]:
        """Delete an address."""
        logger.info(f"Delete address attempt: {address_id} by user {user_id}")
        
        try:
            address = await self.address_repository.get_by_id(address_id, user_id)
            
            if not address:
                logger.warning(f"Address not found or unauthorized: {address_id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Address not found"
                )
            
            await self.address_repository.delete(address)
            logger.info(f"Address deleted successfully: {address_id}")
            return {"message": "Address deleted successfully"}
        except HTTPException:
            raise
        except SQLAlchemyError as e:
            await self.address_repository.rollback()
            logger.error(f"Database error while deleting address: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred"
            )

