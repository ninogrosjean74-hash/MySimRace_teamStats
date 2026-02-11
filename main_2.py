import streamlit as st
import pandas as pd
import time

import process.login as login
import process.cached_fetch as fetch

st.set_page_config(
    page_title="GRID 404",
    layout="wide",
    page_icon="🏎️",
)  # active le wide mode

if not "session" in st.session_state:
    st.session_state["session"] = login.create_session()

if not "is_logged" in st.session_state:
    st.session_state["is_logged"] = False


if not st.session_state["is_logged"]:
    username = st.text_input("Pilot name")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if login.login_MSR(st.session_state["session"], username, password):
            st.session_state["is_logged"] = True
            st.success("Connected!")
            time.sleep(1)
            st.rerun()
        else:
            st.warning("Connection failed")
            st.rerun()
else:
    # Define the pages
    teamLeaderBoard = st.Page("teamLeaderBoard.py", title="Leaderboard")
    individuels = st.Page("individuels.py", title="Temps individuels")
    ohneSpeed = st.Page("ohneSpeed_time.py", title="Temps Ohne Speed")

    # Set up navigation
    pg = st.navigation([teamLeaderBoard, individuels, ohneSpeed])

    # Run the selected page
    pg.run()
