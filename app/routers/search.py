from fastapi import APIRouter, Depends, HTTPException, status, Path
from typing import List
from app.services.query_service import QueryService
from app.models.models import SearchRequest, SearchResult
from app.core.logger import logger

router = APIRouter()

def get_query_service():
    return QueryService()

@router.post("/", response_model=List[SearchResult])
async def search(
    library_id: str = Path(..., description="ID of the library"),
    search_request: SearchRequest = None,
    index_type: str = "HNSW",
    query_service: QueryService = Depends(get_query_service)
):
    try:
        if search_request is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Search request data is required"
            )
        results = query_service.search(library_id, search_request, index_type)
        return results
    except ValueError as e:
        logger.error(f"Value error performing search: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error performing search: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
    