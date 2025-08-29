import json
from typing import List, Optional
from app.repositories import BaseRepository
from app.models.models import Library, LibraryCreate
from app.core.logger import logger

class LibraryRepository(BaseRepository):
    def create_library(self, library: LibraryCreate) -> Library:
        logger.info(f"Creating library: {library.name}")
        library_obj = Library(**library.model_dump())
        
        # Insert into database
        self.execute_query(
            "INSERT INTO libraries (id, name, metadata, created_at) VALUES (?, ?, ?, ?)",
            (library_obj.id, library_obj.name, json.dumps(library_obj.metadata.model_dump()), library_obj.created_at)
        )
        logger.info(f"Library created with ID: {library_obj.id}")
        return library_obj
    
    def get_library(self, library_id: str) -> Optional[Library]:
        logger.info(f"Getting library: {library_id}")
        result = self.execute_query(
            "SELECT * FROM libraries WHERE id = ?",
            (library_id,)
        )
        if not result:
            logger.warning(f"Library not found: {library_id}")
            return None
        row = result[0]
        
        # Convert metadata from JSON string back to dict
        metadata = json.loads(row["metadata"]) if row["metadata"] else {}
        return Library(
            id=row["id"],
            name=row["name"],
            metadata=metadata,
            created_at=row["created_at"]
        )
    def get_all_libraries(self) -> List[Library]:
        logger.info("Getting all libraries")
        result = self.execute_query("SELECT * FROM libraries")
        libraries = []
        for row in result:
            metadata = json.loads(row["metadata"]) if row["metadata"] else {}
            libraries.append(Library(
                id=row["id"],
                name=row["name"],
                metadata=metadata,
                created_at=row["created_at"]
            ))
        return libraries
    
    def update_library(self, library_id: str, library: LibraryCreate) -> Optional[Library]:
        logger.info(f"Updating library: {library_id}")
        existing_library = self.get_library(library_id)
        if not existing_library:
            return None
        self.execute_query(
            "UPDATE libraries SET name = ?, metadata = ? WHERE id = ?",
            (library.name, json.dumps(library.metadata.model_dump()), library_id)
        )
        return self.get_library(library_id)
    
    def delete_library(self, library_id: str) -> bool:
        logger.info(f"Deleting library: {library_id}")
        existing_library = self.get_library(library_id)
        if not existing_library:
            return False
        self.execute_query("DELETE FROM libraries WHERE id = ?", (library_id,))
        logger.info(f"Library deleted: {library_id}")
        return True
    