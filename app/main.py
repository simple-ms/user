"""
User Service - User Profile and Address Management Microservice

This is the main entry point for the User service.
All routes are defined in views/ and registered via routes.py
"""
from fastapi import FastAPI

from .routes import register_routes

app = FastAPI(
    title="User Service",
    description="User profile and address management microservice",
    version="1.0.0",
    docs_url="/docs/user",
    openapi_url="/openapi.json/user",
    redoc_url="/redoc/user"
)

# NOTE: CORS is handled by nginx gateway - no CORS middleware here

# Register all routes
register_routes(app)
