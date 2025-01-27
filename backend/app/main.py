from fastapi import FastAPI
from mangum import Mangum
from app.core.config import settings
from app.api.api_v1.api import api_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Strategic Analytics Dashboard Backend API"
)

app.include_router(api_router, prefix="/api/v1")

# Handler for AWS Lambda
handler = Mangum(app)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": settings.VERSION} 