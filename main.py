import streamlit as st
import pandas as pd
import time

import process.login as login
import process.cached_fetch as cfetch
import process.treat_data as treat_data

st.set_page_config(
    page_title="GRID 404",
    layout="wide",
    page_icon="🏎️",
)  # active le wide mode

if not "session" in st.session_state:
    st.session_state["session"] = login.create_session()

if not "is_logged" in st.session_state:
    st.session_state["is_logged"] = False

if not "session_expired" in st.session_state:
    st.session_state["session_expired"] = False


if not st.session_state["is_logged"]:
    if st.session_state["session_expired"]:
        st.markdown("Session expired : reconnect")
    else:
        st.markdown("Connection to Mysimrace")

    username = st.text_input("Pilot name", width=400)
    password = st.text_input("Password", type="password", width=400)
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
    all_data = cfetch.get_all_data()
    ohne_speed_MSR_s = cfetch.get_ohne_speed("MSR", "s")
    treat_data.comp_all_performances(all_data, ohne_speed_MSR_s)

    # Define the pages
    teamLeaderBoard = st.Page("teamLeaderBoard.py", title="Leaderboard")
    individuels = st.Page("individuels.py", title="Temps individuels")
    ohneSpeed = st.Page("ohneSpeed_time.py", title="Temps Ohne Speed")

    # Set up navigation
    pg = st.navigation([teamLeaderBoard, individuels, ohneSpeed])

    # Run the selected page
    pg.run()

    ft: time.struct_time = all_data["fetch_time"]
    if st.button("Reload data"):
        st.cache_data.clear()
        if not login.is_logged_in(st.session_state["session"]):
            st.session_state["session_expired"] = True
            st.session_state["is_logged"] = False
        st.rerun()

    st.markdown(f"Dernier chargement des données : {ft.tm_mday:02d}/{ft.tm_mon:02d} {ft.tm_hour:02d}h{ft.tm_min:02d}")
