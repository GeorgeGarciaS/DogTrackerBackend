from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from src.enums import TelemetryIssueType, TelemetryStatus


@pytest.mark.timeout(300)
def test_ingest_telemetry_success(api_client: TestClient):
    # create dog first
    dog_response = api_client.post("/internal/dogs", json={
        "name": "Mr Waffles",
        "start_latitude": 51.5,
        "start_longitude": 16.3
    })
    assert dog_response.status_code == 201
    dog_id = dog_response.json()["dog_id"]

    telemetry_response = api_client.post("/telemetry", json={
        "dog_id": dog_id,
        "event_ts": str(datetime.now()),
        "latitude": 51.5001,
        "longitude": 16.3001,
        "cumulative_steps": 120,
        "heart_rate": 88,
        "battery": 95,
        "signal_strength": 67
    })

    assert telemetry_response.status_code == 200
    telemetry_data = telemetry_response.json()
    assert "event_id" in telemetry_data
    assert telemetry_data["status"] == TelemetryStatus.ACCEPTED.value
    assert telemetry_data["detail"] == ""

@pytest.mark.timeout(300)
def test_ingest_telemetry_invalid_dog_id(api_client: TestClient):
    telemetry_response = api_client.post("/telemetry", json={
        "dog_id": "111aaa",
        "event_ts": str(datetime.now()),
        "latitude": 51.5001,
        "longitude": 16.3001,
        "cumulative_steps": 120,
        "heart_rate": 88,
        "battery": 95,
        "signal_strength": 67
    })

    assert telemetry_response.status_code == 400

@pytest.mark.timeout(300)
def test_ingest_telemetry_invalid_heart_rate_and_battery(api_client: TestClient):
    # create dog first
    dog_response = api_client.post("/internal/dogs", json={
        "name": "Mr Waffles",
        "start_latitude": 51.5,
        "start_longitude": 16.3
    })
    assert dog_response.status_code == 201
    dog_id = dog_response.json()["dog_id"]

    telemetry_response = api_client.post("/telemetry", json={
        "dog_id": dog_id,
        "event_ts": str(datetime.now()),
        "latitude": 51.5001,
        "longitude": 16.3001,
        "cumulative_steps": 120,
        "heart_rate": -5,
        "battery": 300,
        "signal_strength": 67
    })

    assert telemetry_response.status_code == 200
    telemetry_data = telemetry_response.json()
    event_id = telemetry_data['event_id']
    assert event_id != ""
    assert telemetry_data["status"] == TelemetryStatus.REJECTED.value
    assert TelemetryIssueType.BATTERY_OUT_OF_RANGE.value in telemetry_data["detail"]
    assert TelemetryIssueType.HEART_RATE_INVALID.value in telemetry_data["detail"]

    # check telemetry was logged in data quality issues
    data_quality_issue_response = api_client.get(
        f"/internal/data_quality_issues/{event_id}"
    )

    list_data_quality_issue_data = data_quality_issue_response.json()
    assert len(list_data_quality_issue_data) == 2
    for data_quality_issue_data in list_data_quality_issue_data:
        assert "issue_id" in data_quality_issue_data
        assert dog_id == data_quality_issue_data["dog_id"]
        assert event_id == data_quality_issue_data["event_id"]



@pytest.mark.timeout(300)
def test_ingest_telemetry_shows_in_dog_current_status(api_client: TestClient):
    # create dog first
    dog_response = api_client.post("/internal/dogs", json={
        "name": "Mr Waffles",
        "start_latitude": 51.5,
        "start_longitude": 16.3
    })
    assert dog_response.status_code == 201
    dog_id = dog_response.json()["dog_id"]

    # ingest valid telemetry
    telemetry_response = api_client.post("/telemetry", json={
        "dog_id": dog_id,
        "event_ts": str(datetime.now()),
        "latitude": 51.5001,
        "longitude": 16.3001,
        "cumulative_steps": 120,
        "heart_rate": 88,
        "battery": 95,
        "signal_strength": 67
    })

    assert telemetry_response.status_code == 200
    telemetry_data = telemetry_response.json()
    event_id = telemetry_data['event_id']
    assert telemetry_data["status"] == TelemetryStatus.ACCEPTED.value

    # check telemetry was recorded on dog status
    dog_current_status_response = api_client.get(
        f"/dogs/{dog_id}/status"
    )
    dog_current_status_data = dog_current_status_response.json()
    assert dog_current_status_data["last_event_id"] == event_id
    assert dog_current_status_data["dog_id"] == dog_id

