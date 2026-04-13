import json
import os
from pathlib import Path

import pandas as pd
import requests
import streamlit as st

SIM_STATE_PATH = Path("/app/simulator/runtime/sim_state.json")
BACKEND_BASE_URL = os.getenv("BACKEND_BASE_URL", "http://localhost:8000")


st.set_page_config(page_title="Dog Tracker", layout="wide")
st.title("Dog Tracker Simulator")


def load_sim_state() -> dict | None:
    if not SIM_STATE_PATH.exists():
        return None

    try:
        return json.loads(SIM_STATE_PATH.read_text())
    except Exception:
        return None


def load_current_status() -> dict | None:
    try:
        response = requests.get(f"{BACKEND_BASE_URL}/dog_current_status", timeout=5)
        response.raise_for_status()
        return response.json()
    except Exception:
        return None


sim_state = load_sim_state()
backend_state = load_current_status()

col1, col2 = st.columns(2)

with col1:
    st.subheader("Ground Truth")
    if sim_state:
        st.json(sim_state)

        df = pd.DataFrame(
            [{"lat": sim_state["latitude"], "lon": sim_state["longitude"]}]
        )
        st.map(df)
    else:
        st.warning("No simulator state yet.")

with col2:
    st.subheader("Backend Current Status")
    if backend_state:
        st.json(backend_state)

        if "latitude" in backend_state and "longitude" in backend_state:
            df = pd.DataFrame(
                [{"lat": backend_state["latitude"], "lon": backend_state["longitude"]}]
            )
            st.map(df)
    else:
        st.warning("No backend status yet.")