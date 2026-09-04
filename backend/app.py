from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.api.scanner import router as scanner_router
from backend.api.site_audit import router as site_audit_router
from backend.api.recommendations import router as recommendations_router
from backend.database.init_db import init_database


app = FastAPI(
    title="RankPilot AI API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",
        "http://localhost:5173",
        "https://rankpilot-ai.maazansari260.workers.dev",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Free Scan API
app.include_router(scanner_router)

# Pro Site Audit API
app.include_router(site_audit_router)
app.include_router(recommendations_router)


@app.on_event("startup")
def initialize_database() -> None:
    """Ensure the local database is ready before audit persistence is used."""
    init_database()


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
):
    return JSONResponse(
        status_code=400,
        content={"detail": "Invalid URL"},
    )


@app.get("/")
def root():
    return {
        "message": "Welcome to RankPilot AI API",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "RankPilot AI API",
        "version": "1.0.0",
    }