@pytest.mark.timeout(300)
def test_invalid_ingest_telemetry_does_not_shows_in_dog_current_status(
    api_client: TestClient
):
    # create dog first
    dog_response = api_client.post("/internal/dogs", json={
        "name": "Mr Waffles",
        "start_latitude": 51.5,
        "start_longitude": 16.3
    })
    assert dog_response.status_code == 201
    dog_id = dog_response.json()["dog_id"]

    # ingest invalid telemetry
    telemetry_response = api_client.post("/telemetry", json={
        "dog_id": dog_id,
        "event_ts": str(datetime.now()),
        "latitude": 51.5001,
        "longitude": 16.3001,
        "cumulative_steps": 120,
        "heart_rate": -5,
        "battery": 300,
        "signal_strength": 67
    })

    assert telemetry_response.status_code == 200
    telemetry_data = telemetry_response.json()
    assert telemetry_data["status"] == TelemetryStatus.REJECTED.value

    # check telemetry was not recorded on dog status
    dog_current_status_response = api_client.get(
        f"/dogs/{dog_id}/status"
    )
    dog_current_status_data = dog_current_status_response.json()
    assert dog_current_status_response.status_code == 400

    # ingest valid telemetry
    telemetry_response = api_client.post("/telemetry", json={
        "dog_id": dog_id,
        "event_ts": str(datetime.now()),
        "latitude": 51.5001,
        "longitude": 16.3001,
        "cumulative_steps": 120,
        "heart_rate": 88,
        "battery": 95,
        "signal_strength": 67
    })

    assert telemetry_response.status_code == 200
    telemetry_data = telemetry_response.json()
    valid_telemetry_event_id = telemetry_data['event_id']
    assert telemetry_data["status"] == TelemetryStatus.ACCEPTED.value

    # check telemetry was recorded on dog status
    dog_current_status_response = api_client.get(
        f"/dogs/{dog_id}/status"
    )
    dog_current_status_data = dog_current_status_response.json()
    dog_current_status_dog_id = dog_current_status_data["dog_id"]
    dog_current_status_last_event_id = dog_current_status_data["last_event_id"]
    assert dog_current_status_response.status_code == 200
    assert dog_current_status_last_event_id == valid_telemetry_event_id
    assert dog_current_status_dog_id == dog_id

    # ingest invalid telemetry
    telemetry_response = api_client.post("/telemetry", json={
        "dog_id": dog_id,
        "event_ts": str(datetime.now()),
        "latitude": 51.5001,
        "longitude": 16.3001,
        "cumulative_steps": 120,
        "heart_rate": -5,
        "battery": 300,
        "signal_strength": 67
    })

    assert telemetry_response.status_code == 200
    telemetry_data = telemetry_response.json()
    assert telemetry_data["status"] == TelemetryStatus.REJECTED.value

    # check telemetry was recorded on dog status
    dog_current_status_response = api_client.get(
        f"/dogs/{dog_id}/status"
    )
    dog_current_status_data = dog_current_status_response.json()
    dog_current_status_dog_id = dog_current_status_data["dog_id"]
    dog_current_status_last_event_id = dog_current_status_data["last_event_id"]
    assert dog_current_status_response.status_code == 200
    assert dog_current_status_last_event_id == valid_telemetry_event_id
    assert dog_current_status_dog_id == dog_id