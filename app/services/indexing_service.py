from typing import Optional, Dict, Any
from app.repositories.chunk_repository import ChunkRepository
from app.repositories.library_repository import LibraryRepository
from app.utils.locking import lock_manager
from app.core.logger import logger
import numpy as np

class IndexingService:  
    def __init__(self):
        self.repository = ChunkRepository()
        self.library_repository = LibraryRepository()
    
    def build_index(self, library_id: str, index_type: str = "HNSW", 
                   parameters: Optional[Dict[str, Any]] = None) -> bool:
        logger.info(f"Building {index_type} index for library: {library_id}")
        
        if not library_id or not library_id.strip():
            logger.error("Library ID cannot be empty")
            raise ValueError("Library ID cannot be empty")
        
        library = self.library_repository.get_library(library_id)
        if not library:
            logger.error(f"Library not found: {library_id}")
            raise ValueError(f"Library not found: {library_id}")
        
        # Get all chunks and vectors for library
        chunks, vectors = self.repository.get_all_vectors(library_id)
        if len(chunks) == 0 or len(vectors) == 0:
            logger.error(f"No vectors found for library: {library_id}")
            raise ValueError(f"No vectors found for library: {library_id}")
        
        # Acquire lock for the library to prevent concurrent writes
        with lock_manager.get_lock(library_id):
            if index_type == "HNSW":
                # Avoid circular imports
                from app.indexing.hnsw_index import HNSWIndex
                index = HNSWIndex()
                success = index.build_index(vectors, parameters or {})
            elif index_type == "FLAT":
                from app.indexing.flat_index import FlatIndex
                index = FlatIndex()
                success = index.build_index(vectors, parameters or {})
            else:
                logger.error(f"Unsupported index type: {index_type}")
                raise ValueError(f"Unsupported index type: {index_type}")
            
            if not success:
                logger.error(f"Failed to build {index_type} index for library: {library_id}")
                return False
            
            # Save index to disk
            index_path = f"data/index_{library_id}_{index_type}.pkl"
            index.save_index(index_path)
            
            logger.info(f"{index_type} index built successfully for library: {library_id}")
            return True
    
    def get_index_info(self, library_id: str, index_type: str = "HNSW") -> Optional[Dict[str, Any]]:
        logger.info(f"Getting index info for library: {library_id}, type: {index_type}")
        if not library_id or not library_id.strip():
            logger.error("Library ID cannot be empty")
            raise ValueError("Library ID cannot be empty")
        
        library = self.library_repository.get_library(library_id)
        if not library:
            logger.error(f"Library not found: {library_id}")
            raise ValueError(f"Library not found: {library_id}")
        index_path = f"data/index_{library_id}_{index_type}.pkl"
        
        if index_type == "HNSW":
            from app.indexing.hnsw_index import HNSWIndex
            index = HNSWIndex()
        elif index_type == "FLAT":
            from app.indexing.flat_index import FlatIndex
            index = FlatIndex()
        else:
            logger.error(f"Unsupported index type: {index_type}")
            raise ValueError(f"Unsupported index type: {index_type}")

        if not index.load_index(index_path):
            logger.warning(f"Index not found for library: {library_id}, type: {index_type}")
            return None
        
        info = index.get_index_info()
        logger.info(f"Index info retrieved for library: {library_id}")
        return info
    