from typing import List, Optional
from app.repositories.library_repository import LibraryRepository
from app.models.models import Library, LibraryCreate
from app.core.logger import logger

class LibraryService:
    def __init__(self):
        self.repository = LibraryRepository()
    
    def create_library(self, library_data: LibraryCreate) -> Library:
        logger.info(f"Creating library: {library_data.name}")
        if not library_data.name or not library_data.name.strip():
            logger.error("Library name cannot be empty")
            raise ValueError("Library name cannot be empty")
        
        library = self.repository.create_library(library_data)
        logger.info(f"Library created successfully: {library.id}")
        return library
    
    def get_library(self, library_id: str) -> Optional[Library]:
        logger.info(f"Getting library: {library_id}")
        if not library_id or not library_id.strip():
            logger.error("Library ID cannot be empty")
            raise ValueError("Library ID cannot be empty")
        
        library = self.repository.get_library(library_id)
        if not library:
            logger.warning(f"Library not found: {library_id}")
            return None
        logger.info(f"Library retrieved successfully: {library_id}")
        return library
    
    def get_all_libraries(self) -> List[Library]:
        logger.info("Getting all libraries")
        libraries = self.repository.get_all_libraries()
        logger.info(f"Retrieved {len(libraries)} libraries")
        return libraries
    
    def update_library(self, library_id: str, library_data: LibraryCreate) -> Optional[Library]:
        logger.info(f"Updating library: {library_id}")
        if not library_id or not library_id.strip():
            logger.error("Library ID cannot be empty")
            raise ValueError("Library ID cannot be empty")
        
        if not library_data.name or not library_data.name.strip():
            logger.error("Library name cannot be empty")
            raise ValueError("Library name cannot be empty")
        existing_library = self.repository.get_library(library_id)
        if not existing_library:
            logger.warning(f"Library not found: {library_id}")
            return None
        library = self.repository.update_library(library_id, library_data)
        logger.info(f"Library updated successfully: {library_id}")
        return library
    
    def delete_library(self, library_id: str) -> bool:
        logger.info(f"Deleting library: {library_id}")
        if not library_id or not library_id.strip():
            logger.error("Library ID cannot be empty")
            raise ValueError("Library ID cannot be empty")
        existing_library = self.repository.get_library(library_id)
        if not existing_library:
            logger.warning(f"Library not found: {library_id}")
            return False
        
        success = self.repository.delete_library(library_id)
        if success:
            logger.info(f"Library deleted successfully: {library_id}")
        else:
            logger.error(f"Failed to delete library: {library_id}")
        
        return success
    