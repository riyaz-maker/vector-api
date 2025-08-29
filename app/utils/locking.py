import threading
from typing import Dict
from app.core.logger import logger

class LockManager:
    """
    Thread safe lock manager for per-library concurrency.
    """
    def __init__(self):
        self.locks: Dict[str, threading.RLock] = {}
        self._global_lock = threading.RLock()
        
    def get_lock(self, library_id: str) -> threading.RLock:
        with self._global_lock:
            if library_id not in self.locks:
                logger.debug(f"Creating new lock for library: {library_id}")
                self.locks[library_id] = threading.RLock()
            return self.locks[library_id]
    
    def acquire_lock(self, library_id: str, blocking: bool = True, timeout: float = -1) -> bool:
        lock = self.get_lock(library_id)
        logger.debug(f"Trying to acquire lock for library: {library_id}")
        
        if blocking and timeout == -1:
            lock.acquire()
            logger.debug(f"Lock acquired for library: {library_id}")
            return True
        else:
            acquired = lock.acquire(blocking=blocking, timeout=timeout)
            if acquired:
                logger.debug(f"Lock acquired for library: {library_id}")
            else:
                logger.warning(f"Failed to acquire lock for library: {library_id}")
            return acquired
    
    def release_lock(self, library_id: str):
        with self._global_lock:
            if library_id in self.locks:
                try:
                    self.locks[library_id].release()
                    logger.debug(f"Lock released for library: {library_id}")
                except RuntimeError:
                    logger.warning(f"Trying to release unlocked lock for library: {library_id}")
    
    def remove_lock(self, library_id: str):
        with self._global_lock:
            if library_id in self.locks:
                del self.locks[library_id]
                logger.debug(f"Lock removed for library: {library_id}")

lock_manager = LockManager()
