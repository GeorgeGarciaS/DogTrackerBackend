import json
import os
import time
from pathlib import Path
from typing import Any

import pandas as pd
import pydeck as pdk
import requests
import streamlit as st

from frontend.map_config import BAD_ZONE, BOUNDARY

DEFAULT_STATE_PATH = Path(__file__).resolve().parent / "runtime" / "sim_state.json"
SIM_STATE_PATH = Path(os.getenv("SIM_STATE_PATH", DEFAULT_STATE_PATH))
BACKEND_BASE_URL = os.getenv("BACKEND_BASE_URL", "http://localhost:8000")

CENTER_LAT = (BOUNDARY["min_lat"] + BOUNDARY["max_lat"]) / 2
CENTER_LON = (BOUNDARY["min_lon"] + BOUNDARY["max_lon"]) / 2
REFRESH_SECONDS = 0.4
EVENT_FLASH_SECONDS = 1.0

GT_NORMAL_COLOR = [0, 120, 255, 220]
APP_NORMAL_COLOR = [0, 180, 80, 220]
EVENT_FLASH_COLOR = [255, 0, 0, 230]

st.set_page_config(page_title="Dog Tracker Simulator", layout="wide")
st.title(
    """Dog Tracker Simulator - 
    Dog: Mr Waffles - 
    This is a proof of concept, reloads are needed"""
)


def load_sim_state() -> dict | None:
    if not SIM_STATE_PATH.exists():
        return None
    try:
        return json.loads(SIM_STATE_PATH.read_text())
    except Exception:
        return None


def load_backend_state(dog_id: str | None) -> dict | None:
    if not dog_id:
        return None
    try:
        response = requests.get(f"{BACKEND_BASE_URL}/dogs/{dog_id}/status", timeout=0.5)
        response.raise_for_status()
        return response.json()
    except Exception:
        return None


def rectangle_polygon(zone: dict) -> list[list[float]]:
    return [
        [zone["min_lon"], zone["min_lat"]],
        [zone["max_lon"], zone["min_lat"]],
        [zone["max_lon"], zone["max_lat"]],
        [zone["min_lon"], zone["max_lat"]],
        [zone["min_lon"], zone["min_lat"]],
    ]


@st.cache_data
def get_static_zones() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "name": "Boundary",
                "polygon": rectangle_polygon(BOUNDARY),
                "fill_color": [0, 0, 0, 0],
                "line_color": [0, 0, 0, 255],
            },
            {
                "name": "Bad Zone",
                "polygon": rectangle_polygon(BAD_ZONE),
                "fill_color": [255, 0, 0, 40],
                "line_color": [220, 0, 0, 255],
            },
        ]
    )


@st.cache_resource
def get_zone_layer() -> pdk.Layer:
    return pdk.Layer(
        "PolygonLayer",
        data=get_static_zones(),
        get_polygon="polygon",
        get_fill_color="fill_color",
        get_line_color="line_color",
        stroked=True,
        filled=True,
        pickable=True,
        line_width_min_pixels=3,
    )


def state_to_point(state: dict | None, name: str) -> dict | None:
    if not state:
        return None

    lat = state.get("latitude")
    lon = state.get("longitude")
    if lat is None or lon is None:
        return None

    return {
        "name": name,
        "latitude": lat,
        "longitude": lon,
    }


def make_point_layer(point: dict, color: list[int]) -> pdk.Layer:
    return pdk.Layer(
        "ScatterplotLayer",
        data=pd.DataFrame([point]),
        get_position="[longitude, latitude]",
        get_fill_color=color,
        get_radius=4,
        pickable=True,
        radius_min_pixels=8,
        radius_max_pixels=24,
    )


def signal_icon(signal: int) -> str:
    if signal >= 70:
        return "🟢"
    if signal >= 40:
        return "🟡"
    return "🔴"


def make_deck(point: dict | None, color: list[int]) -> pdk.Deck:
    layers = [get_zone_layer()]

    if point is not None:
        layers.append(make_point_layer(point, color))

    tooltip: Any = {"text": "{name}"}
    return pdk.Deck(
        initial_view_state=pdk.ViewState(
            latitude=CENTER_LAT,
            longitude=CENTER_LON,
            zoom=16,
            pitch=0,
        ),
        layers=layers,
        tooltip=tooltip,
        map_style="light",
    )


if "prev_event_seq" not in st.session_state:
    st.session_state.prev_event_seq = 0
if "flash_until_monotonic" not in st.session_state:
    st.session_state.flash_until_monotonic = 0.0
