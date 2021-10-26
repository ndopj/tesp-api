from fastapi import APIRouter

from src.api.endpoints import endpoint


api_router = APIRouter()
api_router.include_router(endpoint.router, prefix="/ga4gh/tes/v1", tags=["TaskService"])
