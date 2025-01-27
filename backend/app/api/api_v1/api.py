from fastapi import APIRouter
from app.api.api_v1.endpoints import config, data

api_router = APIRouter()

api_router.include_router(config.router, prefix="/config", tags=["config"])
api_router.include_router(data.router, prefix="/data", tags=["data"]) 