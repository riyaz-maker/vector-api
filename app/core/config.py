from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional

class Settings(BaseSettings):
    COHERE_API_KEY: str = Field(..., description="Cohere API key for generating embeddings")
    DATABASE_URL: str = Field("sqlite:///./vector_db.sqlite", description="Database connection string")
    LOG_LEVEL: str = Field("INFO", description="Logging level")
    COHERE_MODEL: str = Field("embed-english-v3.0", description="Cohere model to use for embeddings")
    COHERE_INPUT_TYPE: str = Field("search_document", description="Cohere input type for embeddings")
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
