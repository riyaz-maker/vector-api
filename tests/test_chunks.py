import pytest
from fastapi import status

def test_create_chunk(test_client, mock_cohere_client, sample_library_data, sample_document_data, sample_chunk_data):
    library_response = test_client.post("/libraries/", json=sample_library_data)
    library_id = library_response.json()["id"]
    document_response = test_client.post(f"/libraries/{library_id}/documents/", json=sample_document_data)
    document_id = document_response.json()["id"]
    response = test_client.post(
        f"/libraries/{library_id}/documents/{document_id}/chunks/", 
        json=sample_chunk_data
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["text"] == sample_chunk_data["text"]
    assert response.json()["library_id"] == library_id
    assert response.json()["document_id"] == document_id
    assert "id" in response.json()

def test_create_chunk_without_embedding(test_client, mock_cohere_client, sample_library_data, sample_document_data):
    library_response = test_client.post("/libraries/", json=sample_library_data)
    library_id = library_response.json()["id"]
    document_response = test_client.post(f"/libraries/{library_id}/documents/", json=sample_document_data)
    document_id = document_response.json()["id"]
    chunk_data = {
        "text": "Test chunk without embedding",
        "metadata": {
            "source": "test",
            "page": 1
        }
    }
    response = test_client.post(
        f"/libraries/{library_id}/documents/{document_id}/chunks/", 
        json=chunk_data
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["text"] == chunk_data["text"]
    assert response.json()["embedding"] is not None

def test_get_chunks_by_document(test_client, mock_cohere_client, sample_library_data, sample_document_data, sample_chunk_data):
    library_response = test_client.post("/libraries/", json=sample_library_data)
    library_id = library_response.json()["id"]
    document_response = test_client.post(f"/libraries/{library_id}/documents/", json=sample_document_data)
    document_id = document_response.json()["id"]
    test_client.post(
        f"/libraries/{library_id}/documents/{document_id}/chunks/", 
        json=sample_chunk_data
    )
    response = test_client.get(f"/libraries/{library_id}/documents/{document_id}/chunks/")
    
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)
    assert len(response.json()) == 1
    assert response.json()[0]["text"] == sample_chunk_data["text"]

def test_get_chunk(test_client, mock_cohere_client, sample_library_data, sample_document_data, sample_chunk_data):
    library_response = test_client.post("/libraries/", json=sample_library_data)
    library_id = library_response.json()["id"]
    document_response = test_client.post(f"/libraries/{library_id}/documents/", json=sample_document_data)
    document_id = document_response.json()["id"]
    chunk_response = test_client.post(
        f"/libraries/{library_id}/documents/{document_id}/chunks/", 
        json=sample_chunk_data
    )
    chunk_id = chunk_response.json()["id"]
    response = test_client.get(f"/libraries/{library_id}/documents/{document_id}/chunks/{chunk_id}")
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == chunk_id
    assert response.json()["text"] == sample_chunk_data["text"]

def test_update_chunk(test_client, mock_cohere_client, sample_library_data, sample_document_data, sample_chunk_data):
    library_response = test_client.post("/libraries/", json=sample_library_data)
    library_id = library_response.json()["id"]
    document_response = test_client.post(f"/libraries/{library_id}/documents/", json=sample_document_data)
    document_id = document_response.json()["id"]
    chunk_response = test_client.post(
        f"/libraries/{library_id}/documents/{document_id}/chunks/", 
        json=sample_chunk_data
    )
    chunk_id = chunk_response.json()["id"]
    update_data = {
        "text": "Updated chunk text",
        "embedding": [0.6, 0.7, 0.8, 0.9, 1.0] * 64,
        "metadata": {
            "source": "updated",
            "page": 2
        }
    }
    response = test_client.put(
        f"/libraries/{library_id}/documents/{document_id}/chunks/{chunk_id}", 
        json=update_data
    )
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["text"] == update_data["text"]
    assert response.json()["metadata"]["page"] == update_data["metadata"]["page"]

def test_delete_chunk(test_client, mock_cohere_client, sample_library_data, sample_document_data, sample_chunk_data):
    library_response = test_client.post("/libraries/", json=sample_library_data)
    library_id = library_response.json()["id"]
    document_response = test_client.post(f"/libraries/{library_id}/documents/", json=sample_document_data)
    document_id = document_response.json()["id"]
    chunk_response = test_client.post(
        f"/libraries/{library_id}/documents/{document_id}/chunks/", 
        json=sample_chunk_data
    )
    chunk_id = chunk_response.json()["id"]
    response = test_client.delete(f"/libraries/{library_id}/documents/{document_id}/chunks/{chunk_id}")
    
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # Verification
    get_response = test_client.get(f"/libraries/{library_id}/documents/{document_id}/chunks/{chunk_id}")
    assert get_response.status_code == status.HTTP_404_NOT_FOUND
