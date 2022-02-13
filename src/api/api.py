from fastapi import APIRouter

from src.api.endpoints import task_service


api_router = APIRouter()
api_router.include_router(task_service.router, prefix="/ga4gh/tes/v1", tags=["TaskService"])
