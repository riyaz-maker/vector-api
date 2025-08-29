# Code written to verfiy if the sample data is populated correctly. Used Cursor for this file.

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.repositories.library_repository import LibraryRepository
from app.repositories.document_repository import DocumentRepository
from app.repositories.chunk_repository import ChunkRepository
import numpy as np

def verify_data():
    """Verify that data was properly added to the database"""
    print("Verifying database content...")
    
    # Initialize repositories
    library_repo = LibraryRepository()
    document_repo = DocumentRepository()
    chunk_repo = ChunkRepository()
    
    # 1. Check libraries
    libraries = library_repo.get_all_libraries()
    print(f"Libraries found: {len(libraries)}")
    
    for library in libraries:
        print(f"  - {library.name} (ID: {library.id})")
        
        # 2. Check documents in this library
        documents = document_repo.get_documents_by_library(library.id)
        print(f"  Documents in library: {len(documents)}")
        
        for document in documents:
            print(f"    - {document.name} (ID: {document.id})")
            
            # 3. Check chunks in this document
            chunks = chunk_repo.get_chunks_by_document(library.id, document.id)
            print(f"    Chunks in document: {len(chunks)}")
            
            for chunk in chunks:
                has_embedding = chunk.embedding is not None
                print(f"      - Chunk ID: {chunk.id}, Has embedding: {has_embedding}")
                if has_embedding:
                    print(f"        Embedding length: {len(chunk.embedding)}")
    
    # 4. Check vector files
    print("\nChecking vector files...")
    data_dir = "data"
    if os.path.exists(data_dir):
        for file in os.listdir(data_dir):
            if file.startswith("vectors_") and file.endswith(".npy"):
                file_path = os.path.join(data_dir, file)
                try:
                    vectors = np.load(file_path, allow_pickle=True)
                    print(f"  {file}: {len(vectors)} vectors")
                except:
                    print(f"  {file}: Could not load")
    
    # 5. Check index files
    print("\nChecking index files...")
    if os.path.exists(data_dir):
        for file in os.listdir(data_dir):
            if file.startswith("index_") and file.endswith(".pkl"):
                file_path = os.path.join(data_dir, file)
                file_size = os.path.getsize(file_path)
                print(f"  {file}: {file_size} bytes")

if __name__ == "__main__":
    verify_data()