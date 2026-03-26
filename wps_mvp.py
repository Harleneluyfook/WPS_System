import streamlit as st
import pandas as pd
from datetime import datetime

# -------------------------
# Page config
# -------------------------
st.set_page_config(page_title="WPS Disaster Prioritization", layout="wide")

# -------------------------
# Session state
# -------------------------
if 'lgu_entries' not in st.session_state:
    st.session_state.lgu_entries = []

# -------------------------
# Sample Barangay List (replace later with full 128)
# -------------------------
barangay_list = [
    "Abanao-Zandueta-Kayong-Chugum-Otek",
    "Alfonso Tabora",
    "Andres Bonifacio",
    "Aurelio Mendoza",
    "Camp 7",
    "Camp 8",
    "Dominican Hill",
    "Irisan",
    "Loakan Proper",
    "Sample Barangay A",
    "Sample Barangay B"
]

# -------------------------
# Normalize function
# -------------------------
def normalize(column):
    if len(column) == 0:
        return column
    if column.max() == column.min():
        return column * 0
    return (column - column.min()) / (column.max() - column.min())

# -------------------------
# Priority Calculation
# -------------------------
def calculate_priorities(df):
    if len(df) == 0:
        return df

    df['Norm_Casualties'] = normalize(df['Casualties'])
    df['Norm_Affected'] = normalize(df['Affected Families'])
    df['Norm_Damaged'] = normalize(df['Damaged Houses'])

    weight = 1/3
    df['Priority Score'] = (
        df['Norm_Casualties'] * weight +
        df['Norm_Affected'] * weight +
        df['Norm_Damaged'] * weight
    )

    return df

# -------------------------
# Title
# -------------------------
st.title("Weighted Priority Scheduler (WPS)")
st.caption("Simple disaster prioritization tool")

# -------------------------
# Tabs
# -------------------------
tab1, tab2 = st.tabs(["Data Entry", "Results"])

# ================= TAB 1 =================
with tab1:
    st.subheader("Enter Disaster Data")

    with st.form("input_form"):
        col1, col2 = st.columns(2)

        with col1:
            region_name = st.selectbox("Select Barangay", barangay_list)
            casualties = st.number_input("Casualties", min_value=0, value=0)

        with col2:
            affected = st.number_input("Affected Families", min_value=0, value=0)
            damaged = st.number_input("Damaged Houses", min_value=0, value=0)

        submit = st.form_submit_button("Add to Queue")

        if submit:
            new_entry = {
                "Region": region_name,
                "Casualties": casualties,
                "Affected Families": affected,
                "Damaged Houses": damaged,
                "Timestamp": datetime.now()
            }

            st.session_state.lgu_entries.append(new_entry)

            df_temp = pd.DataFrame(st.session_state.lgu_entries)
            df_temp = calculate_priorities(df_temp)

            st.session_state.lgu_entries = df_temp.to_dict("records")

            st.success(f"{region_name} added to queue.")

    # -------------------------
    # Queue Display
    # -------------------------
    st.markdown("---")
    st.subheader("Current Queue")

    if st.session_state.lgu_entries:
        df = pd.DataFrame(st.session_state.lgu_entries)
        df_sorted = df.sort_values("Priority Score", ascending=False).reset_index(drop=True)

        for i, row in df_sorted.iterrows():
            st.markdown(f"### {i+1}. {row['Region']}")
            st.write(f"Priority Score: {row['Priority Score']:.3f}")
            st.write(f"Casualties: {int(row['Casualties'])}")
            st.write(f"Affected Families: {int(row['Affected Families'])}")
            st.write(f"Damaged Houses: {int(row['Damaged Houses'])}")
            st.markdown("---")

        if st.button("Clear All"):
            st.session_state.lgu_entries = []
            st.rerun()

    else:
        st.info("No data yet.")

# ================= TAB 2 =================
with tab2:
    st.subheader("Results")

    if st.session_state.lgu_entries:
        df = pd.DataFrame(st.session_state.lgu_entries)
        df_sorted = df.sort_values("Priority Score", ascending=False).reset_index(drop=True)

        # Chart
        st.bar_chart(df_sorted.set_index("Region")["Priority Score"])

        # Table
        st.dataframe(
            df_sorted[['Region', 'Priority Score', 'Casualties', 'Affected Families', 'Damaged Houses']],
            use_container_width=True
        )

        # -------------------------
        # Simple Response Plan
        # -------------------------
        st.markdown("---")
        st.subheader("Response Plan")

        for idx, row in df_sorted.iterrows():

            if row['Priority Score'] >= 0.66:
                priority = "High"
                icon = "🔴"
                eta = "Immediate (within 24 hrs)"
            elif row['Priority Score'] >= 0.33:
                priority = "Medium"
                icon = "🟡"
                eta = "Within 24–72 hrs"
            else:
                priority = "Low"
                icon = "🟢"
                eta = "After 72 hrs"

            if idx == 0:
                wait = "No wait time"
            else:
                wait = f"~{idx * 12} hrs after previous"

            st.markdown(f"""
            **{idx + 1}. {row['Region']}**  
            {icon} Priority: {priority}  
            ⏱ Estimated Response: {eta}  
            ⌛ Queue Delay: {wait}
            """)

            st.markdown("---")

    else:
        st.warning("No data available.")
