import streamlit as st
import connect


RP, Q = connect.get_ohneSpeed_times(format="OG", formatTime="min.s")


st.table(RP)
