import pandas as pd
import streamlit as st

st.set_page_config(page_title="Student Study Tracker", layout="wide")

#shared data: read the CSV once, then every page reads and changes st.session_state.df
if "df" not in st.session_state:
    df = pd.read_csv("students.csv", parse_dates=["Date"])

    st.session_state.df = df
    st.session_state.sample = df.copy()
    st.session_state.notes = []
    st.session_state.chat = [
        {"role": "assistant", "content": "Hi! Ask me anything about the students."}
    ]

pages = [
    st.Page("Lab6.py", title="Home"),
    st.Page("Lab6_pg2.py", title="Graphs"),
    st.Page("Lab6_pg3.py", title="Files"),
]

pg = st.navigation(pages)

with st.sidebar:
    st.caption(f"{len(st.session_state.df)} students loaded")

pg.run()