from fastapi import FastAPI

from app.api import router
from app.config import settings
from app.models import HealthResponse


app = FastAPI(title=settings.app_name)
app.include_router(router)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        app=settings.app_name,
        environment=settings.environment,
    )
