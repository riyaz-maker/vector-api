import pytest
from fastapi import status

def test_build_index(test_client, mock_cohere_client, sample_library_data, sample_document_data, sample_chunk_data):
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
    response = test_client.post(f"/libraries/{library_id}/index/", json=index_params)
    
    assert response.status_code == status.HTTP_202_ACCEPTED
    assert "message" in response.json()
    assert "indexing started" in response.json()["message"].lower()

def test_get_index_info(test_client, mock_cohere_client, sample_library_data, sample_document_data, sample_chunk_data):
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
    response = test_client.get(f"/libraries/{library_id}/index/")
    
    assert response.status_code == status.HTTP_200_OK
    assert "type" in response.json()
    assert "built" in response.json()
    assert "vector_count" in response.json()
