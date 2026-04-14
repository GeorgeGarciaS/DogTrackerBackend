import time
from typing import Literal

import streamlit as st
import streamlit.components.v1 as components

NodeColor = Literal["white", "green", "red"]

STEP_DURATION_SECONDS = 0.25


def _init_pipeline_state() -> None:
    if "pipeline_animating" not in st.session_state:
        st.session_state.pipeline_animating = False
    if "pipeline_animation_started_at" not in st.session_state:
        st.session_state.pipeline_animation_started_at = 0.0
    if "pipeline_active_path" not in st.session_state:
        st.session_state.pipeline_active_path = []
    if "pipeline_active_branch" not in st.session_state:
        st.session_state.pipeline_active_branch = "main"
    if "pipeline_last_event_seq" not in st.session_state:
        st.session_state.pipeline_last_event_seq = 0


def _determine_path(pipeline_info: dict | None) -> tuple[list[str], str]:
    if not pipeline_info:
        return [], "main"

    has_invalid = any(
        pipeline_info.get(k)
        for k in [
            "invalid_telemetry",
            "telemetry_rejected",
            "data_quality_issues_ingest",
        ]
    )

    if has_invalid:
        active: list[str] = []

        if pipeline_info.get("api"):
            active.append("api")
        if pipeline_info.get("invalid_telemetry"):
            active.append("invalid_telemetry")
        if pipeline_info.get("telemetry_raw_ingest"):
            active.append("telemetry_raw_ingest")
        if pipeline_info.get("telemetry_rejected"):
            active.append("telemetry_rejected")
        if pipeline_info.get("data_quality_issues_ingest"):
            active.append("data_quality_issues_ingest")

        return active, "invalid"

    active = []
    for key in [
        "api",
        "telemetry_raw_ingest",
        "telemetry_accepted",
        "status_updated",
    ]:
        if pipeline_info.get(key):
            active.append(key)

    return active, "main"


def trigger_pipeline_animation(event_seq: int, pipeline_info: dict | None) -> None:
    _init_pipeline_state()

    if event_seq > st.session_state.pipeline_last_event_seq:
        st.session_state.pipeline_last_event_seq = event_seq
        active_path, branch = _determine_path(pipeline_info)
        st.session_state.pipeline_active_path = active_path
        st.session_state.pipeline_active_branch = branch
        st.session_state.pipeline_animation_started_at = time.monotonic()
        st.session_state.pipeline_animating = True


def pipeline_animation_in_progress() -> bool:
    _init_pipeline_state()

    if not st.session_state.pipeline_animating:
        return False

    elapsed = time.monotonic() - st.session_state.pipeline_animation_started_at
    max_count = len(st.session_state.pipeline_active_path)

    if max_count == 0:
        st.session_state.pipeline_animating = False
        return False

    count = int(elapsed / STEP_DURATION_SECONDS) + 1
    if count > max_count:
        st.session_state.pipeline_animating = False
        return False

    return True


def _current_lit_keys() -> set[str]:
    if not pipeline_animation_in_progress():
        return set()

    elapsed = time.monotonic() - st.session_state.pipeline_animation_started_at
    count = int(elapsed / STEP_DURATION_SECONDS) + 1
    return set(st.session_state.pipeline_active_path[:count])


def _node_color(node_key: str, lit_keys: set[str], branch: str) -> NodeColor:
    if node_key not in lit_keys:
        return "white"

    if node_key in {
        "invalid_telemetry",
        "telemetry_rejected",
        "data_quality_issues_ingest",
    }:
        return "red"

    return "green"


def _label_html(label: str, color: NodeColor) -> str:
    if color == "green":
        text_color = "#22c55e"
        glow = "0 0 8px rgba(34,197,94,0.65)"
    elif color == "red":
        text_color = "#ef4444"
        glow = "0 0 8px rgba(239,68,68,0.65)"
    else:
        text_color = "#ffffff"
        glow = "none"

    return f"""
    <div class="pipeline-label" style="color:{text_color}; text-shadow:{glow};">
        {label}
    </div>
    """


def render_pipeline_indicator() -> None:
    _init_pipeline_state()

    lit_keys = _current_lit_keys()
    branch = st.session_state.pipeline_active_branch

    html = f"""
    <html>
    <head>
      <style>
        body {{
          margin: 0;
          background: transparent;
          font-family: Arial, sans-serif;
        }}

        .wrap {{
          padding: 6px 0 2px 0;
        }}

        .grid {{
          display: grid;
          grid-template-columns: 120px 28px 170px 28px 150px 28px 190px;
          grid-template-rows: auto auto;
          row-gap: 34px;
          align-items: center;
        }}

        .pipeline-label {{
          font-size: 14px;
          font-weight: 700;
          white-space: nowrap;
          transition: color 0.2s ease, text-shadow 0.2s ease;
        }}

        .arrow {{
          color: #64748b;
          font-size: 18px;
          text-align: center;
        }}

        .branch {{
          color: #64748b;
          font-size: 18px;
          text-align: left;
          line-height: 1;
          margin-top: -8px;
        }}
      </style>
    </head>
    <body>
      <div class="wrap">
        <div class="grid">
          <div style="grid-column:1; grid-row:1;">
            {_label_html("API", _node_color("api", lit_keys, branch))}
          </div>
          <div class="arrow" style="grid-column:2; grid-row:1;">→</div>

          <div style="grid-column:3; grid-row:1;">
            {_label_html("Raw Ingest", _node_color("telemetry_raw_ingest", lit_keys, branch))}
          </div>
          <div class="arrow" style="grid-column:4; grid-row:1;">→</div>

          <div style="grid-column:5; grid-row:1;">
            {_label_html("Accepted", _node_color("telemetry_accepted", lit_keys, branch))}
          </div>
          <div class="arrow" style="grid-column:6; grid-row:1;">→</div>

          <div style="grid-column:7; grid-row:1;">
            {_label_html("Status Updated", _node_color("status_updated", lit_keys, branch))}
          </div>

          <div class="branch" style="grid-column:1; grid-row:2;">↘</div>
          <div style="grid-column:1; grid-row:2;">
            {_label_html("Invalid Telemetry", _node_color("invalid_telemetry", lit_keys, branch))}
          </div>

          <div
            class="branch"
            style="grid-column:3; grid-row:2; justify-self:end; margin-right:-22px;"
          >
            ↘
          </div>
          <div style="grid-column:5; grid-row:2;">
            {_label_html("Rejected", _node_color("telemetry_rejected", lit_keys, branch))}
          </div>
          <div class="arrow" style="grid-column:6; grid-row:2;">→</div>

          <div style="grid-column:7; grid-row:2;">
            {_label_html("DQ Issues", _node_color("data_quality_issues_ingest", lit_keys, branch))}
          </div>
        </div>
      </div>
    </body>
    </html>
    """

    components.html(html, height=115, scrolling=False)