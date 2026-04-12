import pytest
from starlette.testclient import TestClient


@pytest.mark.timeout(300)
def test_create_dog_success(api_client: TestClient):
    # check that only some data is exposed in the public endpoint
    first_dogs_response = api_client.post("/dogs", json={
        "name": "Mr Waffles",
        "start_latitude": 48.2,
        "start_longitude": 16.3
    })

    assert first_dogs_response.status_code == 201
    first_dogs_data = first_dogs_response.json()
    for key in [
        "dog_id",
        
    ]:
        assert key in first_dogs_data
    for key in [
        "name",
        "device_id",
        "start_latitude",
        "start_longitude",
        "is_active",
        "created_at"
    ]:
        assert key not in first_dogs_data

    # check testers can get the complete data
    second_dogs_response = api_client.post("/internal/dogs", json={
        "name": "Butter Cup",
        "start_latitude": 48.2,
        "start_longitude": 16.3
    })

    assert second_dogs_response.status_code == 201
    second_dogs_data = second_dogs_response.json()
    for key in [
        "dog_id",
        "device_id",
        "name",
        "start_latitude",
        "start_longitude",
        "is_active",
        "created_at"
    ]:
        assert key in second_dogs_data

    # check that both enpoints are logging correctly
    list_dogs_response = api_client.get("/internal/dogs")
    list_dogs_data = list_dogs_response.json()
    assert len(list_dogs_data) == 2



@pytest.mark.timeout(300)
def test_create_dog_invalid_latitude(api_client: TestClient):
    response = api_client.post("/internal/dogs", json={
        "name": "Mr Waffles",
        "start_latitude": 300,
        "start_longitude": 16.3
    })

    assert response.status_code == 400
    data = response.json()

    # check that invalid response is not logged
    response = api_client.get("/internal/dogs")
    data = response.json()
    assert len(data) == 0
    