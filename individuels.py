import connect
import streamlit as st

team_pilots_dict = connect.get_team_pilots()
sbPilots = st.selectbox(
    "Pilot",
    sorted(team_pilots_dict.keys()),
    width=500,
    index=0,
)


LC, RC = st.columns(2)

sbLigne = LC.selectbox(
    "Circuit",
    ["All"],  # + sorted([x for x in select.index]),
    width=500,
    index=0,
)
sbCol = RC.selectbox(
    "Voiture",
    ["All"],  # + sorted([x for x in select.columns]),
    width=500,
    index=0,
)

radio = st.radio(
    "Data",
    ["Performance", "Laps"],
    horizontal=True,
)

st.table(connect.get_showable_pilot_df(team_pilots_dict[sbPilots], data=radio))
if st.button("Reload MSR data"):
    connect.update_all_MSR_data()
    print(st.session_state["MSR_session"])
