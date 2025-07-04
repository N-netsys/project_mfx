from fastapi import FastAPI
from .core.config import settings
from .api.v1.api import api_router
from .core.database import engine
from .models import Base # Import Base to ensure models are registered

# This line ensures that SQLAlchemy knows about all your models
# when a tool like Alembic inspects the application's metadata.
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    openapi_url="/api/v1/openapi.json"
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/", tags=["Health Check"])
def read_root():
    return {"status": "ok", "message": f"Welcome to {settings.PROJECT_NAME}"}