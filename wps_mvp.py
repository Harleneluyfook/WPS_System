import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="WPS Dashboard", layout="wide")

st.title("Weighted Priority Scheduler")
st.caption("Disaster Response Prioritization System")

# FUNCTIONS
def normalize(col):
    if col.max() == col.min():
        return col * 0
    return (col - col.min()) / (col.max() - col.min())

def compute_priority(df):
    df["Norm_Casualties"] = normalize(df["Casualties"])
    df["Norm_Affected"] = normalize(df["Affected Families"])
    df["Norm_Damaged"] = normalize(df["Damaged Houses"])

    # Equal weights (WSM)
    w1, w2, w3 = 0.33, 0.33, 0.33

    df["Priority Score"] = (
        df["Norm_Casualties"] * w1 +
        df["Norm_Affected"] * w2 +
        df["Norm_Damaged"] * w3
    )

    return df.sort_values("Priority Score", ascending=False).reset_index(drop=True)

# INITIALIZE QUEUE
if "df" not in st.session_state:
    data = [
        ("A. Bonifacio-Caguioa-Rimando (Abcr)",15),
        ("Abanao-Zandueta-Kayong-Chugum-Otek (Azkco)",284),
        ("Alfonso Tabora",26),
        ("Ambiong",40),
        ("Andres Bonifacio (Lower Bokawkan)",37),
        ("Apugan-Loakan",58),
        ("Asin Road",356),
        ("Atok Trail",398),
        ("Aurora Hill Proper (Malvar-Sgt. Floresca)",20),
        ("Aurora Hill, North Central",58),
        ("Aurora Hill, South Central",62),
        ("Bakakeng Central",112),
        ("Bakakeng North",35),
        ("Balsigan",40),
        ("Brookside",261),
        ("Camp 7",137),
        ("Campo Filipino",84),
        ("City Camp Central",308),
        ("Dominican Hill-Mirador",164),
        ("Harrison-Claudio Carantes",325),
        ("Irisan",989),
        ("Kias",181),
        ("Outlook Drive",96),
        ("Padre Burgos",103),
        ("Pinget",112),
        ("Rock Quarry, Lower",195),
        ("San Luis Village",113),
        ("Session Road Area",45),
        ("Teodora Alonzo",120),
        ("Trancoville",22)
    ]

    df = pd.DataFrame(data, columns=["Barangay", "Affected Families"])

    # Random baseline disaster data
    np.random.seed(1)
    df["Casualties"] = np.random.randint(0, 20, size=len(df))
    df["Damaged Houses"] = np.random.randint(10, 300, size=len(df))

    df = compute_priority(df)

    st.session_state.df = df
    st.session_state.selected_barangay = None

df = st.session_state.df

# TABS
tab1, tab2 = st.tabs(["Input", "Results"])

# TAB 1 — INPUT
with tab1:
    st.subheader("Barangay Disaster Input")

    selected = st.selectbox(
        "Choose Barangay",
        df["Barangay"].tolist()
    )

    st.markdown("### Enter Disaster Impact Data")

    col1, col2, col3 = st.columns(3)

    with col1:
        casualties = st.number_input("Casualties", min_value=0, step=1)

    with col2:
        affected = st.number_input("Affected Families", min_value=0, step=1)

    with col3:
        damaged = st.number_input("Damaged Houses", min_value=0, step=1)

    if st.button("Add to Assessment"):
        df = st.session_state.df

        # Update selected barangay
        df.loc[df["Barangay"] == selected, "Casualties"] = casualties
        df.loc[df["Barangay"] == selected, "Affected Families"] = affected
        df.loc[df["Barangay"] == selected, "Damaged Houses"] = damaged

        # Recompute priority queue
        df = compute_priority(df)

        st.session_state.df = df
        st.session_state.selected_barangay = selected

        st.success(f"{selected} updated and queue reordered")

# TAB 2 — RESULTS
with tab2:
    st.subheader("Disaster Priority Overview")

    df = st.session_state.df
    selected = st.session_state.selected_barangay

    if selected is None:
        st.warning("Please select and input data in the Input tab first.")
    else:
        selected_row = df[df["Barangay"] == selected].iloc[0]
        rank = df[df["Barangay"] == selected].index[0] + 1
        total = len(df)

        # In QUEUE
        top = df.iloc[0]

        st.markdown("##  Highest Priority Area")
        st.markdown(f"""
        <div style="
            padding:15px;
            border-radius:10px;
            background-color:#ffe5e5;
            border-left:6px solid #ff4b4b;
        ">
            <strong>{top['Barangay']}</strong><br>
            Score: {top['Priority Score']:.3f} |
            Affected: {int(top['Affected Families'])} |
            Casualties: {int(top['Casualties'])} |
            Damaged: {int(top['Damaged Houses'])}
        </div>
        """, unsafe_allow_html=True)

        # BARANGAY STATUS
        st.markdown("---")
        st.markdown("##  Your Barangay Status")

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Rank", f"#{rank}")
        col2.metric("Out of", total)
        col3.metric("Priority Score", f"{selected_row['Priority Score']:.3f}")

        if rank == 1:
            level = "HIGH PRIORITY"
        elif rank <= 5:
            level = "MEDIUM PRIORITY"
        else:
            level = "LOW PRIORITY"

        col4.metric("Priority Level", level)

        #  RESPONSE
        st.markdown("---")
        st.markdown("##  Response Plan")

        if rank == 1:
            msg = "Immediate response (within 24 hours)"
        elif rank <= 3:
            msg = "Urgent (24–48 hours)"
        elif rank <= 6:
            msg = "Scheduled (2–3 days)"
        else:
            msg = "Monitoring / delayed response"

        st.info(msg)

        #  POSITION
        st.markdown("###  Position in Queue")
        # Create number line
        numbers = [str(i+1) for i in range(total)]
        markers = ["   "] * total
        markers[rank - 1] = " 🔴 "
        st.markdown(" ".join(numbers))
        st.markdown(" ".join(markers))
        st.caption(f"You are at position #{rank} out of {total}")

        # FULL QUEUE (MAIN FEATURE)
        st.markdown("---")
        st.markdown("##  Priority Queue")

        df_display = df.copy()
        df_display["Rank"] = df_display.index + 1

        for i, row in df_display.iterrows():
            r = int(row["Rank"])

            # Softer colors (clean UI)
            if r == 1:
                bg = "#ffe5e5"
                border = "#ff4b4b"
            elif r <= 3:
                bg = "#fff4e5"
                border = "#ffa500"
            elif r <= 10:
                bg = "#e6f0ff"
                border = "#4b8bff"
            else:
                bg = "#f5f5f5"
                border = "#999"

            st.markdown(f"""
            <div style="
                padding:10px;
                margin:6px 0;
                border-radius:8px;
                background-color:{bg};
                border-left:5px solid {border};
            ">
                <strong>#{r} — {row['Barangay']}</strong><br>
                Score: {row['Priority Score']:.3f} |
                Affected: {int(row['Affected Families'])} |
                Casualties: {int(row['Casualties'])} |
                Damaged: {int(row['Damaged Houses'])}
            </div>
            """, unsafe_allow_html=True)

        # DETAILS
        st.markdown("---")
        st.markdown("##  Impact Breakdown")

        col1, col2, col3 = st.columns(3)

        col1.metric("Affected Families", int(selected_row["Affected Families"]))
        col2.metric("Casualties", int(selected_row["Casualties"]))
        col3.metric("Damaged Houses", int(selected_row["Damaged Houses"]))

