from typing import List
from fastapi import FastAPI, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select

from .database import get_db
from .models import Address
from .schemas import AddressCreate, AddressResponse
from .logger import logger
from .dependencies import get_current_user_id

app = FastAPI(
    title="User Service",
    description="User profile and address management microservice",
    version="1.0.0",
    docs_url="/docs/user",
    openapi_url="/openapi.json/user",
    redoc_url="/redoc/user"
)


# --- HEALTH CHECK ---

@app.get("/user/health", tags=["Health"])
async def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "healthy", "service": "user-service"}


# --- ADDRESS ENDPOINTS ---

@app.post(
    "/users/addresses",
    response_model=AddressResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Addresses"]
)
async def add_address(
    address: AddressCreate,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    Add a new address for the authenticated user.
    
    User ID is extracted from X-User-Id header (set by Nginx after token validation).
    """
    logger.info(f"Adding address for user {user_id}: {address.title}")
    
    try:
        new_address = Address(
            user_id=user_id,  # Link to the Auth User ID
            title=address.title,
            street=address.street,
            city=address.city,
            country=address.country,
            zip_code=address.zip_code
        )
        db.add(new_address)
        await db.commit()
        await db.refresh(new_address)
        
        logger.info(f"Address created successfully: {new_address.id} for user {user_id}")
        return new_address
        
    except SQLAlchemyError as e:
        await db.rollback()
        logger.error(f"Database error while adding address: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred"
        )


@app.get(
    "/users/addresses",
    response_model=List[AddressResponse],
    tags=["Addresses"]
)
async def get_addresses(
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    Get all addresses for the authenticated user.
    
    User ID is extracted from X-User-Id header (set by Nginx after token validation).
    """
    logger.info(f"Fetching addresses for user {user_id}")
    
    try:
        result = await db.execute(select(Address).filter(Address.user_id == user_id))
        addresses = result.scalars().all()
        
        logger.info(f"Found {len(addresses)} addresses for user {user_id}")
        return addresses
        
    except SQLAlchemyError as e:
        logger.error(f"Database error while fetching addresses: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred"
        )


@app.delete(
    "/users/addresses/{address_id}",
    status_code=status.HTTP_200_OK,
    tags=["Addresses"]
)
async def delete_address(
    address_id: str,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    Delete a specific address.
    
    Only the owner of the address can delete it.
    """
    logger.info(f"Delete address attempt: {address_id} by user {user_id}")
    
    try:
        result = await db.execute(
            select(Address).filter(
                Address.id == address_id,
                Address.user_id == user_id  # Ensure user owns this address
            )
        )
        address = result.scalar_one_or_none()
        
        if not address:
            logger.warning(f"Address not found or unauthorized: {address_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Address not found"
            )
        
        await db.delete(address)
        await db.commit()
        
        logger.info(f"Address deleted successfully: {address_id}")
        return {"message": "Address deleted successfully"}
        
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        await db.rollback()
        logger.error(f"Database error while deleting address: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred"
        )