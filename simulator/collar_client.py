import requests


def build_telemetry_payload(dog, signal_quality: int) -> dict:
    return {
        "dog_id": dog.dog_id,
        "event_ts": dog.last_update_ts.isoformat(),
        "latitude": dog.latitude,
        "longitude": dog.longitude,
        "cumulative_steps": dog.cumulative_steps,
        "heart_rate": dog.heart_rate,
        "battery": dog.battery,
        "signal_strength": signal_quality,
    }



def create_dog(
    base_url: str,
    name: str,
    start_latitude: float,
    start_longitude: float
) -> str:
    url = f"{base_url}/dogs"
    payload = {
        "name": name,
        "start_latitude": start_latitude,
        "start_longitude": start_longitude,
    }

    response = requests.post(url, json=payload, timeout=5)
    print(f"create dog status={response.status_code}")
    print(response.text)
    response.raise_for_status()

    data = response.json()
    return data["dog_id"]

def send_telemetry(payload: dict, base_url: str) -> None:
    url = f"{base_url}/telemetry"
    response = requests.post(url, json=payload, timeout=5)
    response.raise_for_status()

    print(f"sent telemetry: status={response.status_code}")
    return response.json()