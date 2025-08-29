import numpy as np
import pickle
from abc import ABC, abstractmethod
from typing import List, Optional, Tuple, Dict, Any
from app.core.logger import logger

class BaseIndex(ABC):
    """Abstract base class for both indexing algorithms"""
    def __init__(self):
        self.index = None
        self.vectors = None
        self.built = False
    
    @abstractmethod
    def build_index(self, vectors: np.ndarray, parameters: Dict[str, Any] = {}) -> bool:
        """
        Build the index from the given vectors.
        """
        pass
    
    @abstractmethod
    def search(self, query_vector: List[float], k: int = 5) -> Tuple[List[int], List[float]]:
        """
        Search for the k nearest neighbors of the query vector.
        """
        pass
    
    def save_index(self, file_path: str) -> bool:
        try:
            with open(file_path, 'wb') as f:
                pickle.dump({
                    'index': self.index,
                    'vectors': self.vectors,
                    'built': self.built
                }, f)
            logger.info(f"Index saved to {file_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save index: {str(e)}")
            return False
    
    def load_index(self, file_path: str) -> bool:
        try:
            with open(file_path, 'rb') as f:
                data = pickle.load(f)
                self.index = data['index']
                self.vectors = data['vectors']
                self.built = data['built']
            logger.info(f"Index loaded from {file_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to load index: {str(e)}")
            return False
    
    def get_index_info(self) -> Dict[str, Any]:
        return {
            'type': self.__class__.__name__,
            'built': self.built,
            'vector_count': len(self.vectors) if self.vectors is not None else 0,
            'dimensions': self.vectors.shape[1] if self.vectors is not None else 0
        }
    
    @staticmethod
    def cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        return dot_product / (norm1 * norm2)
    
    @staticmethod
    def euclidean_distance(vec1: np.ndarray, vec2: np.ndarray) -> float:
        return np.linalg.norm(vec1 - vec2)
    
    @staticmethod
    def l2_distance(vec1: np.ndarray, vec2: np.ndarray) -> float:
        return np.sqrt(np.sum((vec1 - vec2) ** 2))
    