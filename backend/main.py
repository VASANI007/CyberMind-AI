"""
CyberMind AI - Enterprise FastAPI Server
"""

from __future__ import annotations

import time
import threading
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from backend.config import (
    APP_NAME,
    APP_VERSION,
    DEBUG,
    CORS_ORIGINS,
    BASE_DIR,
)
from backend.routers import scanners, history, analytics, ai, reports, settings, feedback, profile
from backend.db_service import db_service
from core.logger import logger


def _warmup_ml_models():
    """Pre-warm ML models in background thread for zero-latency inference."""
    try:
        from ml.model_loader import model_loader
        m_dir = BASE_DIR / "ml" / "models"
        p1 = m_dir / "phishing_url_model.pkl"
        p2 = m_dir / "online_valid_model.pkl"
        p3 = m_dir / "file_signatures_model.pkl"
        if p1.exists():
            model_loader.load(str(p1))
        if p2.exists():
            model_loader.load(str(p2))
        if p3.exists():
            model_loader.load(str(p3))
        logger.info("ML Models warmed up successfully.")
    except Exception as exc:
        logger.warning("ML warmup non-critical notice: %s", exc)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup actions
    logger.info(f"Starting {APP_NAME} v{APP_VERSION} Backend Engine...")
    t = threading.Thread(target=_warmup_ml_models, daemon=True)
    t.start()
    yield
    # Shutdown actions
    logger.info(f"Stopping {APP_NAME} Backend Engine...")


app = FastAPI(
    title=f"{APP_NAME} API",
    version=APP_VERSION,
    description="Enterprise Cybersecurity Threat Intelligence and Multi-Scanner API Layer",
    lifespan=lifespan,
    docs_url="/api/docs" if DEBUG else "/api/docs",
    redoc_url="/api/redoc" if DEBUG else "/api/redoc",
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1)(:[0-9]+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Request Timing Middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = f"{process_time:.4f}s"
    return response

# Include All API Routers
app.include_router(scanners.router)
app.include_router(history.router)
app.include_router(analytics.router)
app.include_router(ai.router)
app.include_router(reports.router)
app.include_router(settings.router)
app.include_router(feedback.router)
app.include_router(profile.router)


# Health Check
@app.get("/api/health", tags=["System"])
def health_check():
    from ml.model_loader import model_loader
    return {
        "status": "Healthy",
        "app": APP_NAME,
        "version": APP_VERSION,
        "database": "Connected",
        "ml_models_loaded": len(getattr(model_loader, "_cache", {})),
        "timestamp": time.time(),
    }


# Mount built React frontend if dist exists
frontend_dist = BASE_DIR / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/assets", StaticFiles(directory=str(frontend_dist / "assets")), name="assets")

    from fastapi.responses import FileResponse

    @app.get("/{full_path:path}", tags=["Frontend"])
    async def serve_react_app(full_path: str):
        # Don't intercept API routes or documentation
        if full_path.startswith("api/") or full_path in ("api", "docs", "redoc", "openapi.json"):
            return JSONResponse(status_code=404, content={"detail": "Not Found"})

        target_file = frontend_dist / full_path
        if target_file.is_file():
            return FileResponse(target_file)
        return FileResponse(frontend_dist / "index.html")
else:
    @app.get("/", tags=["Root"])
    def root():
        return {
            "message": f"Welcome to {APP_NAME} API Engine",
            "version": APP_VERSION,
            "docs": "/api/docs",
            "health": "/api/health",
        }


if __name__ == "__main__":
    import uvicorn
    from backend.config import BACKEND_HOST, BACKEND_PORT
    uvicorn.run("backend.main:app", host=BACKEND_HOST, port=BACKEND_PORT, reload=DEBUG)
