import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import API routes
from app.api import router

# Create FastAPI app
app = FastAPI(
    title="King of the Hill API",
    description="A high-performance service for comparing TV advertisement scripts using LLMs",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development - restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Simple health check endpoint."""
    return {"status": "healthy"}
