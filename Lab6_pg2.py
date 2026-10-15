import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import streamlit as st

df = st.session_state.df
all_groups = sorted(df["Group"].unique())

st.header("Section 1")
st.write("Streamlit Graphs")

#sidebar filters
with st.sidebar:
    st.subheader("Filters")
    groups = st.multiselect("Groups", all_groups, default=all_groups)
    low, high = st.slider("Score range", 0, 100, (0, 100))
    lab_only = st.toggle("Only students who attended the lab")
    palette = st.selectbox("Seaborn palette", ["deep", "pastel", "muted", "Set2"])

data = df[df["Group"].isin(groups) & df["Score"].between(low, high)]
if lab_only:
    data = data[data["Lab"]]

if data.empty:
    st.warning("No students match the filters.")
    st.stop()

with st.expander("View Details"):
    st.write(f"{len(data)} of {len(df)} students are shown. Change the filters in the sidebar.")

col1, col2 = st.columns(2)
with col1:
    #Dataframe
    st.caption("DataFrame: ")
    st.dataframe(data, hide_index=True)

    #line chart
    st.caption("Line chart: average score per exam date")
    st.line_chart(data.groupby("Date")["Score"].mean(), y_label="Score", color="#ff006aa4")

with col2:
    #Table
    st.caption("Table: ")
    st.table(data[["Hours", "Score"]].describe().round(1))

    #bar chart
    st.caption("Bar chart: average score per group")
    st.bar_chart(data.groupby("Group")["Score"].mean())

#scatter chart
st.caption("Scatter chart: ")
st.scatter_chart(data, x="Hours", y="Score", color="Group")

st.divider()

st.header("Section 2")
st.write("Plots with Matplotlib")

col1, col2 = st.columns(2)

with col1:
    st.caption("Scatter with a trend line")
    fig, ax = plt.subplots()
    ax.scatter(data["Hours"], data["Score"], alpha=0.6)
    if len(data) > 1 and data["Hours"].nunique() > 1:
        slope, intercept = np.polyfit(data["Hours"], data["Score"], 1)
        x = np.linspace(data["Hours"].min(), data["Hours"].max(), 50)
        ax.plot(x, slope * x + intercept, color="red", label="Trend")
        ax.legend()
    ax.set_xlabel("Hours")
    ax.set_ylabel("Score")
    st.pyplot(fig)

with col2:
    st.caption("Histogram of scores")
    fig, ax = plt.subplots()
    ax.hist(data["Score"], bins=10, edgecolor="white")
    ax.axvline(50, color="red", linestyle="--", label="Pass mark")
    ax.set_xlabel("Score")
    ax.set_ylabel("Students")
    ax.legend()
    st.pyplot(fig)

st.divider()

st.header("Section 3")
st.write("Plots with Seaborn")

#one theme and palette for all the Seaborn plots below
sns.set_theme(style="whitegrid", palette=palette)

col1, col2 = st.columns(2)

with col1:
    st.caption("Boxplot: scores per group")
    fig, ax = plt.subplots()
    sns.boxplot(data=data, x="Group", y="Score", hue="Group", order=all_groups,
                hue_order=all_groups, legend=False, ax=ax)
    st.pyplot(fig)

    st.caption("Histogram with density curve")
    fig, ax = plt.subplots()
    sns.histplot(data=data, x="Score", hue="Group", hue_order=all_groups,
                 kde=True, element="step", ax=ax)
    st.pyplot(fig)

with col2:
    st.caption("Scatterplot: hours vs score")
    fig, ax = plt.subplots()
    sns.scatterplot(data=data, x="Hours", y="Score", hue="Group",
                    hue_order=all_groups, style="Lab", ax=ax)
    st.pyplot(fig)

    st.caption("Heatmap: correlations")
    fig, ax = plt.subplots()
    corr = data[["Hours", "Score", "Lab"]].astype(float).corr()
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", vmin=-1, vmax=1, ax=ax)
    st.pyplot(fig)
