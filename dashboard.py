import streamlit as st
import pandas as pd
import time
import os
import json

st.set_page_config(
    page_title="🚨 AI Log Monitor",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🚀 Real-Time AI Log Analyzer")
st.caption("Powered by Pathway + Gemini + Transformers")

# ==============================
# Helper to load latest logs
# ==============================
def load_logs():
    file_path = "./alerts/enhanced_logs.json"
    if not os.path.exists(file_path):
        return pd.DataFrame(columns=["log", "classification", "explanation", "time"])

    # Read JSON lines safely
    with open(file_path, "r") as f:
        lines = [json.loads(line) for line in f if line.strip()]
    df = pd.DataFrame(lines)

    # Convert timestamps to readable times
    if "time" in df.columns:
        df["time"] = pd.to_datetime(df["time"], unit="ms")
    return df

# ==============================
# Sidebar Controls
# ==============================
refresh_rate = st.sidebar.slider("⏱ Refresh every (seconds):", 2, 20, 5)
filter_choice = st.sidebar.multiselect(
    "🔍 Filter by classification:",
    ["critical", "warning", "normal", "unknown"],
    default=["critical", "warning", "normal"]
)

# ==============================
# Live Dashboard
# ==============================
placeholder = st.empty()

while True:
    df = load_logs()
    if not df.empty:
        df = df[df["classification"].isin(filter_choice)]

        with placeholder.container():
            st.subheader("📊 Live Log Feed")
            st.dataframe(df.tail(20), use_container_width=True)

            st.markdown("---")
            st.subheader("📈 Classification Summary")
            summary = df["classification"].value_counts().reset_index()
            summary.columns = ["classification", "count"]
            st.bar_chart(summary.set_index("classification"))

            st.markdown("---")
            st.subheader("💬 Recent Critical Explanations")
            for _, row in df[df["classification"] == "critical"].tail(3).iterrows():
                st.error(f"**{row['log']}**\n\n> {row['explanation']}")
    else:
        st.info("Waiting for logs to appear...")

    time.sleep(refresh_rate)
