import re

import pandas as pd
import streamlit as st


#callbacks run BEFORE the script reruns, so the page below already sees the new data
def add_student():
    name = st.session_state.f_name.strip()
    if not name:
        st.toast("Please enter a name.")
        return
    row = {
        "Name": name,
        "Group": st.session_state.f_group,
        "Hours": st.session_state.f_hours,
        "Score": st.session_state.f_score,
        "Date": pd.Timestamp(st.session_state.f_date),
        "Lab": st.session_state.f_lab,
    }
    st.session_state.df = pd.concat(
        [st.session_state.df, pd.DataFrame([row])], ignore_index=True
    )
    st.toast(f"{name} added.")


def remove_student(index):
    st.session_state.df = st.session_state.df.drop(index).reset_index(drop=True)
    st.toast("Student removed.")


def add_note():
    text = st.session_state.n_text.strip()
    if not text:
        st.toast("The note is empty.")
        return
    st.session_state.notes.append({
        "Student": st.session_state.n_student,
        "Note": text,
        "Time": pd.Timestamp.now().strftime("%d.%m.%Y %H:%M"),
    })
    st.toast("Note saved.")


def delete_note(index):
    st.session_state.notes.pop(index)


#a simple rule-based "assistant": it looks for keywords and answers from the data
def answer(question, df):
    q = question.lower()
    if df.empty:
        return "There are no students yet."

    #a specific student
    for _, row in df.iterrows():
        if re.search(rf"\b{re.escape(row['Name'].lower())}\b", q):
            lab = "attended" if row["Lab"] else "did not attend"
            return (f"{row['Name']} is in group {row['Group']}: {row['Hours']} study hours, "
                    f"score {row['Score']:.0f}, {lab} the lab.")

    #a specific group
    sub, label = df, "all groups"
    for g in sorted(df["Group"].unique()):
        if re.search(rf"\bgroup {g.lower()}\b", q):
            sub, label = df[df["Group"] == g], f"group {g}"

    per_group = ", ".join(
        f"{g}: {m:.1f}" for g, m in df.groupby("Group")["Score"].mean().items()
    )

    if "how many" in q or "count" in q or "number of" in q:
        return f"There are {len(sub)} students in {label}."
    if "average" in q or "mean" in q:
        if "hour" in q:
            return f"The average study time in {label} is {sub['Hours'].mean():.1f} hours."
        if label == "all groups" and "group" in q:
            return f"Average score per group: {per_group}"
        return f"The average score in {label} is {sub['Score'].mean():.1f}."
    if any(w in q for w in ["worst", "lowest", "weakest"]):
        low = sub.nsmallest(3, "Score")
        return f"Lowest scores in {label}: " + ", ".join(f"{r.Name} ({r.Score:.0f})" for r in low.itertuples())
    if any(w in q for w in ["best", "top", "highest"]):
        top = sub.nlargest(3, "Score")
        return f"Top students in {label}: " + ", ".join(f"{r.Name} ({r.Score:.0f})" for r in top.itertuples())
    if "pass" in q or "fail" in q:
        passed = int((sub["Score"] >= 50).sum())
        return f"In {label}, {passed} of {len(sub)} students passed ({passed / len(sub):.0%})."
    if "lab" in q:
        yes, no = sub[sub["Lab"]], sub[~sub["Lab"]]
        text = f"{len(yes)} of {len(sub)} students in {label} attended the lab."
        if not yes.empty and not no.empty:
            text += f" Their average score is {yes['Score'].mean():.1f}, against {no['Score'].mean():.1f} for the others."
        return text
    if "group" in q:
        return f"Average score per group: {per_group}"

    return ("I can answer about counts, averages, best and worst students, the pass rate, "
            "the lab, groups, or a student by name.")


df = st.session_state.df

st.title("Student Study Tracker")

# display text using Markdown formatting
st.markdown("**Log students, explore the results and share the data.**")
st.caption("Everything you change here appears on the Graphs and Files pages.")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Overview",
    "Add student",
    "Manage",
    "Ask",
    "Notes"
])


