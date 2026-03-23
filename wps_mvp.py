import streamlit as st
import pandas as pd
import numpy as np

# -------------------------
# Page config
# -------------------------
st.set_page_config(page_title="WPS Disaster Prioritization", layout="wide")

# -------------------------
# Title
# -------------------------
st.title("Weighted Priority Scheduler (WPS)")
st.subheader("Disaster Response Prioritization System")

st.write("""
This system applies the Weighted Sum Model (WSM) with an equal weighting scheme
to prioritize disaster-affected areas based on impact criteria.
""")

# -------------------------
# File upload
# -------------------------
uploaded_file = st.file_uploader("Upload CSV file", type=["csv", "xlxs"])

# -------------------------
# Sample data if no file
# -------------------------
if uploaded_file is None:
    st.info("Using sample data. Upload a CSV to use your own dataset.")
    data = {
        "Barangay": ["A", "B", "C"],
        "Casualties": [5, 2, 8],
        "Affected_Families": [100, 150, 80],
        "Damaged_Houses": [20, 10, 30]
    }
    df = pd.DataFrame(data)
else:
    df = pd.read_csv(uploaded_file)

# -------------------------
# Display input data
# -------------------------
st.subheader("Input Data")
st.dataframe(df)

# -------------------------
# Normalization function
# -------------------------
def normalize(column):
    if column.max() == column.min():
        return column * 0
    return (column - column.min()) / (column.max() - column.min())

# Apply normalization
df["Norm_Casualties"] = normalize(df["Casualties"])
df["Norm_Affected"] = normalize(df["Affected_Families"])
df["Norm_Damaged"] = normalize(df["Damaged_Houses"])

# -------------------------
# Equal weighting (WSM)
# -------------------------
weight = 1/3
df["Priority Score"] = (
    df["Norm_Casualties"] * weight +
    df["Norm_Affected"] * weight +
    df["Norm_Damaged"] * weight
)

# -------------------------
# Sort by priority score
# -------------------------
df_sorted = df.sort_values(by="Priority Score", ascending=False)

# -------------------------
# Results
# -------------------------
st.subheader("Prioritized Results")
st.dataframe(df_sorted)

# -------------------------
# Visualization
# -------------------------
st.subheader("Priority Score Visualization")
st.bar_chart(df_sorted.set_index("Barangay")["Priority Score"])
