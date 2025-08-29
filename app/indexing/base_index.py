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
                # Persist full index state
                state = {
                    'index': self.index,
                    'vectors': self.vectors,
                    'built': self.built
                }
                # If index implementation exposes extra attributes, include them
                if hasattr(self, 'levels'):
                    state['levels'] = getattr(self, 'levels')
                if hasattr(self, 'entry_point'):
                    state['entry_point'] = getattr(self, 'entry_point')
                if hasattr(self, 'M'):
                    state['M'] = getattr(self, 'M')
                if hasattr(self, 'ef_construction'):
                    state['ef_construction'] = getattr(self, 'ef_construction')
                if hasattr(self, 'ef_search'):
                    state['ef_search'] = getattr(self, 'ef_search')
                pickle.dump(state, f)
            logger.info(f"Index saved to {file_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save index: {str(e)}")
            return False
    
    def load_index(self, file_path: str) -> bool:
        try:
            with open(file_path, 'rb') as f:
                data = pickle.load(f)
                # Load common fields
                self.index = data.get('index')
                self.vectors = data.get('vectors')
                self.built = data.get('built', False)
                # Load optional implementation specific fields if present
                if 'levels' in data:
                    setattr(self, 'levels', data.get('levels'))
                if 'entry_point' in data:
                    setattr(self, 'entry_point', data.get('entry_point'))
                if 'M' in data:
                    setattr(self, 'M', data.get('M'))
                if 'ef_construction' in data:
                    setattr(self, 'ef_construction', data.get('ef_construction'))
                if 'ef_search' in data:
                    setattr(self, 'ef_search', data.get('ef_search'))
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
    