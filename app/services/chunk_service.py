from typing import List, Optional, Tuple
from app.repositories.chunk_repository import ChunkRepository
from app.repositories.library_repository import LibraryRepository
from app.repositories.document_repository import DocumentRepository
from app.utils.cohere_client import cohere_client
from app.utils.locking import lock_manager
from app.models.models import Chunk, ChunkCreate
from app.core.logger import logger

class ChunkService: 
    def __init__(self):
        self.repository = ChunkRepository()
        self.library_repository = LibraryRepository()
        self.document_repository = DocumentRepository()
    
    def create_chunk(self, library_id: str, document_id: Optional[str], chunk_data: ChunkCreate) -> Optional[Chunk]:
        logger.info(f"Creating chunk in library: {library_id}, document: {document_id}")
        if not library_id or not library_id.strip():
            logger.error("Library ID cannot be empty")
            raise ValueError("Library ID cannot be empty")
        
        if not chunk_data.text or not chunk_data.text.strip():
            logger.error("Chunk text cannot be empty")
            raise ValueError("Chunk text cannot be empty")
        
        library = self.library_repository.get_library(library_id)
        if not library:
            logger.error(f"Library not found: {library_id}")
            raise ValueError(f"Library not found: {library_id}")
        
        if document_id:
            document = self.document_repository.get_document(library_id, document_id)
            if not document:
                logger.error(f"Document not found: {document_id}")
                raise ValueError(f"Document not found: {document_id}")
        
        # Generate embedding
        if not chunk_data.embedding:
            logger.info(f"Generating embedding for chunk text: {chunk_data.text[:50]}")
            embedding = cohere_client.get_embedding(chunk_data.text)
            if not embedding:
                logger.error("Failed to generate embedding for chunk")
                raise ValueError("Failed to generate embedding for chunk")
            
            chunk_data.embedding = embedding
            logger.info("Embedding generated successfully")
        
        # Acquire lock for library to prevent concurrent writes
        with lock_manager.get_lock(library_id):
            chunk = self.repository.create_chunk(library_id, document_id, chunk_data)
            if not chunk:
                logger.error(f"Failed to create chunk in library: {library_id}")
                return None
            logger.info(f"Chunk created successfully: {chunk.id}")
            return chunk
    
    def get_chunk(self, library_id: str, document_id: Optional[str], chunk_id: str) -> Optional[Chunk]:
        logger.info(f"Getting chunk: {chunk_id} from library: {library_id}, document: {document_id}")

        if not library_id or not library_id.strip():
            logger.error("Library ID cannot be empty")
            raise ValueError("Library ID cannot be empty")
        
        if not chunk_id or not chunk_id.strip():
            logger.error("Chunk ID cannot be empty")
            raise ValueError("Chunk ID cannot be empty")
        
        library = self.library_repository.get_library(library_id)
        if not library:
            logger.error(f"Library not found: {library_id}")
            raise ValueError(f"Library not found: {library_id}")
        
        if document_id:
            document = self.document_repository.get_document(library_id, document_id)
            if not document:
                logger.error(f"Document not found: {document_id}")
                raise ValueError(f"Document not found: {document_id}")
        
        chunk = self.repository.get_chunk(library_id, document_id, chunk_id)
        if not chunk:
            logger.warning(f"Chunk not found: {chunk_id}")
            return None
        logger.info(f"Chunk retrieved successfully: {chunk_id}")
        return chunk
    
    def get_chunks_by_library(self, library_id: str) -> List[Chunk]:
        logger.info(f"Getting chunks in library: {library_id}")
        if not library_id or not library_id.strip():
            logger.error("Library ID cannot be empty")
            raise ValueError("Library ID cannot be empty")
        
        library = self.library_repository.get_library(library_id)
        if not library:
            logger.error(f"Library not found: {library_id}")
            raise ValueError(f"Library not found: {library_id}")
        chunks = self.repository.get_chunks_by_library(library_id)
        logger.info(f"Retrieved {len(chunks)} chunks from library: {library_id}")
        return chunks
    
    def get_chunks_by_document(self, library_id: str, document_id: str) -> List[Chunk]:
        logger.info(f"Getting all chunks in document: {document_id} from library: {library_id}")
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
        
        document = self.document_repository.get_document(library_id, document_id)
        if not document:
            logger.error(f"Document not found: {document_id}")
            raise ValueError(f"Document not found: {document_id}")
        
        chunks = self.repository.get_chunks_by_document(library_id, document_id)
        logger.info(f"Retrieved {len(chunks)} chunks from document: {document_id}")
        return chunks
    
    def get_all_vectors(self, library_id: str) -> Tuple[List[Chunk], List[List[float]]]:
        logger.info(f"Getting vectors for library: {library_id}")
        
        if not library_id or not library_id.strip():
            logger.error("Library ID cannot be empty")
            raise ValueError("Library ID cannot be empty")
        
        library = self.library_repository.get_library(library_id)
        if not library:
            logger.error(f"Library not found: {library_id}")
            raise ValueError(f"Library not found: {library_id}")
        
        chunks, vectors = self.repository.get_all_vectors(library_id)
        logger.info(f"Retrieved {len(chunks)} vectors from library: {library_id}")
        return chunks, vectors
    
    def update_chunk(self, library_id: str, document_id: Optional[str], chunk_id: str, chunk_data: ChunkCreate) -> Optional[Chunk]:
        logger.info(f"Updating chunk: {chunk_id} in library: {library_id}, document: {document_id}")
        if not library_id or not library_id.strip():
            logger.error("Library ID cannot be empty")
            raise ValueError("Library ID cannot be empty")
        
        if not chunk_id or not chunk_id.strip():
            logger.error("Chunk ID cannot be empty")
            raise ValueError("Chunk ID cannot be empty")
        
        if not chunk_data.text or not chunk_data.text.strip():
            logger.error("Chunk text cannot be empty")
            raise ValueError("Chunk text cannot be empty")
        
        library = self.library_repository.get_library(library_id)
        if not library:
            logger.error(f"Library not found: {library_id}")
            raise ValueError(f"Library not found: {library_id}")
        
        if document_id:
            document = self.document_repository.get_document(library_id, document_id)
            if not document:
                logger.error(f"Document not found: {document_id}")
                raise ValueError(f"Document not found: {document_id}")
        
        existing_chunk = self.repository.get_chunk(library_id, document_id, chunk_id)
        if not existing_chunk:
            logger.warning(f"Chunk not found: {chunk_id}")
            return None
        
        # Generate embedding if not provided and text has changed
        if not chunk_data.embedding and chunk_data.text != existing_chunk.text:
            logger.info(f"Generating embedding for updated chunk text: {chunk_data.text[:50]}...")
            embedding = cohere_client.get_embedding(chunk_data.text)
            if not embedding:
                logger.error("Failed to generate embedding for chunk")
                raise ValueError("Failed to generate embedding for chunk")

            chunk_data.embedding = embedding
            logger.info("Embedding generated successfully")
        
        # Acquire lock for library to prevent concurrent writes
        with lock_manager.get_lock(library_id):
            chunk = self.repository.update_chunk(library_id, document_id, chunk_id, chunk_data)
            if not chunk:
                logger.error(f"Failed to update chunk: {chunk_id}")
                return None
            logger.info(f"Chunk updated successfully: {chunk_id}")
            return chunk
    
    def delete_chunk(self, library_id: str, document_id: Optional[str], chunk_id: str) -> bool:
        logger.info(f"Deleting chunk: {chunk_id} from library: {library_id}, document: {document_id}")
        if not library_id or not library_id.strip():
            logger.error("Library ID cannot be empty")
            raise ValueError("Library ID cannot be empty")
        
        if not chunk_id or not chunk_id.strip():
            logger.error("Chunk ID cannot be empty")
            raise ValueError("Chunk ID cannot be empty")
        
        library = self.library_repository.get_library(library_id)
        if not library:
            logger.error(f"Library not found: {library_id}")
            raise ValueError(f"Library not found: {library_id}")
        
        if document_id:
            document = self.document_repository.get_document(library_id, document_id)
            if not document:
                logger.error(f"Document not found: {document_id}")
                raise ValueError(f"Document not found: {document_id}")
        
        existing_chunk = self.repository.get_chunk(library_id, document_id, chunk_id)
        if not existing_chunk:
            logger.warning(f"Chunk not found: {chunk_id}")
            return False
        
        with lock_manager.get_lock(library_id):
            success = self.repository.delete_chunk(library_id, document_id, chunk_id)
            if success:
                logger.info(f"Chunk deleted successfully: {chunk_id}")
            else:
                logger.error(f"Failed to delete chunk: {chunk_id}")
            
            return success
        