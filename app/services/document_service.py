from typing import List, Optional
from app.repositories.document_repository import DocumentRepository
from app.repositories.library_repository import LibraryRepository
from app.models.models import Document, DocumentCreate
from app.core.logger import logger

class DocumentService:
    def __init__(self):
        self.repository = DocumentRepository()
        self.library_repository = LibraryRepository()
    
    def create_document(self, library_id: str, document_data: DocumentCreate) -> Optional[Document]:
        logger.info(f"Creating document in library: {library_id}")
        if not library_id or not library_id.strip():
            logger.error("Library ID cannot be empty")
            raise ValueError("Library ID cannot be empty")
        
        if not document_data.name or not document_data.name.strip():
            logger.error("Document name cannot be empty")
            raise ValueError("Document name cannot be empty")

        library = self.library_repository.get_library(library_id)
        if not library:
            logger.error(f"Library not found: {library_id}")
            raise ValueError(f"Library not found: {library_id}")
        
        document = self.repository.create_document(library_id, document_data)
        if not document:
            logger.error(f"Failed to create document in library: {library_id}")
            return None
        logger.info(f"Document created successfully: {document.id}")
        return document
    
    def get_document(self, library_id: str, document_id: str) -> Optional[Document]:
        logger.info(f"Getting document: {document_id} from library: {library_id}")
        if not library_id or not library_id.strip():
            logger.error("Library ID cannot be empty")
            raise ValueError("Library ID cannot be empty")
        
        if not document_id or not document_id.strip():
            logger.error("Document ID cannot be empty")
            raise ValueError("Document ID cannot be empty")
        
        library = self.library_repository.get_library(library_id)
        if not library:
            logger.error(f"Library not found: {library_id}")
            raise ValueError(f"Library not found: {library_id}")
        
        document = self.repository.get_document(library_id, document_id)
        if not document:
            logger.warning(f"Document not found: {document_id}")
            return None
        logger.info(f"Document retrieved successfully: {document_id}")
        return document
    
    def get_documents_by_library(self, library_id: str) -> List[Document]:
        logger.info(f"Getting all documents in library: {library_id}")
        if not library_id or not library_id.strip():
            logger.error("Library ID cannot be empty")
            raise ValueError("Library ID cannot be empty")
        
        library = self.library_repository.get_library(library_id)
        if not library:
            logger.error(f"Library not found: {library_id}")
            raise ValueError(f"Library not found: {library_id}")
        
        documents = self.repository.get_documents_by_library(library_id)
        logger.info(f"Retrieved {len(documents)} documents from library: {library_id}")
        return documents
    
    def update_document(self, library_id: str, document_id: str, document_data: DocumentCreate) -> Optional[Document]:
        logger.info(f"Updating document: {document_id} in library: {library_id}")
        if not library_id or not library_id.strip():
            logger.error("Library ID cannot be empty")
            raise ValueError("Library ID cannot be empty")
        
        if not document_id or not document_id.strip():
            logger.error("Document ID cannot be empty")
            raise ValueError("Document ID cannot be empty")
        
        if not document_data.name or not document_data.name.strip():
            logger.error("Document name cannot be empty")
            raise ValueError("Document name cannot be empty")
        
        library = self.library_repository.get_library(library_id)
        if not library:
            logger.error(f"Library not found: {library_id}")
            raise ValueError(f"Library not found: {library_id}")
        
        existing_document = self.repository.get_document(library_id, document_id)
        if not existing_document:
            logger.warning(f"Document not found: {document_id}")
            return None
        
        # Update document
        document = self.repository.update_document(library_id, document_id, document_data)
        if not document:
            logger.error(f"Failed to update document: {document_id}")
            return None
        logger.info(f"Document updated successfully: {document_id}")
        return document
    
    def delete_document(self, library_id: str, document_id: str) -> bool:
        logger.info(f"Deleting document: {document_id} from library: {library_id}")
        if not library_id or not library_id.strip():
            logger.error("Library ID cannot be empty")
            raise ValueError("Library ID cannot be empty")
        
        if not document_id or not document_id.strip():
            logger.error("Document ID cannot be empty")
            raise ValueError("Document ID cannot be empty")
        
        library = self.library_repository.get_library(library_id)
        if not library:
            logger.error(f"Library not found: {library_id}")
            raise ValueError(f"Library not found: {library_id}")
        
        existing_document = self.repository.get_document(library_id, document_id)
        if not existing_document:
            logger.warning(f"Document not found: {document_id}")
            return False
        
        success = self.repository.delete_document(library_id, document_id)
        if success:
            logger.info(f"Document deleted successfully: {document_id}")
        else:
            logger.error(f"Failed to delete document: {document_id}")
        
        return success
    