from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
import sys
from app.core.logger import logger
from app.routers import (
    libraries_router, 
    documents_router, 
    chunks_router, 
    index_router, 
    search_router
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application starting up")
    try:
        data_dir = "data"
        if not os.path.exists(data_dir):
            os.makedirs(data_dir, exist_ok=True)
            logger.info(f"Created data directory: {data_dir}")
        
        # Initialize database
        logger.info("Initializing database")
        from app.repositories.library_repository import LibraryRepository
        repo = LibraryRepository()
        logger.info("Database initialized successfully")
        
        # Test cohere connection
        logger.info("Testing Cohere API connection")
        from app.utils.cohere_client import cohere_client
        if cohere_client.health_check():
            logger.info("Cohere API connection successful")
        else:
            logger.warning("Cohere API connection failed - check API key")
        
        yield
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # Shutdown
    logger.info("Application shutting down")

# Initialize FastAPI application with lifespan
app = FastAPI(
    title="Indexing Algorithms API",
    description="REST API that allows users to index and query their documents within a Vector Database",
    version="1.0.0",
    docs_url="/docs",
    lifespan=lifespan
)

# Include routers
app.include_router(libraries_router, prefix="/libraries", tags=["libraries"])
app.include_router(documents_router, prefix="/libraries/{library_id}/documents", tags=["documents"])
app.include_router(chunks_router, prefix="/libraries/{library_id}/documents/{document_id}/chunks", tags=["chunks"])
app.include_router(index_router, prefix="/libraries/{library_id}/index", tags=["indexing"])
app.include_router(search_router, prefix="/libraries/{library_id}/search", tags=["search"])

@app.get("/")
async def root():
    """Health check endpoint"""
    logger.info("Health check endpoint called")
    return {
        "message": "Vector Database API is running",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "libraries": "/libraries",
            "documents": "/libraries/{library_id}/documents",
            "chunks": "/libraries/{library_id}/documents/{document_id}/chunks",
            "indexing": "/libraries/{library_id}/index",
            "search": "/libraries/{library_id}/search"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    logger.info("Health check endpoint called")
    return {"status": "healthy", "service": "vector-database-api"}

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers
@app.exception_handler(404)
async def not_found_exception_handler(request: Request, exc: Exception):
    """Handle 404 errors"""
    logger.warning(f"404 error: {request.url} not found")
    return JSONResponse(
        status_code=404,
        content={"message": f"The requested resource {request.url} was not found"},
    )

@app.exception_handler(500)
async def internal_server_error_handler(request: Request, exc: Exception):
    """Handle 500 errors"""
    logger.error(f"500 error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"message": "Internal server error"},
    )

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting server")
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
