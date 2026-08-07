from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from backend.api.scanner import router as scanner_router
from backend.api.site_audit import router as site_audit_router


app = FastAPI(
    title="RankPilot AI API",
    version="1.0.0",
)

# Free Scan API
app.include_router(scanner_router)

# Pro Site Audit API
app.include_router(site_audit_router)


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