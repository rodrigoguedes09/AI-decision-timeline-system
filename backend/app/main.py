"""
AI Decision Timeline - Main FastAPI Application

This is the entry point for the backend API that powers the decision timeline system.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import decisions, traces, stats

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Decision Timeline API",
    description="Visual-first system for AI decision traceability and explainability",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(decisions.router, prefix="/api", tags=["decisions"])
app.include_router(traces.router, prefix="/api", tags=["traces"])
app.include_router(stats.router, prefix="/api", tags=["stats"])


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "AI Decision Timeline API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "decisions": "/api/decisions",
            "traces": "/api/traces",
            "stats": "/api/stats/overview"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "AI Decision Timeline"}
