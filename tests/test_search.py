import pytest
from fastapi import status

def test_search(test_client, mock_cohere_client, sample_library_data, sample_document_data, sample_chunk_data, sample_search_data):
    library_response = test_client.post("/libraries/", json=sample_library_data)
    library_id = library_response.json()["id"]
    document_response = test_client.post(f"/libraries/{library_id}/documents/", json=sample_document_data)
    document_id = document_response.json()["id"]
    test_client.post(
        f"/libraries/{library_id}/documents/{document_id}/chunks/", 
        json=sample_chunk_data
    )
    index_params = {
        "index_type": "HNSW",
        "parameters": {
            "M": 16,
            "ef_construction": 200
        }
    }
    test_client.post(f"/libraries/{library_id}/index/", json=index_params)
    response = test_client.post(f"/libraries/{library_id}/search/", json=sample_search_data)

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0
    assert "chunk" in response.json()[0]
    assert "score" in response.json()[0]

def test_search_with_metadata_filter(test_client, mock_cohere_client, sample_library_data, sample_document_data, sample_chunk_data, sample_search_data):
    library_response = test_client.post("/libraries/", json=sample_library_data)
    library_id = library_response.json()["id"]
    document_response = test_client.post(f"/libraries/{library_id}/documents/", json=sample_document_data)
    document_id = document_response.json()["id"]
    test_client.post(
        f"/libraries/{library_id}/documents/{document_id}/chunks/", 
        json=sample_chunk_data
    )
    index_params = {
        "index_type": "HNSW",
        "parameters": {
            "M": 16,
            "ef_construction": 200
        }
    }
    test_client.post(f"/libraries/{library_id}/index/", json=index_params)
    
    # Search with metadata filter
    search_data_with_filter = {
        "query_embedding": [0.1, 0.2, 0.3, 0.4, 0.5] * 64,
        "k": 5,
        "metadata_filter": {
            "source": "test"
        }
    }
    response = test_client.post(f"/libraries/{library_id}/search/", json=search_data_with_filter)
    
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)

def test_search_without_index(test_client, mock_cohere_client, sample_library_data):
    library_response = test_client.post("/libraries/", json=sample_library_data)
    library_id = library_response.json()["id"]
    search_data = {
        "query_embedding": [0.1, 0.2, 0.3, 0.4, 0.5] * 64,
        "k": 5,
        "metadata_filter": {}
    }
    response = test_client.post(f"/libraries/{library_id}/search/", json=search_data)
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
