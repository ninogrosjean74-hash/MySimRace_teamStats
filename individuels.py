import streamlit as st

import process.treat_data as treat_data
import process.cached_fetch as cfetch

all_data = cfetch.get_all_data()
ohne_speed_MSR_s = cfetch.get_ohne_speed("MSR", "s")
treat_data.comp_all_performances(all_data, ohne_speed_MSR_s)

st.markdown("# Meilleurs temps")


team_pilots_dict = all_data["pilots"]
sbPilots = st.selectbox(
    "Pilot",
    team_pilots_dict.keys(),
    format_func=lambda id: team_pilots_dict[id]["name"],
    width=250,
    index=0,
)


# LC, RC = st.columns(2)

# sbLigne = LC.selectbox(
#     "Circuit",
#     ["All"] + sorted([x["track_name"] for x in all_data["tracks"].values()]),
#     width=500,
#     index=0,
# )
# sbCol = RC.selectbox(
#     "Voiture",
#     ["All"] + sorted([x for x in select.columns]),
#     width=500,
#     index=0,
# )

radio = st.radio(
    "Data",
    ["Performance", "Laps"],
    horizontal=True,
)

st.table(treat_data.get_showable_pilot_df(all_data, sbPilots, data=radio))
