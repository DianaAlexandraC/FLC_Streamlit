import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st

COLUMNS = ["Name", "Group", "Hours", "Score", "Date", "Lab"]


def load_data(new):
    new = new[COLUMNS].copy()
    new["Date"] = pd.to_datetime(new["Date"])
    st.session_state.df = new
    st.toast("Data loaded.")


def reset_data():
    st.session_state.df = st.session_state.sample.copy()
    st.toast("Sample data restored.")


df = st.session_state.df

st.title("Data Explorer")
st.write(f"The app currently holds **{len(df)} students**.")

col1, col2 = st.columns(2)

with col1:
    #Download the current data
    st.download_button(
        "Download current data (CSV)",
        data=df.to_csv(index=False),
        file_name="students.csv",
        mime="text/csv",
    )

with col2:
    st.button("Reset to sample data", on_click=reset_data)

st.divider()

# Upload CSV
uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

if uploaded_file is not None:
    new = pd.read_csv(uploaded_file)
    missing = [c for c in COLUMNS if c not in new.columns]

    if missing:
        st.error(f"Missing columns: {missing}")
    else:
        st.write("Here's a preview of your data:")
        st.dataframe(new.head(), hide_index=True)
        st.button("Use this data in the app", on_click=load_data, args=(new,))

st.divider()

#Explore the current data
st.subheader("Explore the current data")

numeric = df.select_dtypes(include="number").columns.tolist()

if df.empty or not numeric:
    st.info("There is no numeric data to explore.")
else:
    column = st.selectbox("Column", numeric)
    bins = st.slider("Number of bins", 5, 30, 10)

    col1, col2 = st.columns(2)
    with col1:
        fig, ax = plt.subplots()
        sns.histplot(data=df, x=column, bins=bins, kde=True, ax=ax)
        ax.set_title(f"Distribution of {column}")
        st.pyplot(fig)
    with col2:
        st.write(df[column].describe().round(2))
