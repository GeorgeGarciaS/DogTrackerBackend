import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd
import pydeck as pdk
import requests
import streamlit as st

from frontend.map_config import BAD_ZONE, BOUNDARY
from frontend.pipeline_indicator import (
    pipeline_animation_in_progress,
    render_pipeline_indicator,
    trigger_pipeline_animation,
)

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
TRANSPARENT_COLOR = [0, 0, 0, 0]

st.set_page_config(page_title="Dog Tracker Simulator", layout="wide")

st.markdown(
    """
    <style>
        .block-container {
            padding-top: 1.15rem;
            padding-bottom: 1rem;
        }

        .app-section-card {
            background: rgba(255,255,255,0.03);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 16px;
            padding: 14px 16px;
            margin-bottom: 14px;
        }

        .metric-row {
            padding: 10px 0;
            border-bottom: 1px solid rgba(255,255,255,0.06);
        }

        .metric-row:last-child {
            border-bottom: none;
        }

        .metric-label {
            font-size: 0.82rem;
            opacity: 0.72;
            margin-bottom: 2px;
        }

        .metric-value {
            font-size: 1.1rem;
            font-weight: 700;
            line-height: 1.25;
        }

        .section-title {
            font-size: 1.65rem;
            font-weight: 800;
            line-height: 1.1;
            margin-bottom: 2px;
        }

        .section-subtitle {
            opacity: 0.72;
            font-size: 0.95rem;
            margin-bottom: 12px;
        }

        .hero-title {
            font-size: 3rem;
            font-weight: 800;
            line-height: 1.05;
            margin-bottom: 14px;
        }

        .hero-card {
            background: rgba(255,255,255,0.04);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 14px;
            padding: 14px 18px;
            margin-bottom: 18px;
        }

        .hero-name {
            font-size: 1.05rem;
            font-weight: 700;
            margin-bottom: 4px;
        }

        .hero-sub {
            opacity: 0.8;
            font-size: 0.95rem;
        }

        .why-box {
            background: rgba(255,255,255,0.04);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 12px;
            padding: 12px 14px;
            margin-top: 8px;
        }

        .legend-panel {
            font-size: 0.82rem;
            line-height: 1.28;
            opacity: 0.92;
            padding: 8px 10px;
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 10px;
            background: rgba(255,255,255,0.03);
            width: fit-content;
            margin-left: auto;
            margin-top: 6px;
        }

        .legend-row {
            display: flex;
            align-items: center;
            gap: 6px;
            white-space: nowrap;
        }

        .legend-dot {
            font-size: 0.95rem;
            line-height: 1;
            display: inline-block;
            width: 10px;
            text-align: center;
        }

        .legend-square {
            font-size: 0.9rem;
            line-height: 1;
            display: inline-block;
            width: 10px;
            text-align: center;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


def render_header(
    dog_name: str = "Dog Tracker Simulator For Mr. Waffles, my dog"
) -> None:
    st.markdown(
        f"""
            <div style="margin-top:5px; margin-bottom:18px;">
                <div class="hero-card">
                    <div class="hero-name">{dog_name}</div>
                    <div class="hero-sub">
                        {"Prototype telemetry monitor for trusted dog position "
                        "and event decisions."}
                    </div>
                </div>
            </div>
        """,
        unsafe_allow_html=True,
    )


def render_compact_legend() -> None:
    st.markdown(
        """
        <div class="legend-panel">
            <div class="legend-row">
                <span class="legend-dot" style="color:#0078FF;">●</span>
                <span>Real dog position</span>
            </div>
            <div class="legend-row">
                <span class="legend-dot" style="color:#00B450;">●</span>
                <span>Trusted app position</span>
            </div>
            <div class="legend-row">
                <span class="legend-square" style="color:#FF4D4D;">■</span>
                <span>Degraded signal area</span>
            </div>
            <div class="legend-row">
                <span class="legend-dot" style="color:#00FF88;">●</span>
                <span>Event accepted</span>
            </div>
            <div class="legend-row">
                <span class="legend-dot" style="color:#FF3B3B;">●</span>
                <span>Event rejected</span>
            </div>
            <div class="legend-row">
                <span class="legend-dot" style="color:#FFA500;">●</span>
                <span>Degraded but accepted</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def format_ts_to_seconds(value: Any) -> str:
    if not value:
        return "-"
    try:
        text = str(value).replace("Z", "+00:00")
        dt = datetime.fromisoformat(text)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return str(value)[:19]


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


def make_point_layer(
    point: dict,
    fill_color: list[int],
    line_color: list[int],
    line_width: int = 3,
) -> pdk.Layer:
    return pdk.Layer(
        "ScatterplotLayer",
        data=pd.DataFrame([point]),
        get_position="[longitude, latitude]",
        get_fill_color=fill_color,
        get_line_color=line_color,
        get_radius=4,
        pickable=True,
        radius_min_pixels=8,
        radius_max_pixels=24,
        stroked=True,
        filled=True,
        line_width_min_pixels=line_width,
    )


def signal_icon(signal: int) -> str:
    if signal >= 70:
        return "🟢"
    if signal >= 40:
        return "🟡"
    return "🔴"


def make_deck(
    point: dict | None,
    fill_color: list[int],
    line_color: list[int],
    line_width: int = 3,
) -> pdk.Deck:
    layers = [get_zone_layer()]

    if point is not None:
        layers.append(make_point_layer(point, fill_color, line_color, line_width))

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


def get_event_type(sim_state: dict | None, backend_state: dict | None) -> str:
    if backend_state:
        value = (
            backend_state.get("event_type")
            or backend_state.get("decision_event_type")
            or backend_state.get("latest_event_type")
        )
        if value:
            return str(value)

    if sim_state:
        value = sim_state.get("last_event")
        if value:
            lowered = str(value).lower()
            if lowered in {"noisy", "stale", "invalid", "normal"}:
                return lowered
            return lowered

    return "normal"


def get_zone_label(sim_state: dict | None, backend_state: dict | None) -> str:
    if backend_state:
        value = (
            backend_state.get("zone")
            or backend_state.get("zone_status")
            or backend_state.get("zone_label")
        )
        if value:
            return str(value)

    if sim_state:
        value = sim_state.get("zone")
        if value:
            return str(value)

    return "-"


def get_result_label(backend_state: dict | None) -> str:
    if not backend_state:
        return "-"

    accepted = backend_state.get("accepted")
    if accepted is True:
        return "accepted"
    if accepted is False:
        return "rejected"

    value = (
        backend_state.get("result")
        or backend_state.get("decision_result")
        or backend_state.get("status")
    )
    if value:
        return str(value)

    return "-"


def get_reason_label(backend_state: dict | None) -> str:
    if not backend_state:
        return "-"

    value = (
        backend_state.get("reason")
        or backend_state.get("decision_reason")
        or backend_state.get("reject_reason")
    )
    if value:
        return str(value)

    return "-"


def build_why_text(
    sim_state: dict | None,
    backend_state: dict | None,
) -> str:
    if not sim_state and not backend_state:
        return "Waiting for the next telemetry decision."

    event_type = get_event_type(sim_state, backend_state)
    zone = get_zone_label(sim_state, backend_state)
    result = get_result_label(backend_state)
    reason = get_reason_label(backend_state)

    if result == "rejected":
        if reason != "-":
            return f"Telemetry event rejected due to {reason}."
        return "Telemetry event was rejected by the trusted app filter."

    if event_type == "stale":
        return "Older event received. App view kept the latest trusted position."

    if event_type == "noisy":
        if zone == "bad":
            return (
                "Dog entered the bad signal zone. "
                "Telemetry was noisy but still valid."
            )
        return "Telemetry was noisy, but the event still passed trust checks."

    if event_type == "invalid":
        if reason != "-":
            return f"Telemetry event was marked invalid due to {reason}."
        return "Telemetry event was marked invalid and ignored."

    if zone == "good":
        return "Signal recovered. App position is back in sync."

    return "Latest telemetry was processed and the trusted app state was updated."


def render_metric(label: str, value: Any) -> None:
    display_value = value if value not in [None, ""] else "-"
    st.markdown(
        f"""
        <div class="metric-row">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{display_value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


render_header()

if "prev_event_seq" not in st.session_state:
    st.session_state.prev_event_seq = 0
if "flash_until_monotonic" not in st.session_state:
    st.session_state.flash_until_monotonic = 0.0
if "dashboard_last_event" not in st.session_state:
    st.session_state.dashboard_last_event = None
if "dashboard_last_event_ts" not in st.session_state:
    st.session_state.dashboard_last_event_ts = None
if "displayed_backend_state" not in st.session_state:
    st.session_state.displayed_backend_state = None
if "pending_backend_state" not in st.session_state:
    st.session_state.pending_backend_state = None


@st.fragment(run_every=REFRESH_SECONDS)
def dashboard() -> None:
    sim_state = load_sim_state()
    latest_backend_state = load_backend_state(
        sim_state.get("dog_id") if sim_state else None
    )

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

        st.session_state.pending_backend_state = latest_backend_state

        trigger_pipeline_animation(
            current_event_seq,
            sim_state.get("telemetry_pipeline_info") if sim_state else None,
        )

    if not pipeline_animation_in_progress():
        pending = st.session_state.pending_backend_state

        if pending is not None:
            st.session_state.displayed_backend_state = pending
            st.session_state.pending_backend_state = None
        elif (
            st.session_state.displayed_backend_state is None
            and latest_backend_state is not None
        ):
            st.session_state.displayed_backend_state = latest_backend_state

    backend_state = st.session_state.displayed_backend_state

    gt_point = state_to_point(sim_state, "Ground Truth")
    app_point = state_to_point(backend_state, "Trusted App View")

    flashing = time.monotonic() < st.session_state.flash_until_monotonic

    gt_fill_color = GT_NORMAL_COLOR
    gt_line_color = EVENT_FLASH_COLOR if flashing else TRANSPARENT_COLOR
    gt_line_width = 1 if flashing else 0

    app_fill_color = APP_NORMAL_COLOR
    app_line_color = TRANSPARENT_COLOR
    app_line_width = 0

    stats_col, current_col, request_col = st.columns([1, 2.75, 1.55])

    with stats_col:
        st.subheader("Dog Device Status")
        if sim_state:
            signal = int(sim_state.get("signal_strength", 0))
            st.write(f"Signal: {signal_icon(signal)} {signal}")
            st.write(f"Battery: {sim_state.get('battery', '-')}")
            st.write(f"Heart rate: {sim_state.get('heart_rate', '-')}")
            st.write(f"Steps: {sim_state.get('cumulative_steps', '-')}")
            st.write(f"""Last tracker event: {
                st.session_state.dashboard_last_event or '-'
            }""")
            st.write(
                f"Last tracker event ts: "
                f"{format_ts_to_seconds(st.session_state.dashboard_last_event_ts)}"
            )
            st.write(f"Event counter: {current_event_seq}")
        else:
            st.warning("No simulator state yet.")

    with current_col:
        title_col, legend_col = st.columns([4.2, 1.45])

        with title_col:
            st.markdown(
                """
                <div style="margin-bottom:10px;">
                    <div class="section-title">Telemetry Pipeline</div>
                    <div class="section-subtitle">
                        Real tracker position vs trusted app position
                        after decision filtering
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with legend_col:
            render_compact_legend()

        gt_col, app_col = st.columns(2)

        with gt_col:
            st.markdown("**Real Dog Position**")
            if gt_point:
                st.pydeck_chart(
                    make_deck(gt_point, gt_fill_color, gt_line_color, gt_line_width),
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
            st.markdown("**Trusted App Position**")
            if app_point:
                st.pydeck_chart(
                    make_deck(
                        app_point,
                        app_fill_color,
                        app_line_color,
                        app_line_width,
                    ),
                    use_container_width=True,
                    height=320,
                    key = (
                        f"app_map_{app_point['latitude']}_{app_point['longitude']}_"
                        f"{current_event_seq}_{backend_state.get('updated_at', 'na')}_"
                        f"""{(
                            'pipeline_busy'
                            if pipeline_animation_in_progress()
                            else 'pipeline_done'
                        )}"""
                    )
                )
            else:
                st.info("Waiting for backend status...")

    with request_col:
        st.markdown(
            """
            <div style="margin-bottom:10px;">
                <div class="section-title">Latest Trusted App State</div>
                <div class="section-subtitle">
                    Latest trusted values shown to the app
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if backend_state:
            render_metric(
                "Last valid timestamp",
                format_ts_to_seconds(
                    backend_state.get("last_valid_ts")
                    or backend_state.get("last_event_ts")
                ),
            )
            render_metric("Battery", backend_state.get("battery", "-"))
            render_metric("Signal strength", backend_state.get("signal_strength", "-"))
            render_metric("Heart rate", backend_state.get("heart_rate", "-"))
            render_metric("Steps", backend_state.get("cumulative_steps", "-"))
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("Waiting for trusted app state...")

    st.markdown("---")
    st.markdown("**API Pipeline**")
    render_pipeline_indicator()


dashboard()