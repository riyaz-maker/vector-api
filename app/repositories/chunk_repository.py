import json
import numpy as np
import os
from typing import List, Optional, Tuple
from app.repositories import BaseRepository
from app.repositories.library_repository import LibraryRepository
from app.repositories.document_repository import DocumentRepository
from app.models.models import Chunk, ChunkCreate
from app.core.logger import logger
from app.core.config import settings

class ChunkRepository(BaseRepository):
    
    def __init__(self):
        super().__init__()
        data_dir = "data"
        if not os.path.exists(data_dir):
            os.makedirs(data_dir, exist_ok=True)
            logger.info(f"Created data directory: {data_dir}")
    
    def _get_vector_file_path(self, library_id: str) -> str:
        return f"data/vectors_{library_id}.npy"
    
    def _load_vectors(self, library_id: str) -> np.ndarray:
        file_path = self._get_vector_file_path(library_id)
        if os.path.exists(file_path):
            return np.load(file_path, allow_pickle=True)
        return np.array([])
    
    def _save_vectors(self, library_id: str, vectors: np.ndarray):
        file_path = self._get_vector_file_path(library_id)
        np.save(file_path, vectors)
    
    def create_chunk(self, library_id: str, document_id: Optional[str], chunk: ChunkCreate) -> Optional[Chunk]:
        logger.info(f"Creating chunk in library: {library_id}, document: {document_id}")
        library_repo = LibraryRepository()
        if not library_repo.get_library(library_id):
            logger.error(f"Library not found: {library_id}")
            return None
        if document_id:
            document_repo = DocumentRepository()
            if not document_repo.get_document(library_id, document_id):
                logger.error(f"Document not found: {document_id}")
                return None
    
        chunk_obj = Chunk(**chunk.model_dump(), library_id=library_id, document_id=document_id)
        vectors = self._load_vectors(library_id)
        
        # Add new vector and get it's index
        if chunk_obj.embedding:
            vector_index = len(vectors)
            vectors = np.append(vectors, [chunk_obj.embedding], axis=0) if len(vectors) > 0 else np.array([chunk_obj.embedding])
        else:
            vector_index = -1
        self._save_vectors(library_id, vectors)
        
        # Insert into database
        self.execute_query(
            "INSERT INTO chunks (id, library_id, document_id, text, embedding, metadata, vector_index, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (chunk_obj.id, chunk_obj.library_id, chunk_obj.document_id, chunk_obj.text,
             json.dumps(chunk_obj.embedding) if chunk_obj.embedding else None,
             json.dumps(chunk_obj.metadata.model_dump()), vector_index, chunk_obj.created_at)
        )
        logger.info(f"Chunk created with ID: {chunk_obj.id}")
        return chunk_obj
    
    def get_chunk(self, library_id: str, document_id: Optional[str], chunk_id: str) -> Optional[Chunk]:
        logger.info(f"Getting chunk: {chunk_id} from library: {library_id}, document: {document_id}")
        if document_id:
            result = self.execute_query(
                "SELECT * FROM chunks WHERE id = ? AND library_id = ? AND document_id = ?",
                (chunk_id, library_id, document_id)
            )
        else:
            result = self.execute_query(
                "SELECT * FROM chunks WHERE id = ? AND library_id = ? AND document_id IS NULL",
                (chunk_id, library_id)
            )
        if not result:
            logger.warning(f"Chunk not found: {chunk_id}")
            return None
        row = result[0]
        
        # Convert metadata and embedding from JSON string back to dict/list
        metadata = json.loads(row["metadata"]) if row["metadata"] else {}
        embedding = json.loads(row["embedding"]) if row["embedding"] else None
        return Chunk(
            id=row["id"],
            library_id=row["library_id"],
            document_id=row["document_id"],
            text=row["text"],
            embedding=embedding,
            metadata=metadata,
            created_at=row["created_at"]
        )
    
    def get_chunks_by_library(self, library_id: str) -> List[Chunk]:
        logger.info(f"Getting all chunks in library: {library_id}")
        result = self.execute_query(
            "SELECT * FROM chunks WHERE library_id = ?",
            (library_id,)
        )
        chunks = []
        for row in result:
            metadata = json.loads(row["metadata"]) if row["metadata"] else {}
            embedding = json.loads(row["embedding"]) if row["embedding"] else None
            chunks.append(Chunk(
                id=row["id"],
                library_id=row["library_id"],
                document_id=row["document_id"],
                text=row["text"],
                embedding=embedding,
                metadata=metadata,
                created_at=row["created_at"]
            ))
        return chunks
    
    def get_chunks_by_document(self, library_id: str, document_id: str) -> List[Chunk]:
        logger.info(f"Getting all chunks in document: {document_id} from library: {library_id}")
        result = self.execute_query(
            "SELECT * FROM chunks WHERE library_id = ? AND document_id = ?",
            (library_id, document_id)
        )
        chunks = []
        for row in result:
            metadata = json.loads(row["metadata"]) if row["metadata"] else {}
            embedding = json.loads(row["embedding"]) if row["embedding"] else None
            chunks.append(Chunk(
                id=row["id"],
                library_id=row["library_id"],
                document_id=row["document_id"],
                text=row["text"],
                embedding=embedding,
                metadata=metadata,
                created_at=row["created_at"]
            ))
        return chunks
    
    def get_all_vectors(self, library_id: str) -> Tuple[List[Chunk], np.ndarray]:
        logger.info(f"Getting all vectors for library: {library_id}")
        chunks = self.get_chunks_by_library(library_id)
        vectors = self._load_vectors(library_id)
        chunks_with_embeddings = [chunk for chunk in chunks if chunk.embedding is not None]
        vector_indices = []
        valid_vectors = []
        for i, chunk in enumerate(chunks):
            if chunk.embedding is not None:
                result = self.execute_query(
                    "SELECT vector_index FROM chunks WHERE id = ?",
                    (chunk.id,)
                )
                if result and result[0]["vector_index"] >= 0:
                    vector_indices.append(result[0]["vector_index"])
        
        if len(vector_indices) > 0:
            valid_vectors = vectors[vector_indices]
        return chunks_with_embeddings, valid_vectors
    
    def update_chunk(self, library_id: str, document_id: Optional[str], chunk_id: str, chunk: ChunkCreate) -> Optional[Chunk]:
        logger.info(f"Updating chunk: {chunk_id} in library: {library_id}, document: {document_id}")
        existing_chunk = self.get_chunk(library_id, document_id, chunk_id)
        if not existing_chunk:
            return None
        self.execute_query(
            "UPDATE chunks SET text = ?, embedding = ?, metadata = ? WHERE id = ? AND library_id = ? AND document_id = ?",
            (chunk.text, json.dumps(chunk.embedding) if chunk.embedding else None, 
             json.dumps(chunk.metadata.model_dump()), chunk_id, library_id, document_id)
        )
        if chunk.embedding and chunk.embedding != existing_chunk.embedding:
            vectors = self._load_vectors(library_id)
            result = self.execute_query(
                "SELECT vector_index FROM chunks WHERE id = ?",
                (chunk_id,)
            )
            if result and result[0]["vector_index"] >= 0:
                # Update the vector
                vectors[result[0]["vector_index"]] = chunk.embedding
                self._save_vectors(library_id, vectors)
        
        # Return updated chunk
        return self.get_chunk(library_id, document_id, chunk_id)
    
    def delete_chunk(self, library_id: str, document_id: Optional[str], chunk_id: str) -> bool:
        logger.info(f"Deleting chunk: {chunk_id} from library: {library_id}, document: {document_id}")
        existing_chunk = self.get_chunk(library_id, document_id, chunk_id)
        if not existing_chunk:
            return False
        
        if existing_chunk.embedding:
            vectors = self._load_vectors(library_id)
            result = self.execute_query(
                "SELECT vector_index FROM chunks WHERE id = ?",
                (chunk_id,)
            )
            if result and result[0]["vector_index"] >= 0:
                vectors[result[0]["vector_index"]] = np.zeros_like(vectors[result[0]["vector_index"]])
                self._save_vectors(library_id, vectors)
        
        if document_id:
            self.execute_query(
                "DELETE FROM chunks WHERE id = ? AND library_id = ? AND document_id = ?",
                (chunk_id, library_id, document_id)
            )
        else:
            self.execute_query(
                "DELETE FROM chunks WHERE id = ? AND library_id = ? AND document_id IS NULL",
                (chunk_id, library_id)
            )
        logger.info(f"Chunk deleted: {chunk_id}")
        return True
    