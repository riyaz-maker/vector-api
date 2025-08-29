from fastapi import APIRouter, Depends, HTTPException, status, Path
from typing import List, Optional
from app.services.document_service import DocumentService
from app.models.models import Document, DocumentCreate
from app.core.logger import logger

router = APIRouter()

def get_document_service():
    return DocumentService()

@router.post("/", response_model=Document, status_code=status.HTTP_201_CREATED)
async def create_document(
    library_id: str = Path(..., description="ID of the library"),
    document: DocumentCreate = None,
    document_service: DocumentService = Depends(get_document_service)
):
    try:
        if document is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Document data is required"
            )
        created_document = document_service.create_document(library_id, document)
        if not created_document:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create document"
            )
        return created_document
    except ValueError as e:
        logger.error(f"Value error creating document: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error creating document: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/", response_model=List[Document])
async def get_all_documents(
    library_id: str = Path(..., description="ID of the library"),
    document_service: DocumentService = Depends(get_document_service)
):
    try:
        return document_service.get_documents_by_library(library_id)
    except ValueError as e:
        logger.error(f"Value error getting documents: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error getting documents: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/{document_id}", response_model=Document)
async def get_document(
    library_id: str = Path(..., description="ID of the library"),
    document_id: str = Path(..., description="ID of the document"),
    document_service: DocumentService = Depends(get_document_service)
):
    try:
        document = document_service.get_document(library_id, document_id)
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document not found: {document_id}"
            )
        return document
    except ValueError as e:
        logger.error(f"Value error getting document: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error getting document: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.put("/{document_id}", response_model=Document)
async def update_document(
    library_id: str = Path(..., description="ID of the library"),
    document_id: str = Path(..., description="ID of the document"),
    document: DocumentCreate = None,
    document_service: DocumentService = Depends(get_document_service)
):
    try:
        if document is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Document data is required"
            )
        updated_document = document_service.update_document(library_id, document_id, document)
        if not updated_document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document not found: {document_id}"
            )
        return updated_document
    except ValueError as e:
        logger.error(f"Value error updating document: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error updating document: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    library_id: str = Path(..., description="ID of the library"),
    document_id: str = Path(..., description="ID of the document"),
    document_service: DocumentService = Depends(get_document_service)
):
    try:
        success = document_service.delete_document(library_id, document_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document not found: {document_id}"
            )
    except ValueError as e:
        logger.error(f"Value error deleting document: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error deleting document: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
    