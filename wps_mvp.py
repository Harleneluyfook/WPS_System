import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# -------------------------
# PAGE CONFIG
# -------------------------
st.set_page_config(
    page_title="Baguio WPS Dashboard",
    layout="wide"
)

st.title("Baguio City Disaster Prioritization Dashboard")
st.caption("Weighted Priority Scheduler for Disaster Response")

# -------------------------
# SAMPLE BARANGAYS (replace later with full 128)
# -------------------------
barangays = [
    "Abanao-Zandueta-Kayong-Chugum-Otek",
    "Alfonso Tabora",
    "Andres Bonifacio",
    "Aurora Hill Proper",
    "Bakakeng Central",
    "Bal-Marcoville",
    "Balsigan",
    "Cabinet Hill-Teacher's Camp",
    "Camp 7",
    "City Camp Proper"
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
    df["Norm_Families"] = normalize(df["Affected Families"])
    df["Norm_Houses"] = normalize(df["Damaged Houses"])

    df["Priority Score"] = (
        df["Norm_Casualties"] +
        df["Norm_Families"] +
        df["Norm_Houses"]
    ) / 3

    return df

# -------------------------
# TABS
# -------------------------
tab1, tab2 = st.tabs(["Data Entry", "Results"])

# =========================
# TAB 1: INPUT
# =========================
with tab1:
    st.header("Barangay Impact Input")

    with st.form("input_form"):
        col1, col2, col3 = st.columns(3)

        with col1:
            barangay = st.selectbox("Select Barangay", barangays)

        with col2:
            casualties = st.number_input("Casualties", 0, 10000, 0)

        with col3:
            families = st.number_input("Affected Families", 0, 100000, 0)

        houses = st.number_input("Damaged Houses", 0, 100000, 0)

        submit = st.form_submit_button("Add Entry")

        if submit:
            new_data = {
                "Barangay": barangay,
                "Casualties": casualties,
                "Affected Families": families,
                "Damaged Houses": houses,
                "Time": datetime.now()
            }

            st.session_state.entries.append(new_data)

            df = pd.DataFrame(st.session_state.entries)
            df = compute_priority(df)

            st.session_state.entries = df.to_dict("records")

            st.success(f"{barangay} added successfully")

    st.markdown("---")

    st.subheader("Current Entries")

    if st.session_state.entries:
        df = pd.DataFrame(st.session_state.entries)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No data yet")

# =========================
# TAB 2: RESULTS
# =========================
with tab2:
    st.header("Priority Ranking")

    if not st.session_state.entries:
        st.warning("No data available")
    else:
        df = pd.DataFrame(st.session_state.entries)
        df = df.sort_values("Priority Score", ascending=False).reset_index(drop=True)

        st.subheader("Ranking Overview")

        for i, row in df.iterrows():
            if row["Priority Score"] >= 0.66:
                tag = "HIGH PRIORITY"
            elif row["Priority Score"] >= 0.33:
                tag = "MEDIUM PRIORITY"
            else:
                tag = "LOW PRIORITY"

            st.markdown(f"""
            ### #{i+1} {row['Barangay']}
            Priority Score: **{row['Priority Score']:.3f}**  
            {tag}  
            
            Casualties: {int(row['Casualties'])}  
            Families: {int(row['Affected Families'])}  
            Houses: {int(row['Damaged Houses'])}  
            """)

            st.markdown("---")

        # -------------------------
        # RESPONSE TIMELINE (simple, clean)
        # -------------------------
        st.subheader("Estimated Response Order")

        for i, row in df.iterrows():
            if i == 0:
                time = "Immediate response (within 24 hrs)"
            elif i == 1:
                time = "Next deployment (24–48 hrs)"
            elif i == 2:
                time = "Scheduled (48–72 hrs)"
            else:
                time = f"Queue position {i+1}"

            st.write(f"{i+1}. {row['Barangay']} — {time}")

        # -------------------------
        # SIMPLE RECOMMENDATION
        # -------------------------
        st.markdown("---")
        st.subheader("Recommendation Summary")

        total = len(df)
        high = len(df[df["Priority Score"] >= 0.66])

        st.info(
            f"{high} out of {total} barangays require immediate response. "
            "Resources should be focused on the highest-ranked areas first."
        )
