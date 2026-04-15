import os
from typing import Any

import pandas as pd
import pydeck as pdk
import requests
import streamlit as st

from frontend.map_config import BOUNDARY

BACKEND_BASE_URL = os.getenv("BACKEND_BASE_URL", "http://localhost:8000")
SIGNAL_ZONE_ENDPOINT = f"{BACKEND_BASE_URL}/analytics/signal-zone-bounds"
SIGNAL_ZONE_REFRESH_SECONDS = 3.0


def _rectangle_polygon(row: dict[str, Any]) -> list[list[float]]:
    return [
        [row["min_lon"], row["min_lat"]],
        [row["max_lon"], row["min_lat"]],
        [row["max_lon"], row["max_lat"]],
        [row["min_lon"], row["max_lat"]],
        [row["min_lon"], row["min_lat"]],
    ]


def _zone_fill_color(is_bad_zone: bool) -> list[int]:
    return [255, 59, 59, 90] if is_bad_zone else [0, 180, 80, 90]

def _boundary_polygon() -> list[list[float]]:
    return [
        [BOUNDARY["min_lon"], BOUNDARY["min_lat"]],
        [BOUNDARY["max_lon"], BOUNDARY["min_lat"]],
        [BOUNDARY["max_lon"], BOUNDARY["max_lat"]],
        [BOUNDARY["min_lon"], BOUNDARY["max_lat"]],
        [BOUNDARY["min_lon"], BOUNDARY["min_lat"]],
    ]
def _build_boundary_layer() -> pdk.Layer:
    return pdk.Layer(
        "PolygonLayer",
        data=pd.DataFrame([
            {
                "polygon": _boundary_polygon(),
            }
        ]),
        get_polygon="polygon",
        get_fill_color=[0, 0, 0, 0],       # transparent fill
        get_line_color=[0, 0, 0, 255],     # black outline
        stroked=True,
        filled=True,
        line_width_min_pixels=3,
        pickable=False,
    )

def _zone_line_color(is_bad_zone: bool) -> list[int]:
    return [255, 59, 59, 230] if is_bad_zone else [0, 180, 80, 230]


def fetch_signal_zone_bounds() -> list[dict[str, Any]]:
    try:
        response = requests.get(SIGNAL_ZONE_ENDPOINT, timeout=2.0)
        response.raise_for_status()
        data = response.json()
        if isinstance(data, list):
            return data
    except Exception:
        pass
    return []


def build_signal_zone_dataframe(zones: list[dict[str, Any]]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []

    for zone in zones:
        is_bad_zone = bool(zone.get("is_bad_zone", False))
        rows.append(
            {
                "polygon": _rectangle_polygon(zone),
                "fill_color": _zone_fill_color(is_bad_zone),
                "line_color": _zone_line_color(is_bad_zone),
                "is_bad_zone": is_bad_zone,
                "avg_signal": zone.get("avg_signal"),
                "total_events": zone.get("total_events"),
                "rejected_events": zone.get("rejected_events"),
                "rejection_ratio": zone.get("rejection_ratio"),
                "center_lat": zone.get("center_lat"),
                "center_lon": zone.get("center_lon"),
            }
        )

    return pd.DataFrame(rows)


def _get_view_state(zones_df: pd.DataFrame) -> pdk.ViewState:
    if zones_df.empty:
        return pdk.ViewState(latitude=37.7750, longitude=-122.4194, zoom=15.8, pitch=0)

    return pdk.ViewState(
        latitude=float(zones_df["center_lat"].mean()),
        longitude=float(zones_df["center_lon"].mean()),
        zoom=15.8,
        pitch=0,
    )


def build_signal_zone_deck(zones_df: pd.DataFrame) -> pdk.Deck:
    layer = pdk.Layer(
        "PolygonLayer",
        data=zones_df,
        get_polygon="polygon",
        get_fill_color="fill_color",
        get_line_color="line_color",
        filled=True,
        stroked=True,
        pickable=True,
        line_width_min_pixels=2,
    )

    tooltip: Any = {
        "html": """
        <div style="font-size: 12px;">
            <div><b>Zone:</b> {is_bad_zone}</div>
            <div><b>Avg signal:</b> {avg_signal}</div>
            <div><b>Total events:</b> {total_events}</div>
            <div><b>Rejected events:</b> {rejected_events}</div>
            <div><b>Rejection ratio:</b> {rejection_ratio}</div>
        </div>
        """
    }

    boundary_layer = _build_boundary_layer()

    return pdk.Deck(
        layers=[boundary_layer, layer],  # boundary first so it's underneath
        initial_view_state=_get_view_state(zones_df),
        map_style="light",
        tooltip=tooltip,
    )


def render_signal_zone_map(height: int = 80) -> None:
    st.markdown("**Signal Zone Map**")
    st.caption("Refreshes every 3 seconds")

    zones = fetch_signal_zone_bounds()
    if not zones:
        st.info("Waiting for signal zone analytics...")
        return

    zones_df = build_signal_zone_dataframe(zones)
    st.pydeck_chart(
        build_signal_zone_deck(zones_df),
        use_container_width=True,
        height=height,
        key=f"signal_zone_map_{len(zones_df)}",
    )


@st.fragment(run_every=SIGNAL_ZONE_REFRESH_SECONDS)
def signal_zone_map_fragment(height: int = 80) -> None:
    render_signal_zone_map(height=height)