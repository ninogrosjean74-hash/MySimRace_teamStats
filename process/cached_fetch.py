import streamlit as st

import fetch


@st.cache_data
def get_all_data() -> dict:
    session = st.session_state["session"]
    return fetch.fetch_all_data(session)
