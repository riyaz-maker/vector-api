from fastapi import APIRouter, Depends, HTTPException, status, Path
from typing import Dict, Any
from app.services.indexing_service import IndexingService
from app.core.logger import logger

router = APIRouter()

def get_indexing_service():
    return IndexingService()

@router.post("/", status_code=status.HTTP_202_ACCEPTED)
async def build_index(
    library_id: str = Path(..., description="ID of the library"),
    index_type: str = "HNSW",
    parameters: Dict[str, Any] = {},
    indexing_service: IndexingService = Depends(get_indexing_service)
):
    try:
        success = indexing_service.build_index(library_id, index_type, parameters)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to build {index_type} index for library: {library_id}"
            )
        return {"message": f"Index building started for library: {library_id}"}
    except ValueError as e:
        logger.error(f"Value error building index: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error building index: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/", response_model=Dict[str, Any])
async def get_index_info(
    library_id: str = Path(..., description="ID of the library"),
    index_type: str = "HNSW",
    indexing_service: IndexingService = Depends(get_indexing_service)
):
    try:
        info = indexing_service.get_index_info(library_id, index_type)
        if not info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Index not found for library: {library_id}, type: {index_type}"
            )
        return info
    except ValueError as e:
        logger.error(f"Value error getting index info: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error getting index info: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
    