from fastapi import APIRouter

from tesp_api.api.endpoints import task_endpoints


api_router = APIRouter()
api_router.include_router(task_endpoints.router, prefix="/v1", tags=["TaskService"])
