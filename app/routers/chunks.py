from fastapi import APIRouter, Depends, HTTPException, status, Path
from typing import List, Optional
from app.services.chunk_service import ChunkService
from app.models.models import Chunk, ChunkCreate
from app.core.logger import logger

router = APIRouter()

def get_chunk_service():
    return ChunkService()

@router.post("/", response_model=Chunk, status_code=status.HTTP_201_CREATED)
async def create_chunk(
    library_id: str = Path(..., description="ID of the library"),
    document_id: str = Path(..., description="ID of the document"),
    chunk: ChunkCreate = None,
    chunk_service: ChunkService = Depends(get_chunk_service)
):
    try:
        if chunk is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Chunk data is required"
            )
        created_chunk = chunk_service.create_chunk(library_id, document_id, chunk)
        if not created_chunk:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create chunk"
            )
        return created_chunk
    except ValueError as e:
        logger.error(f"Value error creating chunk: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error creating chunk: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/", response_model=List[Chunk])
async def get_all_chunks(
    library_id: str = Path(..., description="ID of the library"),
    document_id: str = Path(..., description="ID of the document"),
    chunk_service: ChunkService = Depends(get_chunk_service)
):
    try:
        return chunk_service.get_chunks_by_document(library_id, document_id)
    except ValueError as e:
        logger.error(f"Value error getting chunks: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error getting chunks: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/{chunk_id}", response_model=Chunk)
async def get_chunk(
    library_id: str = Path(..., description="ID of the library"),
    document_id: str = Path(..., description="ID of the document"),
    chunk_id: str = Path(..., description="ID of the chunk"),
    chunk_service: ChunkService = Depends(get_chunk_service)
):
    try:
        chunk = chunk_service.get_chunk(library_id, document_id, chunk_id)
        if not chunk:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Chunk not found: {chunk_id}"
            )
        return chunk
    except ValueError as e:
        logger.error(f"Value error getting chunk: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error getting chunk: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.put("/{chunk_id}", response_model=Chunk)
async def update_chunk(
    library_id: str = Path(..., description="ID of the library"),
    document_id: str = Path(..., description="ID of the document"),
    chunk_id: str = Path(..., description="ID of the chunk"),
    chunk: ChunkCreate = None,
    chunk_service: ChunkService = Depends(get_chunk_service)
):
    try:
        if chunk is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Chunk data is required"
            )
        updated_chunk = chunk_service.update_chunk(library_id, document_id, chunk_id, chunk)
        if not updated_chunk:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Chunk not found: {chunk_id}"
            )
        return updated_chunk
    except ValueError as e:
        logger.error(f"Value error updating chunk: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error updating chunk: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.delete("/{chunk_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chunk(
    library_id: str = Path(..., description="ID of the library"),
    document_id: str = Path(..., description="ID of the document"),
    chunk_id: str = Path(..., description="ID of the chunk"),
    chunk_service: ChunkService = Depends(get_chunk_service)
):
    try:
        success = chunk_service.delete_chunk(library_id, document_id, chunk_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Chunk not found: {chunk_id}"
            )
    except ValueError as e:
        logger.error(f"Value error deleting chunk: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error deleting chunk: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
    