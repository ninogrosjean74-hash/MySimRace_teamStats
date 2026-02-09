import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="GRID 404",
    layout="wide",
    page_icon="🏎️",
)  # active le wide mode

if "session" not in st.session_state:
    st.markdown("# Not yet connect to MySimRace.com")
    pilot = st.text_input("Pilot name")
    pwd = st.text_input("Password", type="password")

    if st.button("Login"):
        # st.session_state["session"] = re
        st.success("Connected!")
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
