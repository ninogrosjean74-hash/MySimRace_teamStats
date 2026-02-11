import streamlit as st
import pandas as pd
import process.fetch as fetch
import process.treat_data as treat_data


@st.cache_data
def get_all_data() -> dict:
    session = st.session_state["session"]
    return fetch.fetch_all_data(session)


@st.cache_data
def cache_ohne_speed() -> pd.DataFrame:
    df = fetch.fetch_ohne_speed()
    return treat_data.get_ohneSpeed_times(df)


def get_ohne_speed(names_format="ohne", time_format="min:s") -> pd.DataFrame:
    df = cache_ohne_speed()

    if names_format == "MSR":
        df = treat_data.ohne2MSR_notation(df)
    elif names_format != "ohne":
        print('Incorrect name format : "ohne" or "MSR"')

    if time_format == "min:s":
        return df
    elif time_format == "s":
        return df.map(treat_data.format_time_MinS_2_S)
    else:
        print('Incorrect time format : "min:s" or "s"')
