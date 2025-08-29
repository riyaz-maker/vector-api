from typing import List, Optional, Dict, Any
from app.repositories.chunk_repository import ChunkRepository
from app.repositories.library_repository import LibraryRepository
from app.models.models import Chunk, SearchRequest, SearchResult
from app.core.logger import logger

class QueryService:
    def __init__(self):
        self.repository = ChunkRepository()
        self.library_repository = LibraryRepository()
    
    def search(self, library_id: str, search_request: SearchRequest, 
               index_type: str = "HNSW") -> List[SearchResult]:
        logger.info(f"Performing search in library: {library_id}")
        if not library_id or not library_id.strip():
            logger.error("Library ID cannot be empty")
            raise ValueError("Library ID cannot be empty")
        
        if not search_request.query_embedding:
            logger.error("Query embedding cannot be empty")
            raise ValueError("Query embedding cannot be empty")
        
        if search_request.k <= 0:
            logger.error("K must be greater than 0")
            raise ValueError("K must be greater than 0")
        
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

        # Try to load the index
        if not index.load_index(index_path):
            logger.error(f"Index not found for library: {library_id}, type: {index_type}")
            raise ValueError(f"Index not found for library: {library_id}")

        # Log some internals for debugging (entry_point, levels, vectors shape)
        try:
            entry_point = getattr(index, 'entry_point', None)
            levels = getattr(index, 'levels', None)
            vectors_shape = None
            if hasattr(index, 'vectors') and index.vectors is not None:
                vectors_shape = getattr(index, 'vectors').shape
            logger.info(f"Index internals - entry_point: {entry_point}, levels_len: {len(levels) if levels is not None else None}, vectors_shape: {vectors_shape}")
        except Exception as e:
            logger.debug(f"Could not inspect index internals: {e}")

        # Perform search
        indices, scores = index.search(search_request.query_embedding, search_request.k)
        logger.info(f"Index returned indices: {indices}, scores: {scores}")

        # Get chunks for the library
        chunks, _ = self.repository.get_all_vectors(library_id)
        
        # Map indices to chunks and apply metadata filtering
        results = []
        for i, (idx, score) in enumerate(zip(indices, scores)):
            if idx < len(chunks):
                chunk = chunks[idx]
                if search_request.metadata_filter:
                    if not self._matches_metadata_filter(chunk.metadata, search_request.metadata_filter):
                        continue

                results.append(SearchResult(chunk=chunk, score=score))
        
        logger.info(f"Search completed with {len(results)} results")
        return results
    
    def _matches_metadata_filter(self, chunk_metadata: Dict[str, Any], 
                                metadata_filter: Dict[str, Any]) -> bool:
        # Ensure chunk_metadata is a plain dict
        try:
            if not isinstance(chunk_metadata, dict) and hasattr(chunk_metadata, 'model_dump'):
                chunk_metadata = chunk_metadata.model_dump()
        except Exception:
            # Fall back to attempting to convert via __dict__
            try:
                chunk_metadata = dict(getattr(chunk_metadata, '__dict__', {}) or {})
            except Exception:
                chunk_metadata = {}

        for key, filter_value in metadata_filter.items():
            # Check if key exists in chunk metadata
            if key not in chunk_metadata:
                return False
            chunk_value = chunk_metadata[key]
            
            # For different filter types
            if isinstance(filter_value, dict):
                for op, value in filter_value.items():
                    if op == "$eq":
                        if chunk_value != value:
                            return False
                    elif op == "$ne":
                        if chunk_value == value:
                            return False
                    elif op == "$gt":
                        if not (isinstance(chunk_value, (int, float)) and 
                                isinstance(value, (int, float)) and 
                                chunk_value > value):
                            return False
                    elif op == "$gte":
                        if not (isinstance(chunk_value, (int, float)) and 
                                isinstance(value, (int, float)) and 
                                chunk_value >= value):
                            return False
                    elif op == "$lt":
                        if not (isinstance(chunk_value, (int, float)) and 
                                isinstance(value, (int, float)) and 
                                chunk_value < value):
                            return False
                    elif op == "$lte":
                        if not (isinstance(chunk_value, (int, float)) and 
                                isinstance(value, (int, float)) and 
                                chunk_value <= value):
                            return False
                    elif op == "$in":
                        if chunk_value not in value:
                            return False
                    elif op == "$nin":
                        if chunk_value in value:
                            return False
                    elif op == "$contains":
                        if not (isinstance(chunk_value, str) and 
                                isinstance(value, str) and 
                                value in chunk_value):
                            return False
                    else:
                        logger.warning(f"Unsupported filter operator: {op}")
                        return False
            else:
                if chunk_value != filter_value:
                    return False
        
        return True
    