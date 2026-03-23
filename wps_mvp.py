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
# File uploader (CSV)
# -------------------------
uploaded_file = st.file_uploader(
    "Upload CSV file", type=["csv"]
)

# -------------------------
# Load data
# -------------------------
if uploaded_file is None:
    st.info("Using sample data. Upload a CSV to use your own dataset.")
    data = {
        "Region": ["Region A", "Region B", "Region C"],
        "Casualties": [5, 2, 8],
        "Affected Families": [100, 150, 80],
        "Damaged Houses": [20, 10, 30]
    }
    df = pd.DataFrame(data)
else:
    df = pd.read_csv(uploaded_file)

# -------------------------
# Strip spaces from column names
# -------------------------
df.columns = df.columns.str.strip()

# -------------------------
# Display input data
# -------------------------
st.subheader("Input Data")
st.dataframe(df)

# -------------------------
# Expected columns
# -------------------------
expected_cols = ["Region", "Casualties", "Affected Families", "Damaged Houses"]

missing_cols = [col for col in expected_cols if col not in df.columns]
if missing_cols:
    st.error(f"The following required columns are missing: {missing_cols}")
    st.write("Columns found in your file:", df.columns.tolist())
    st.stop()  # Stop execution to avoid errors

# -------------------------
# Convert numeric columns to float (safe)
# -------------------------
numeric_cols = ["Casualties", "Affected Families", "Damaged Houses"]
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")  # convert strings to NaN

# Fill NaNs with 0
df[numeric_cols] = df[numeric_cols].fillna(0)

# -------------------------
# Normalization function
# -------------------------
def normalize(column):
    if column.max() == column.min():
        return column * 0
    return (column - column.min()) / (column.max() - column.min())

# Apply normalization
df["Norm_Casualties"] = normalize(df["Casualties"])
df["Norm_Affected"] = normalize(df["Affected Families"])
df["Norm_Damaged"] = normalize(df["Damaged Houses"])

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
st.bar_chart(df_sorted.set_index("Region")["Priority Score"])
