import sqlite3
import os
from contextlib import contextmanager
from typing import Generator, List, Any
from app.core.config import settings
from app.core.logger import logger

class BaseRepository:
    """Base repository class with common database operations"""
    def __init__(self):
        self.initialize_database()
    
    @contextmanager
    def get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        # Extract database file path from URL
        db_path = settings.DATABASE_URL.replace("sqlite:///", "")
        db_dir = os.path.dirname(db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
            logger.info(f"Created database directory: {db_dir}")
        
        conn = sqlite3.connect(db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row   # Return rows as dictionaries
        try:
            yield conn
        finally:
            conn.close()
    
    def execute_query(self, query: str, params: tuple = ()) -> Any:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            if query.strip().upper().startswith('SELECT'):
                return cursor.fetchall()
            return cursor.lastrowid
    
    def initialize_database(self):
        logger.info("Initializing database tables")
        self.execute_query("PRAGMA foreign_keys = ON")
        
        self.execute_query("""
            CREATE TABLE IF NOT EXISTS libraries (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        self.execute_query("""
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                library_id TEXT NOT NULL,
                name TEXT NOT NULL,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (library_id) REFERENCES libraries (id) ON DELETE CASCADE
            )
        """)
        
        self.execute_query("""
            CREATE TABLE IF NOT EXISTS chunks (
                id TEXT PRIMARY KEY,
                library_id TEXT NOT NULL,
                document_id TEXT,
                text TEXT NOT NULL,
                embedding BLOB,
                metadata TEXT,
                vector_index INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (library_id) REFERENCES libraries (id) ON DELETE CASCADE,
                FOREIGN KEY (document_id) REFERENCES documents (id) ON DELETE CASCADE
            )
        """)
        
        logger.info("Database tables initialized successfully")
