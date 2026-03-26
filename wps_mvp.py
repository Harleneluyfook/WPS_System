import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

st.set_page_config(page_title="WPS Dashboard", layout="wide")

st.title("🏥 Weighted Priority Scheduler")
st.caption("Disaster Response Prioritization System")

# -------------------------
# SAMPLE BARANGAY DATA
# -------------------------
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
("Bal-Marcoville (Marcoville)",26),
("Balsigan",40),
("Bayan Park East",11),
("Bayan Park Village",63),
("Bayan Park West (Bayan Park)",57),
("Bgh Compound",69),
("Brookside",261),
("Brookspoint",43),
("Cabinet Hill-Teacher's Camp",54),
("Camdas Subdivision",14),
("Camp 7",137),
("Camp 8",33),
("Camp Allen",27),
("Campo Filipino",84),
("City Camp Central",308),
("City Camp Proper",18),
("Country Club Village",5),
("Cresencia Village",33),
("Dagsian, Lower",40),
("Dagsian, Upper",18),
("Dizon Subdivision",57),
("Dominican Hill-Mirador",164),
("Dontogan",75),
("Dps Area",20),
("Engineers Hill",19),
("Fairview Village",83),
("Ferdinand (Happy Homes-Campo Sioco)",54),
("Fort Del Pilar",21),
("Gabriela Silang",19),
("Gibraltar",34),
("Greenwater Village",47),
("Guisad Central",46),
("Guisad Sorong",117),
("Happy Hollow",67),
("Harrison-Claudio Carantes",325),
("Hillside",24),
("Holy Ghost Extension",29),
("Honeymoon (Honeymoon-Holy Ghost)",121),
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

# Add RANDOM values for missing columns
np.random.seed(1)
df["Casualties"] = np.random.randint(0, 20, size=len(df))
df["Damaged Houses"] = np.random.randint(10, 300, size=len(df))

# -------------------------
# NORMALIZATION FUNCTION
# -------------------------
def normalize(col):
    return (col - col.min()) / (col.max() - col.min())

df["Norm_Casualties"] = normalize(df["Casualties"])
df["Norm_Affected"] = normalize(df["Affected Families"])
df["Norm_Damaged"] = normalize(df["Damaged Houses"])

df["Priority Score"] = (
    df["Norm_Casualties"] +
    df["Norm_Affected"] +
    df["Norm_Damaged"]
) / 3

df = df.sort_values("Priority Score", ascending=False).reset_index(drop=True)

# -------------------------
# USER INPUT (clean UI)
# -------------------------
st.subheader("Select Barangay")

selected = st.selectbox(
    "Choose a barangay",
    df["Barangay"].tolist()
)

selected_row = df[df["Barangay"] == selected].iloc[0]

st.markdown("### 📍 Selected Barangay Overview")
col1, col2, col3 = st.columns(3)

col1.metric("Affected Families", int(selected_row["Affected Families"]))
col2.metric("Casualties", int(selected_row["Casualties"]))
col3.metric("Damaged Houses", int(selected_row["Damaged Houses"]))

st.markdown("---")

# -------------------------
# PRIORITY RANKING (USER FRIENDLY)
# -------------------------
st.subheader("🚨 Priority Ranking")

for i, row in df.head(10).iterrows():
    if i == 0:
        badge = "🥇 TOP PRIORITY"
    elif i == 1:
        badge = "🥈 NEXT"
    elif i == 2:
        badge = "🥉 THIRD"
    else:
        badge = f"#{i+1}"

    highlight = "background-color:#fff3cd;" if row["Barangay"] == selected else ""

    st.markdown(f"""
    <div style="padding:12px; border-radius:10px; margin:6px 0; {highlight}">
        <strong>{badge} - {row['Barangay']}</strong><br>
        Score: {row['Priority Score']:.3f}  
        | Families: {int(row['Affected Families'])}  
        | Casualties: {int(row['Casualties'])}  
        | Damaged: {int(row['Damaged Houses'])}
    </div>
    """, unsafe_allow_html=True)

# -------------------------
# SIMPLE TIMELINE (FLARE ✨)
# -------------------------
st.markdown("---")
st.subheader("⏱️ Estimated Response Timeline")

rank = df[df["Barangay"] == selected].index[0] + 1

if rank == 1:
    msg = "🚨 Immediate response (within 24 hours)"
elif rank <= 3:
    msg = "⚠️ Urgent response (24–48 hours)"
elif rank <= 6:
    msg = "📅 Scheduled (2–3 days)"
else:
    msg = "⏳ Monitoring / delayed response"

st.info(f"**{selected} is ranked #{rank}** → {msg}")
