from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.services.library_service import LibraryService
from app.models.models import Library, LibraryCreate
from app.core.logger import logger

router = APIRouter()

def get_library_service():
    return LibraryService()

@router.post("/", response_model=Library, status_code=status.HTTP_201_CREATED)
async def create_library(
    library: LibraryCreate,
    library_service: LibraryService = Depends(get_library_service)
):
    try:
        return library_service.create_library(library)
    except ValueError as e:
        logger.error(f"Value error creating library: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error creating library: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/", response_model=List[Library])
async def get_all_libraries(
    library_service: LibraryService = Depends(get_library_service)
):
    try:
        return library_service.get_all_libraries()
    except Exception as e:
        logger.error(f"Unexpected error getting libraries: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/{library_id}", response_model=Library)
async def get_library(
    library_id: str,
    library_service: LibraryService = Depends(get_library_service)
):
    try:
        library = library_service.get_library(library_id)
        if not library:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Library not found: {library_id}"
            )
        return library
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error getting library: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.put("/{library_id}", response_model=Library)
async def update_library(
    library_id: str,
    library: LibraryCreate,
    library_service: LibraryService = Depends(get_library_service)
):
    try:
        updated_library = library_service.update_library(library_id, library)
        if not updated_library:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Library not found: {library_id}"
            )
        return updated_library
    except ValueError as e:
        logger.error(f"Value error updating library: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error updating library: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.delete("/{library_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_library(
    library_id: str,
    library_service: LibraryService = Depends(get_library_service)
):
    try:
        success = library_service.delete_library(library_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Library not found: {library_id}"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error deleting library: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
    