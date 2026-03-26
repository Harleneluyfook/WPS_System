import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# -------------------------
# PAGE CONFIG
# -------------------------
st.set_page_config(
    page_title="WPS Disaster Prioritization",
    layout="wide"
)

st.title("Baguio City Disaster Prioritization")
st.caption("Weighted Priority Scheduler for Disaster Response")

# -------------------------
# SAMPLE BARANGAYS (replace later with full 128)
# -------------------------
barangays = [
    "Session Road Area",
    "Burnham Park",
    "Camp 7",
    "Loakan",
    "Bakakeng",
    "Irisan",
    "Aurora Hill",
    "Pinsao",
    "Engineer’s Hill",
    "Upper QM"
]

# -------------------------
# SESSION STATE
# -------------------------
if "entries" not in st.session_state:
    st.session_state.entries = []

# -------------------------
# FUNCTIONS
# -------------------------
def normalize(col):
    if len(col) == 0:
        return col
    if col.max() == col.min():
        return col * 0
    return (col - col.min()) / (col.max() - col.min())

def compute_priority(df):
    df["Norm_Casualties"] = normalize(df["Casualties"])
    df["Norm_Affected"] = normalize(df["Affected"])
    df["Norm_Damaged"] = normalize(df["Damaged"])

    df["Score"] = (
        df["Norm_Casualties"] +
        df["Norm_Affected"] +
        df["Norm_Damaged"]
    ) / 3

    return df

# -------------------------
# TABS (like dengue dashboard)
# -------------------------
tab1, tab2 = st.tabs(["Data Entry", "Prioritization"])

# ======================
# TAB 1: INPUT
# ======================
with tab1:
    st.header("Enter Disaster Data")

    with st.form("form"):
        col1, col2 = st.columns(2)

        with col1:
            barangay = st.selectbox("Select Barangay", barangays)
            casualties = st.number_input("Casualties", min_value=0, step=1)

        with col2:
            affected = st.number_input("Affected Families", min_value=0, step=1)
            damaged = st.number_input("Damaged Houses", min_value=0, step=1)

        submit = st.form_submit_button("Add to Queue")

        if submit:
            st.session_state.entries.append({
                "Barangay": barangay,
                "Casualties": casualties,
                "Affected": affected,
                "Damaged": damaged,
                "Time": datetime.now()
            })
            st.success(f"{barangay} added")

    st.markdown("---")

    if st.session_state.entries:
        st.subheader("Current Entries")
        df = pd.DataFrame(st.session_state.entries)
        st.dataframe(df, use_container_width=True)

# ======================
# TAB 2: RESULTS
# ======================
with tab2:
    st.header("Priority Ranking")

    if not st.session_state.entries:
        st.warning("No data yet. Add entries first.")
    else:
        df = pd.DataFrame(st.session_state.entries)
        df = compute_priority(df)

        df = df.sort_values("Score", ascending=False).reset_index(drop=True)

        st.subheader("Who needs help first?")

        # -------------------------
        # PRIORITY CARDS (user-friendly ranking)
        # -------------------------
        for i, row in df.iterrows():
            rank = i + 1

            if rank == 1:
                badge = "🚨 FIRST PRIORITY"
            elif rank == 2:
                badge = "⚠️ NEXT IN LINE"
            else:
                badge = "📍 QUEUED"

            with st.container():
                st.markdown(f"""
                ### #{rank} {row['Barangay']}
                **{badge}**

                Priority Score: **{row['Score']:.3f}**

                Casualties: {row['Casualties']}  
                Affected Families: {row['Affected']}  
                Damaged Houses: {row['Damaged']}
                """)
                st.markdown("---")

        # -------------------------
        # SIMPLE TIMELINE FEEL
        # -------------------------
        st.subheader("Estimated Response Flow")

        for i, row in df.iterrows():
            if i == 0:
                time = "Immediate response"
            elif i == 1:
                time = "Next 24–48 hours"
            else:
                time = f"After {48 + i*12} hours"

            st.write(f"{i+1}. {row['Barangay']} → {time}")

        # -------------------------
        # CLEAN RECOMMENDATION SECTION
        # -------------------------
        st.subheader("Recommendation")

        top = df.iloc[0]

        st.info(f"""
Focus response on **{top['Barangay']}** first due to highest impact.

Allocate initial resources based on:
- Casualties
- Affected families
- Housing damage

Continue response following the ranking order shown above.
""")
