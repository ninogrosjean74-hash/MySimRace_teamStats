import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="GRID 404",
    layout="wide",
    page_icon="🏎️",
)  # active le wide mode

# Define the pages
teamLeaderBoard = st.Page("teamLeaderBoard.py", title="Leaderboard")
individuels = st.Page("individuels.py", title="Temps individuels")
ohneSpeed = st.Page("ohneSpeed_time.py", title="Temps Ohne Speed")

# Set up navigation
pg = st.navigation([teamLeaderBoard, individuels, ohneSpeed])

# Run the selected page
pg.run()
