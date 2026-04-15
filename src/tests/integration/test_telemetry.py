from datetime import datetime, timedelta

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


@pytest.mark.timeout(300)
def test_ingest_telemetry_detects_exact_duplicate_and_logs_dq_issue(
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

    event_ts = str(datetime.now())

    payload = {
        "dog_id": dog_id,
        "event_ts": event_ts,
        "latitude": 51.5001,
        "longitude": 16.3001,
        "cumulative_steps": 120,
        "heart_rate": 88,
        "battery": 95,
        "signal_strength": 67
    }

    # first ingest should be accepted
    first_response = api_client.post("/telemetry", json=payload)
    assert first_response.status_code == 200
    first_data = first_response.json()
    assert "event_id" in first_data
    assert first_data["status"] == TelemetryStatus.ACCEPTED.value

    # Valid telemetry should update dog_id.status
    dog_current_status_response = api_client.get(f"/dogs/{dog_id}/status")
    assert dog_current_status_response.status_code == 200
    dog_current_status_data = dog_current_status_response.json()
    assert dog_current_status_data["dog_id"] == dog_id
    assert dog_current_status_data["last_event_id"] == first_data["event_id"]

    # exact same payload should be detected as duplicate
    duplicate_response = api_client.post("/telemetry", json=payload)
    assert duplicate_response.status_code == 200
    duplicate_data = duplicate_response.json()

    duplicate_event_id = duplicate_data["event_id"]
    assert duplicate_event_id != ""
    assert duplicate_data["status"] == TelemetryStatus.REJECTED.value
    assert TelemetryIssueType.DUPLICATE_EVENT.value in duplicate_data["detail"]

    # check duplicate telemetry was logged in data quality issues
    data_quality_issue_response = api_client.get(
        f"/internal/data_quality_issues/{duplicate_event_id}"
    )
    assert data_quality_issue_response.status_code == 200

    list_data_quality_issue_data = data_quality_issue_response.json()
    assert len(list_data_quality_issue_data) == 1

    duplicate_issue_found = False
    for data_quality_issue_data in list_data_quality_issue_data:
        assert "issue_id" in data_quality_issue_data
        assert data_quality_issue_data["dog_id"] == dog_id
        assert data_quality_issue_data["event_id"] == duplicate_event_id
        if data_quality_issue_data[
            "issue_type"
        ] == TelemetryIssueType.DUPLICATE_EVENT.value:
            duplicate_issue_found = True

    assert duplicate_issue_found is True


@pytest.mark.timeout(300)
def test_ingest_delayed_valid_telemetry_updates_current_status_when_newer_than_stored(
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

    # simulate delayed telemetry:
    # event happened a few seconds ago, but arrives now
    delayed_event_ts = str(datetime.now() - timedelta(seconds=15))

    delayed_response = api_client.post("/telemetry", json={
        "dog_id": dog_id,
        "event_ts": delayed_event_ts,
        "latitude": 51.50012,   # slight coordinate drift
        "longitude": 16.30012,
        "cumulative_steps": 118,  # slightly inconsistent but still valid
        "heart_rate": 86,         # slightly noisy but valid
        "battery": 95,
        "signal_strength": 20     # degraded but valid
    })

    assert delayed_response.status_code == 200
    delayed_data = delayed_response.json()
    delayed_event_id = delayed_data["event_id"]

    assert delayed_data["status"] == TelemetryStatus.ACCEPTED.value
    assert delayed_data["detail"] == ""

    # because this is the first valid telemetry for the dog,
    # it should still become current status even though event_ts is in the past
    dog_current_status_response = api_client.get(f"/dogs/{dog_id}/status")
    assert dog_current_status_response.status_code == 200

    dog_current_status_data = dog_current_status_response.json()
    assert dog_current_status_data["dog_id"] == dog_id
    assert dog_current_status_data["last_event_id"] == delayed_event_id


@pytest.mark.timeout(300)
def test_ingest_stale_telemetry_does_not_override_newer_current_status(
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

    older_ts = str(datetime.now() - timedelta(seconds=20))
    newer_ts = str(datetime.now() - timedelta(seconds=5))

    # ingest newer valid telemetry first
    newer_response = api_client.post("/telemetry", json={
        "dog_id": dog_id,
        "event_ts": newer_ts,
        "latitude": 51.5002,
        "longitude": 16.3002,
        "cumulative_steps": 140,
        "heart_rate": 90,
        "battery": 94,
        "signal_strength": 70
    })

    assert newer_response.status_code == 200
    newer_data = newer_response.json()
    newer_event_id = newer_data["event_id"]
    assert newer_data["status"] == TelemetryStatus.ACCEPTED.value

    # now send stale telemetry that arrives later but has older event_ts
    stale_response = api_client.post("/telemetry", json={
        "dog_id": dog_id,
        "event_ts": older_ts,
        "latitude": 51.5001,
        "longitude": 16.3001,
        "cumulative_steps": 120,
        "heart_rate": 88,
        "battery": 95,
        "signal_strength": 67
    })

    assert stale_response.status_code == 200
    stale_data = stale_response.json()

    # stale data may still be accepted as valid telemetry,
    # but it must not replace current dog status
    assert stale_data["status"] == TelemetryStatus.ACCEPTED.value

    dog_current_status_response = api_client.get(f"/dogs/{dog_id}/status")
    assert dog_current_status_response.status_code == 200

    dog_current_status_data = dog_current_status_response.json()
    assert dog_current_status_data["dog_id"] == dog_id
    assert dog_current_status_data["last_event_id"] == newer_event_id