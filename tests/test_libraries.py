import pytest
from unittest.mock import patch, MagicMock
from fastapi import status

def test_create_library(test_client, mock_cohere_client, sample_library_data):
    response = test_client.post("/libraries/", json=sample_library_data)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["name"] == sample_library_data["name"]
    assert "id" in response.json()

def test_get_all_libraries(test_client, mock_cohere_client):
    response = test_client.get("/libraries/")
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)

def test_get_library(test_client, mock_cohere_client, sample_library_data):
    create_response = test_client.post("/libraries/", json=sample_library_data)
    library_id = create_response.json()["id"]
    response = test_client.get(f"/libraries/{library_id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == library_id
    assert response.json()["name"] == sample_library_data["name"]

def test_get_nonexistent_library(test_client, mock_cohere_client):
    response = test_client.get("/libraries/nonexistent-id")
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_update_library(test_client, mock_cohere_client, sample_library_data):
    create_response = test_client.post("/libraries/", json=sample_library_data)
    library_id = create_response.json()["id"]
    update_data = {
        "name": "Updated Library Name",
        "metadata": {
            "description": "Updated description",
            "category": "updated"
        }
    }
    response = test_client.put(f"/libraries/{library_id}", json=update_data)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["name"] == update_data["name"]
    assert response.json()["metadata"]["description"] == update_data["metadata"]["description"]

def test_delete_library(test_client, mock_cohere_client, sample_library_data):
    create_response = test_client.post("/libraries/", json=sample_library_data)
    library_id = create_response.json()["id"]
    response = test_client.delete(f"/libraries/{library_id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    get_response = test_client.get(f"/libraries/{library_id}")
    assert get_response.status_code == status.HTTP_404_NOT_FOUND
