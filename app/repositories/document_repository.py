import json
from typing import List, Optional
from app.repositories import BaseRepository
from app.repositories.library_repository import LibraryRepository
from app.models.models import Document, DocumentCreate
from app.core.logger import logger

class DocumentRepository(BaseRepository):    
    def __init__(self):
        super().__init__()
    
    def create_document(self, library_id: str, document: DocumentCreate) -> Optional[Document]:
        logger.info(f"Creating document in library: {library_id}")
        library_repo = LibraryRepository()
        if not library_repo.get_library(library_id):
            logger.error(f"Library not found: {library_id}")
            return None
        document_obj = Document(**document.model_dump(), library_id=library_id)
        
        # Insert into database
        self.execute_query(
            "INSERT INTO documents (id, library_id, name, metadata, created_at) VALUES (?, ?, ?, ?, ?)",
            (document_obj.id, document_obj.library_id, document_obj.name, 
             json.dumps(document_obj.metadata.model_dump()), document_obj.created_at)
        )
        logger.info(f"Document created with ID: {document_obj.id}")
        return document_obj
    
    def get_document(self, library_id: str, document_id: str) -> Optional[Document]:
        logger.info(f"Getting document: {document_id} from library: {library_id}")
        result = self.execute_query(
            "SELECT * FROM documents WHERE id = ? AND library_id = ?",
            (document_id, library_id)
        )
        if not result:
            logger.warning(f"Document not found: {document_id}")
            return None
        row = result[0]
        
        # Convert metadata from JSON string back to dict
        metadata = json.loads(row["metadata"]) if row["metadata"] else {}
        
        return Document(
            id=row["id"],
            library_id=row["library_id"],
            name=row["name"],
            metadata=metadata,
            created_at=row["created_at"]
        )
    
    def get_documents_by_library(self, library_id: str) -> List[Document]:
        logger.info(f"Getting all documents in library: {library_id}")
        result = self.execute_query(
            "SELECT * FROM documents WHERE library_id = ?",
            (library_id,)
        )
        documents = []
        for row in result:
            metadata = json.loads(row["metadata"]) if row["metadata"] else {}
            documents.append(Document(
                id=row["id"],
                library_id=row["library_id"],
                name=row["name"],
                metadata=metadata,
                created_at=row["created_at"]
            ))
        return documents
    
    def update_document(self, library_id: str, document_id: str, document: DocumentCreate) -> Optional[Document]:
        logger.info(f"Updating document: {document_id} in library: {library_id}")
        existing_document = self.get_document(library_id, document_id)
        if not existing_document:
            return None
        self.execute_query(
            "UPDATE documents SET name = ?, metadata = ? WHERE id = ? AND library_id = ?",
            (document.name, json.dumps(document.metadata.model_dump()), document_id, library_id)
        )
        return self.get_document(library_id, document_id)
    
    def delete_document(self, library_id: str, document_id: str) -> bool:
        logger.info(f"Deleting document: {document_id} from library: {library_id}")
        existing_document = self.get_document(library_id, document_id)
        if not existing_document:
            return False
        self.execute_query(
            "DELETE FROM documents WHERE id = ? AND library_id = ?",
            (document_id, library_id)
        )
        logger.info(f"Document deleted: {document_id}")
        return True
    