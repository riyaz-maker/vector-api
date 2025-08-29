import pytest
from fastapi import status

def test_create_document(test_client, mock_cohere_client, sample_library_data, sample_document_data):
    library_response = test_client.post("/libraries/", json=sample_library_data)
    library_id = library_response.json()["id"]
    response = test_client.post(f"/libraries/{library_id}/documents/", json=sample_document_data)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["name"] == sample_document_data["name"]
    assert response.json()["library_id"] == library_id
    assert "id" in response.json()

def test_get_documents_by_library(test_client, mock_cohere_client, sample_library_data, sample_document_data):
    library_response = test_client.post("/libraries/", json=sample_library_data)
    library_id = library_response.json()["id"]
    test_client.post(f"/libraries/{library_id}/documents/", json=sample_document_data)
    response = test_client.get(f"/libraries/{library_id}/documents/")
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == sample_document_data["name"]

def test_get_document(test_client, mock_cohere_client, sample_library_data, sample_document_data):
    library_response = test_client.post("/libraries/", json=sample_library_data)
    library_id = library_response.json()["id"]
    document_response = test_client.post(f"/libraries/{library_id}/documents/", json=sample_document_data)
    document_id = document_response.json()["id"]
    response = test_client.get(f"/libraries/{library_id}/documents/{document_id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == document_id
    assert response.json()["name"] == sample_document_data["name"]

def test_update_document(test_client, mock_cohere_client, sample_library_data, sample_document_data):
    library_response = test_client.post("/libraries/", json=sample_library_data)
    library_id = library_response.json()["id"]
    document_response = test_client.post(f"/libraries/{library_id}/documents/", json=sample_document_data)
    document_id = document_response.json()["id"]
    update_data = {
        "name": "Updated Document Name",
        "metadata": {
            "source": "updated",
            "author": "updated_tester"
        }
    }
    response = test_client.put(f"/libraries/{library_id}/documents/{document_id}", json=update_data)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["name"] == update_data["name"]
    assert response.json()["metadata"]["source"] == update_data["metadata"]["source"]

def test_delete_document(test_client, mock_cohere_client, sample_library_data, sample_document_data):
    library_response = test_client.post("/libraries/", json=sample_library_data)
    library_id = library_response.json()["id"]
    document_response = test_client.post(f"/libraries/{library_id}/documents/", json=sample_document_data)
    document_id = document_response.json()["id"]
    response = test_client.delete(f"/libraries/{library_id}/documents/{document_id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # Verification
    get_response = test_client.get(f"/libraries/{library_id}/documents/{document_id}")
    assert get_response.status_code == status.HTTP_404_NOT_FOUND