with tab1:
    if df.empty:
        st.info("No data yet. Add a student or upload a file.")
    else:
        #columns + metric
        col1, col2, col3 = st.columns(3)
        col1.metric("Students", len(df))
        col2.metric("Average score", round(df["Score"].mean(), 1))
        col3.metric("Average hours", round(df["Hours"].mean(), 1))

        #progress bar
        pass_rate = (df["Score"] >= 50).mean()
        st.progress(pass_rate, text=f"Pass rate: {pass_rate:.0%}")

        #status messages
        best = df.loc[df["Score"].idxmax()]
        worst = df.loc[df["Score"].idxmin()]
        st.success(f"Top score: {best['Name']} ({best['Score']:.0f})")
        st.warning(f"Lowest score: {worst['Name']} ({worst['Score']:.0f})")

        #latex and code
        st.latex(r"\text{pass rate} = \frac{\text{students with score} \geq 50}{\text{all students}}")
        st.code('pass_rate = (df["Score"] >= 50).mean()', language="python")

        #expander + json
        with st.expander("Raw summary"):
            st.json({
                "students": len(df),
                "per group": {k: int(v) for k, v in df["Group"].value_counts().sort_index().items()},
            })


with tab2:
    #container with border
    with st.container(border=True):
        #form: nothing reruns until the button is pressed
        with st.form("add_student", clear_on_submit=True):
            col1, col2 = st.columns(2)

            #text input
            col1.text_input("Name", key="f_name")

            #radio button
            col1.radio("Group", ["A", "B", "C", "D"], horizontal=True, key="f_group")

            #date input
            col2.date_input("Exam date", key="f_date")

            #toggle
            col2.toggle("Attended the lab", key="f_lab")

            #slider
            st.slider("Study hours", 0.0, 10.0, 5.0, step=0.5, key="f_hours")

            #number input
            st.number_input("Exam score", min_value=0, max_value=100, value=50, key="f_score")

            st.form_submit_button("Add student", on_click=add_student)


with tab3:
    #text input + checkbox as filters
    search = st.text_input("Search by name")
    only_passed = st.checkbox("Only students who passed")

    view = df
    if search:
        view = view[view["Name"].str.contains(search, case=False)]
    if only_passed:
        view = view[view["Score"] >= 50]

    st.dataframe(view, hide_index=True)
    st.caption(f"{len(view)} of {len(df)} students")

    with st.expander("Remove a student"):
        if df.empty:
            st.write("Nothing to remove.")
        else:
            who = st.selectbox(
                "Student",
                df.index,
                format_func=lambda i: f"{df.loc[i, 'Name']} (group {df.loc[i, 'Group']})",
            )
            #popover as a confirmation box
            with st.popover("Remove"):
                st.write("This cannot be undone.")
                st.button("Confirm removal", on_click=remove_student, args=(who,))


with tab4:
    st.caption("Try: How many students are in group A? / Who are the best students in group B? / Tell me about Student 1")

    #chat
    messages = st.container(height=300, border=True)
    if prompt := st.chat_input("Ask about the students"):
        st.session_state.chat.append({"role": "user", "content": prompt})
        st.session_state.chat.append({"role": "assistant", "content": answer(prompt, df)})
    for msg in st.session_state.chat:
        messages.chat_message(msg["role"]).write(msg["content"])


with tab5:
    with st.container(border=True):
        with st.form("add_note", clear_on_submit=True):
            #dropdown selection
            st.selectbox("About", ["General"] + df["Name"].tolist(), key="n_student")

            #multi-line text input
            st.text_area("Note", key="n_text")

            st.form_submit_button("Save note", on_click=add_note)

    notes = st.session_state.notes
    st.caption(f"{len(notes)} notes")

    #newest first
    for i in reversed(range(len(notes))):
        with st.container(border=True):
            st.markdown(f"**{notes[i]['Student']}** - {notes[i]['Time']}")
            st.write(notes[i]["Note"])
            st.button("Delete", key=f"delete_{i}", on_click=delete_note, args=(i,))