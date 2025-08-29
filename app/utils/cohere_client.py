import cohere
from typing import List, Optional
from app.core.config import settings
from app.core.logger import logger

class CohereClient:
    """
    Client for interacting with the Cohere API to generate embeddings.
    """
    
    def __init__(self):
        self.client = None
        self.initialize_client()
    
    def initialize_client(self):
        try:
            if not settings.COHERE_API_KEY:
                logger.error("COHERE_API_KEY is not set in environment.")
                raise ValueError("COHERE_API_KEY is required but not set")
            
            self.client = cohere.Client(settings.COHERE_API_KEY)
            logger.info("Cohere client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Cohere client: {str(e)}")
            raise
    
    def get_embedding(self, text: str, model: Optional[str] = None, 
                     input_type: Optional[str] = None) -> Optional[List[float]]:
        """
        Get embedding for single text string.
        """
        if not self.client:
            logger.error("Cohere client is not initialized")
            return None
        
        model = model or settings.COHERE_MODEL
        input_type = input_type or settings.COHERE_INPUT_TYPE
        try:
            logger.debug(f"Generating embedding for text: {text[:50]}")
            response = self.client.embed(
                texts=[text],
                model=model,
                input_type=input_type
            )
            if response and hasattr(response, 'embeddings') and response.embeddings:
                logger.debug("Embedding generated successfully")
                return response.embeddings[0]
            else:
                logger.error("Failed to generate embedding: Empty response")
                return None
                
        except cohere.CohereAPIError as e:
            logger.error(f"Cohere API error: {str(e)}")
            return None
        except cohere.CohereConnectionError as e:
            logger.error(f"Cohere connection error: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error generating embedding: {str(e)}")
            return None
    
    def get_embeddings_batch(self, texts: List[str], model: Optional[str] = None,
                           input_type: Optional[str] = None) -> Optional[List[List[float]]]:
        """
        Get embeddings for a batch of text strings.
        """
        if not self.client:
            logger.error("Cohere client is not initialized")
            return None
        
        model = model or settings.COHERE_MODEL
        input_type = input_type or settings.COHERE_INPUT_TYPE
        
        if not texts:
            logger.warning("Empty text list provided for embedding")
            return []
        try:
            logger.debug(f"Generating embeddings for {len(texts)} texts")
            response = self.client.embed(
                texts=texts,
                model=model,
                input_type=input_type
            )
            if response and hasattr(response, 'embeddings') and response.embeddings:
                logger.debug(f"Successfully generated {len(response.embeddings)} embeddings")
                return response.embeddings
            else:
                logger.error("Failed to generate embeddings: Empty response")
                return None
                
        except cohere.CohereAPIError as e:
            logger.error(f"Cohere API error: {str(e)}")
            return None
        except cohere.CohereConnectionError as e:
            logger.error(f"Cohere connection error: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error generating embeddings: {str(e)}")
            return None
    
    def health_check(self) -> bool:
        if not self.client:
            return False
        try:
            self.client.embed(texts=["health check"], model=settings.COHERE_MODEL, input_type=settings.COHERE_INPUT_TYPE)
            return True
        except Exception:
            return False

cohere_client = CohereClient()
