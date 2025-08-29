import numpy as np
from typing import List, Tuple, Dict, Any
from app.indexing.base_index import BaseIndex
from app.core.logger import logger

class FlatIndex(BaseIndex):
    """
    Brute force index that calculates distances to all vectors.
    """
    def __init__(self):
        super().__init__()
        self.distance_metric = 'l2'
    
    def build_index(self, vectors: np.ndarray, parameters: Dict[str, Any] = {}) -> bool:
        try:
            logger.info(f"Building FlatIndex with {len(vectors)} vectors")
            if 'distance_metric' in parameters:
                self.distance_metric = parameters['distance_metric']
            self.vectors = vectors
            self.built = True
            logger.info("FlatIndex built successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to build FlatIndex: {str(e)}")
            return False
    
    def search(self, query_vector: List[float], k: int = 5) -> Tuple[List[int], List[float]]:
        if not self.built or self.vectors is None:
            logger.error("Index not built or no vectors available")
            return [], []
        
        if len(query_vector) != self.vectors.shape[1]:
            logger.error(f"Query vector dimension {len(query_vector)} doesn't match index dimension {self.vectors.shape[1]}")
            return [], []
        
        # Convert query vector to numpy array
        query = np.array(query_vector)
        distances = []
        for i, vector in enumerate(self.vectors):
            if self.distance_metric == 'cosine':
                # Convert cosine similarity to distance (1 - similarity)
                similarity = self.cosine_similarity(query, vector)
                distance = 1 - similarity
            elif self.distance_metric == 'euclidean':
                distance = self.euclidean_distance(query, vector)
            else:
                distance = self.l2_distance(query, vector)
            distances.append((i, distance))
        
        distances.sort(key=lambda x: x[1])
        top_k = distances[:k]
        indices = [idx for idx, _ in top_k]
        distances = [dist for _, dist in top_k]
        logger.debug(f"FlatIndex search completed with {k} results")
        return indices, distances
    
    def get_index_info(self) -> Dict[str, Any]:
        info = super().get_index_info()
        info['distance_metric'] = self.distance_metric
        info['complexity'] = {
            'build_time': 'O(1)',
            'query_time': 'O(N)',
            'space': 'O(N)'
        }
        return info
    