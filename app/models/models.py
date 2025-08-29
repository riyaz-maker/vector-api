from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
import uuid

class ChunkMetadata(BaseModel):
    source: Optional[str] = None
    created_at: Optional[datetime] = None
    document_id: Optional[str] = None

class DocumentMetadata(BaseModel):
    source: Optional[str] = None
    author: Optional[str] = None
    created_at: Optional[datetime] = None

class LibraryMetadata(BaseModel):
    description: Optional[str] = None
    created_at: Optional[datetime] = None

class LibraryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    metadata: LibraryMetadata = LibraryMetadata()

class LibraryCreate(LibraryBase):
    pass

class Library(LibraryBase):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        from_attributes = True

class DocumentBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    metadata: DocumentMetadata = DocumentMetadata()

class DocumentCreate(DocumentBase):
    pass

class Document(DocumentBase):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    library_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        from_attributes = True

class ChunkBase(BaseModel):
    text: str = Field(..., min_length=1)
    embedding: Optional[List[float]] = None
    metadata: ChunkMetadata = ChunkMetadata()

class ChunkCreate(ChunkBase):
    pass

class Chunk(ChunkBase):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    library_id: str
    document_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        from_attributes = True

class SearchRequest(BaseModel):
    query_embedding: List[float]
    k: int = Field(5, ge=1, le=100)
    metadata_filter: Optional[Dict] = None

class SearchResult(BaseModel):
    chunk: Chunk
    score: float
    