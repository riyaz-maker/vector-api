# app/indexing/hnsw_index.py
import numpy as np
import random
import heapq
from typing import List, Tuple, Dict, Any, Set
from app.indexing.base_index import BaseIndex
from app.core.logger import logger

class HNSWIndex(BaseIndex):
    def __init__(self):
        super().__init__()
        self.M = 16  # No. of bidirectional links
        self.ef_construction = 200
        self.ef_search = 100
        self.mL = 1.0
        # levels is a list of dicts mapping element_id -> node info
        self.levels = []
        self.entry_point = None
    
    def build_index(self, vectors: np.ndarray, parameters: Dict[str, Any] = {}) -> bool:
        try:
            logger.info(f"Building HNSWIndex with {len(vectors)} vectors")
            if 'M' in parameters:
                self.M = parameters['M']
            if 'ef_construction' in parameters:
                self.ef_construction = parameters['ef_construction']
            if 'mL' in parameters:
                self.mL = parameters['mL']
            
            # Store vectors
            self.vectors = vectors
            
            # initialize levels as dicts (id -> node)
            self.levels = [dict() for _ in range(self._get_max_level() + 1)]
            
            self._build_hnsw(vectors)
            self.built = True
            logger.info("HNSWIndex built successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to build HNSWIndex: {str(e)}")
            return False
    
    def _get_max_level(self) -> int:
        level = int(-np.log(np.random.random()) * self.mL)
        logger.debug(f"Generated max level: {level}, type: {type(level)}")
        return level
    
    def _build_hnsw(self, vectors: np.ndarray):
        if len(vectors) == 0:
            return
        
        # Add 1st element
        first_id = 0
        first_level = self._get_max_level()
        self.entry_point = (first_id, first_level)
        for level in range(first_level + 1):
            if level >= len(self.levels):
                self.levels.append(dict())
            # store node by its element id
            self.levels[level][first_id] = {"id": first_id, "neighbors": []}
        
        # Remaining elements
        for i in range(1, len(vectors)):
            self._insert_element(i, vectors[i])
    
    def _insert_element(self, element_id: int, vector: np.ndarray):
        element_level = self._get_max_level()
        while element_level >= len(self.levels):
            self.levels.append(dict())
        
        # Start from entry point
        current_level = len(self.levels) - 1
        current_node = self.entry_point
        
        # Traverse down
        while current_level > element_level:
            # Find the nearest neighbor at current level
            nearest = self._search_level(vector, current_node[0], current_level, 1)
            if nearest:
                # nearest[0] is a (id, dist) tuple; extract the id
                current_node = (nearest[0][0], current_level)
            current_level -= 1
        for level in range(min(element_level, current_level), -1, -1):
            # Find nearest neighbors at this level
            neighbors = self._search_level(vector, current_node[0], level, self.ef_construction)
            new_element = {"id": element_id, "neighbors": []}

            # Select M nearest neighbors to connect to
            for neighbor_id, _ in neighbors[:self.M]:
                # Add bidirectional links
                new_element["neighbors"].append(neighbor_id)
                # Ensure neighbor exists at this level before appending
                if neighbor_id in self.levels[level]:
                    self.levels[level][neighbor_id]["neighbors"].append(element_id)
            # Add the new node into the level mapping
            self.levels[level][element_id] = new_element
            for neighbor_id, _ in neighbors:
                if neighbor_id in self.levels[level] and len(self.levels[level][neighbor_id]["neighbors"]) > self.M:
                    self._reduce_connections(neighbor_id, level)
    
    def _search_level(self, query: np.ndarray, entry_id: int, level: int, ef: int) -> List[Tuple[int, float]]:
        if level >= len(self.levels) or entry_id not in self.levels[level]:
            return []
        visited = set([entry_id])
        candidates = [(self.l2_distance(query, self.vectors[entry_id]), entry_id)]
        heapq.heapify(candidates)
        results = []
        
        while candidates:
            dist, candidate_id = heapq.heappop(candidates)
            if not results or dist < results[-1][1]:
                results.append((candidate_id, dist))
                results.sort(key=lambda x: x[1])
                if len(results) > ef:
                    results = results[:ef]

            for neighbor_id in self.levels[level][candidate_id]["neighbors"]:
                if neighbor_id not in visited:
                    visited.add(neighbor_id)
                    neighbor_dist = self.l2_distance(query, self.vectors[neighbor_id])
                    heapq.heappush(candidates, (neighbor_dist, neighbor_id))
        
        return [(id, dist) for id, dist in results]
    
    def _reduce_connections(self, element_id: int, level: int):
        if level >= len(self.levels) or element_id not in self.levels[level]:
            return
        element = self.levels[level][element_id]
        if len(element["neighbors"]) <= self.M:
            return
        neighbors_with_dist = []
        for neighbor_id in element["neighbors"]:
            dist = self.l2_distance(self.vectors[element_id], self.vectors[neighbor_id])
            neighbors_with_dist.append((neighbor_id, dist))
        
    # Keep only M nearest neighbors
        neighbors_with_dist.sort(key=lambda x: x[1])
        element["neighbors"] = [id for id, _ in neighbors_with_dist[:self.M]]
    
    def search(self, query_vector: List[float], k: int = 5) -> Tuple[List[int], List[float]]:
        if not self.built or self.vectors is None:
            logger.error("Index not built/no vectors")
            return [], []
        
        if len(query_vector) != self.vectors.shape[1]:
            logger.error(f"Query vector dimension {len(query_vector)} doesn't match index dimension {self.vectors.shape[1]}")
            return [], []
        
        if self.entry_point is None:
            logger.error("No entry point in HNSW index")
            return [], []
        
        # Convert query vector to numpy array
        query = np.array(query_vector)
        
        # Start from entry point
        current_level = len(self.levels) - 1
        current_node = self.entry_point
        # Traverse down to level 0
        while current_level > 0:
            # Find nearest neighbor at current level
            nearest = self._search_level(query, current_node[0], current_level, 1)
            if nearest:
                current_node = (nearest[0][0], current_level)
            current_level -= 1
        results = self._search_level(query, current_node[0], 0, self.ef_search)
        
        # Return top k results
        top_k = results[:k]
        indices = [id for id, _ in top_k]
        distances = [dist for _, dist in top_k]
        logger.debug(f"HNSWIndex search completed with {k} results")
        return indices, distances
    
    def get_index_info(self) -> Dict[str, Any]:
        info = super().get_index_info()
        info['M'] = self.M
        info['ef_construction'] = self.ef_construction
        info['ef_search'] = self.ef_search
        info['mL'] = self.mL
        info['levels'] = len(self.levels)
        info['complexity'] = {
            'build_time': 'O(N log N)',
            'query_time': 'O(log N)',
            'space': 'O(N)'
        }
        return info
    