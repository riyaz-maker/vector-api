from app.routers.libraries import router as libraries_router
from app.routers.documents import router as documents_router
from app.routers.chunks import router as chunks_router
from app.routers.index import router as index_router
from app.routers.search import router as search_router

__all__ = [
    "libraries_router",
    "documents_router",
    "chunks_router",
    "index_router",
    "search_router"
]
