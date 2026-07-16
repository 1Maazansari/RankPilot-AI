from fastapi import FastAPI

app = FastAPI(
    title="RankPilot AI API",
    version="1.0.0"
)

@app.get("/")
def root():
    return {
        "message": "Welcome to RankPilot AI API",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "RankPilot AI API",
        "version": "1.0.0"
    }