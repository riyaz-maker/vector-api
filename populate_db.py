# Code written to populate DB with some test data - Used Cursor for this file.

import sys
import os
import asyncio
from typing import List, Dict, Any

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.library_service import LibraryService
from app.services.document_service import DocumentService
from app.services.chunk_service import ChunkService
from app.services.indexing_service import IndexingService
from app.models.models import LibraryCreate, DocumentCreate, ChunkCreate
from app.core.logger import logger

# Sample data
SAMPLE_LIBRARY = {
    "name": "Machine Learning Research Papers",
    "metadata": {
        "description": "A collection of machine learning research paper excerpts",
        "category": "academic"
    }
}

SAMPLE_DOCUMENTS = [
    {
        "name": "Attention Is All You Need",
        "metadata": {
            "source": "arXiv",
            "authors": "Vaswani et al.",
            "year": 2017
        }
    },
    {
        "name": "BERT: Pre-training of Deep Bidirectional Transformers",
        "metadata": {
            "source": "arXiv",
            "authors": "Devlin et al.",
            "year": 2018
        }
    }
]

SAMPLE_CHUNKS = {
    "Attention Is All You Need": [
        {
            "text": "The dominant sequence transduction models are based on complex recurrent or convolutional neural networks that include an encoder and a decoder. The best performing models also connect the encoder and decoder through an attention mechanism.",
            "metadata": {
                "section": "abstract",
                "page": 1
            }
        },
        {
            "text": "We propose a new simple network architecture, the Transformer, based solely on attention mechanisms, dispensing with recurrence and convolutions entirely.",
            "metadata": {
                "section": "abstract",
                "page": 1
            }
        },
        {
            "text": "Experiments on two machine translation tasks show these models to be superior in quality while being more parallelizable and requiring significantly less time to train.",
            "metadata": {
                "section": "abstract",
                "page": 1
            }
        }
    ],
    "BERT: Pre-training of Deep Bidirectional Transformers": [
        {
            "text": "We introduce a new language representation model called BERT, which stands for Bidirectional Encoder Representations from Transformers.",
            "metadata": {
                "section": "abstract",
                "page": 1
            }
        },
        {
            "text": "Unlike recent language representation models, BERT is designed to pre-train deep bidirectional representations from unlabeled text by jointly conditioning on both left and right context in all layers.",
            "metadata": {
                "section": "abstract",
                "page": 1
            }
        },
        {
            "text": "BERT advances the state of the art for eleven NLP tasks, including pushing the GLUE score to 80.5% (7.7% point absolute improvement), MultiNLI accuracy to 86.7% (4.6% absolute improvement), and SQuAD v1.1 question answering Test F1 to 93.2 (1.5 point absolute improvement).",
            "metadata": {
                "section": "abstract",
                "page": 1
            }
        }
    ]
}

async def populate_database():
    logger.info("Starting database population...")
    
    try:
        # Initialize services
        library_service = LibraryService()
        document_service = DocumentService()
        chunk_service = ChunkService()
        indexing_service = IndexingService()
        
        # 1. Create a library
        logger.info("Creating library...")
        library = library_service.create_library(LibraryCreate(**SAMPLE_LIBRARY))
        library_id = library.id
        logger.info(f"Created library with ID: {library_id}")
        
        # 2. Create documents
        documents = {}
        for doc_data in SAMPLE_DOCUMENTS:
            logger.info(f"Creating document: {doc_data['name']}")
            document = document_service.create_document(
                library_id, 
                DocumentCreate(**doc_data)
            )
            if document:
                documents[doc_data["name"]] = document.id
                logger.info(f"Created document with ID: {document.id}")
            else:
                logger.error(f"Failed to create document: {doc_data['name']}")
                return False
        
        # 3. Create chunks with embeddings
        for doc_name, chunks_data in SAMPLE_CHUNKS.items():
            document_id = documents[doc_name]
            logger.info(f"Creating chunks for document: {doc_name}")
            
            for i, chunk_data in enumerate(chunks_data):
                logger.info(f"Creating chunk {i+1} for {doc_name}")
                chunk = chunk_service.create_chunk(
                    library_id,
                    document_id,
                    ChunkCreate(**chunk_data)
                )
                if chunk:
                    logger.info(f"Created chunk with ID: {chunk.id}")
                else:
                    logger.error(f"Failed to create chunk {i+1} for {doc_name}")
                    return False
        
        # 4. Build index
        logger.info("Building index...")
        success = indexing_service.build_index(
            library_id, 
            "HNSW", 
            {"M": 16, "ef_construction": 200}
        )
        
        if success:
            logger.info("Index built successfully!")
        else:
            logger.error("Failed to build index")
            return False
        
        logger.info("Database population completed successfully!")
        
        # Print summary
        print("\n" + "="*50)
        print("DATABASE POPULATION SUMMARY")
        print("="*50)
        print(f"Library: {SAMPLE_LIBRARY['name']} (ID: {library_id})")
        print(f"Documents created: {len(documents)}")
        total_chunks = sum(len(chunks) for chunks in SAMPLE_CHUNKS.values())
        print(f"Chunks created: {total_chunks}")
        print(f"Index built: {'Yes' if success else 'No'}")
        print("="*50)
        return True
        
    except Exception as e:
        logger.error(f"Error populating database: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(populate_database())
    sys.exit(0 if success else 1)