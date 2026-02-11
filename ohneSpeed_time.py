import streamlit as st
import process.cached_fetch as cfetch

st.markdown("# Temps références ohne speed.")
RP = cfetch.get_ohne_speed(names_format="ohne", time_format="min:s")


st.table(RP)