if "dashboard_last_event" not in st.session_state:
    st.session_state.dashboard_last_event = None
if "dashboard_last_event_ts" not in st.session_state:
    st.session_state.dashboard_last_event_ts = None


@st.fragment(run_every=REFRESH_SECONDS)
def dashboard() -> None:
    sim_state = load_sim_state()
    backend_state = load_backend_state(sim_state.get("dog_id") if sim_state else None)

    gt_point = state_to_point(sim_state, "Ground Truth")
    app_point = state_to_point(backend_state, "App View")

    current_event_seq = 0
    current_last_event = None
    current_last_event_ts = None

    if sim_state:
        current_event_seq = int(sim_state.get("event_seq", 0) or 0)
        current_last_event = sim_state.get("last_event")
        current_last_event_ts = sim_state.get("last_event_ts")

    if current_event_seq > st.session_state.prev_event_seq:
        st.session_state.prev_event_seq = current_event_seq
        st.session_state.flash_until_monotonic = time.monotonic() + EVENT_FLASH_SECONDS
        st.session_state.dashboard_last_event = current_last_event
        st.session_state.dashboard_last_event_ts = current_last_event_ts

    flashing = time.monotonic() < st.session_state.flash_until_monotonic

    gt_color = EVENT_FLASH_COLOR if flashing else GT_NORMAL_COLOR
    app_color = APP_NORMAL_COLOR

    # 3 columns total:
    # 1) dog stats on far left
    # 2) current dashboard (2 maps) in middle
    # 3) request event dashboard (no extra map) on right
    stats_col, current_col, request_col = st.columns([1, 2.6, 1.4])

    with stats_col:
        st.subheader("Dog Stats")
        if sim_state:
            signal = int(sim_state.get("signal_strength", 0))
            st.write(f"Signal: {signal_icon(signal)} {signal}")
            st.write(f"Battery: {sim_state.get('battery', '-')}")
            st.write(f"Heart rate: {sim_state.get('heart_rate', '-')}")
            st.write(f"Steps: {sim_state.get('cumulative_steps', '-')}")
            st.write(
                f"Last tracker event: {st.session_state.dashboard_last_event or '-'}"
            )
            st.write(
                f"""Last tracker event ts: {
                    st.session_state.dashboard_last_event_ts or '-'
                }"""
            )
            st.write(f"Event counter: {current_event_seq}")
        else:
            st.warning("No simulator state yet.")

    with current_col:
        st.subheader("Current Dashboard")

        gt_col, app_col = st.columns(2)

        with gt_col:
            st.markdown("**Ground Truth (Dog Simulator)**")
            if gt_point:
                st.pydeck_chart(
                    make_deck(gt_point, gt_color),
                    use_container_width=True,
                    height=320,
                    key=(
                        f"gt_map_{gt_point['latitude']}_{gt_point['longitude']}_"
                        f"{current_event_seq}_{'flash' if flashing else 'normal'}"
                    ),
                )
            else:
                st.warning("No simulator state yet.")

        with app_col:
            st.markdown("**App View**")
            if app_point:
                st.pydeck_chart(
                    make_deck(app_point, app_color),
                    use_container_width=True,
                    height=320,
                    key=(
                        f"app_map_{app_point['latitude']}_{app_point['longitude']}_"
                        f"{current_event_seq}_{'flash' if flashing else 'normal'}"
                    ),
                )
            else:
                st.info("Waiting for backend status...")

    with request_col:
        st.subheader("Request Event Dashboard")

        if backend_state:
            st.markdown("**DogCurrentStatusResponse**")
            st.write(f"dog_id: {backend_state.get('dog_id', '-')}")
            st.write(f"last_event_id: {backend_state.get('last_event_id', '-')}")
            st.write(f"last_event_ts: {backend_state.get('last_event_ts', '-')}")
            st.write(f"latitude: {backend_state.get('latitude', '-')}")
            st.write(f"longitude: {backend_state.get('longitude', '-')}")
            st.write(f"cumulative_steps: {backend_state.get('cumulative_steps', '-')}")
            st.write(f"heart_rate: {backend_state.get('heart_rate', '-')}")
            st.write(f"battery: {backend_state.get('battery', '-')}")
            st.write(f"signal_strength: {backend_state.get('signal_strength', '-')}")
            st.write(f"updated_at: {backend_state.get('updated_at', '-')}")
        else:
            st.info("Waiting for request-event payload...")

dashboard()