"""Main FastAPI application."""
from fastapi import FastAPI
from app.routes import router
from app.logging_config import setup_logging

# Setup logging
setup_logging()

# Create FastAPI app
app = FastAPI(
    title="FastAPI Sync/Async Demo",
    description="Demonstration of sync/async interaction patterns",
    version="0.1.0"
)

# Include routes
app.include_router(router)


@app.get("/")
async def root():
    """Root endpoint with route listing."""
    return {
        "message": "FastAPI Sync/Async Demonstration",
        "routes": [
            {"path": "/sync-route-sync-inner-async-bg-sync-task", "pattern": "def/sync/async-bg-reg/sync-bg-task"},
            {"path": "/sync-route-sync-inner-async-bg-async-task", "pattern": "def/sync/async-bg-reg/async-bg-task"},
            {"path": "/sync-route-sync-inner-sync-bg-sync-task", "pattern": "def/sync/sync-bg-reg/sync-bg-task"},
            {"path": "/async-route-sync-inner-async-bg-async-task", "pattern": "async/sync/async-bg-reg/async-bg-task"},
            {"path": "/async-route-async-inner-async-bg-async-task", "pattern": "async/async/async-bg-reg/async-bg-task"},
            {"path": "/async-route-async-inner-async-bg-sync-task", "pattern": "async/async/async-bg-reg/sync-bg-task"},
            {"path": "/async-route-async-inner-sync-bg-sync-task", "pattern": "async/async/sync-bg-reg/sync-bg-task"},
        ]
    }
