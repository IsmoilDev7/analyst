import streamlit as st
import pandas as pd
import plotly.express as px

# =============================
# PAGE CONFIG
# =============================
st.set_page_config(page_title="CRM Analytics Dashboard", layout="wide")
st.title("📊 CRM Leads Analytics Dashboard")

# =============================
# FILE UPLOADER
# =============================
uploaded_file = st.sidebar.file_uploader(
    "📂 Excel fayl yuklang (.xlsx)",
    type=["xlsx"]
)

if uploaded_file is None:
    st.info("⬅️ Analizni boshlash uchun Excel yuklang")
    st.stop()

# =============================
# LOAD DATA
# =============================
df = pd.read_excel(uploaded_file)

# =============================
# DATE PARSE
# =============================
df["Date of creation"] = pd.to_datetime(df["Date of creation"], errors="coerce", dayfirst=True)
df["Date modified"] = pd.to_datetime(df["Date modified"], errors="coerce", dayfirst=True)

# =============================
# SIDEBAR FILTERS
# =============================
st.sidebar.header("🔎 Filters")

stage_f = st.sidebar.multiselect("Stage", df["Stage"].unique(), df["Stage"].unique())
source_f = st.sidebar.multiselect("Source", df["Source"].unique(), df["Source"].unique())
manager_f = st.sidebar.multiselect("Responsible", df["Responsible"].unique(), df["Responsible"].unique())

date_range = st.sidebar.date_input(
    "Date of creation",
    [df["Date of creation"].min(), df["Date of creation"].max()]
)

filtered = df[
    (df["Stage"].isin(stage_f)) &
    (df["Source"].isin(source_f)) &
    (df["Responsible"].isin(manager_f)) &
    (df["Date of creation"].between(pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])))
]

# =============================
# KPI METRICS
# =============================
st.subheader("📌 KPI Overview")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Leads", len(filtered))
c2.metric("Companies", filtered["Company name"].nunique())
c3.metric("Managers", filtered["Responsible"].nunique())
c4.metric("Sources", filtered["Source"].nunique())

# =============================
# STAGE FUNNEL
# =============================
st.subheader("📈 Lead Funnel (Stage)")

stage_count = filtered["Stage"].value_counts().reset_index()
stage_count.columns = ["Stage", "Leads"]

fig_stage = px.bar(
    stage_count,
    x="Stage",
    y="Leads",
    text="Leads",
    title="Leads by Stage"
)
st.plotly_chart(fig_stage, use_container_width=True)

# =============================
# BEST SOURCE ANALYSIS
# =============================
st.subheader("🔥 Best Lead Sources")

src = filtered.groupby("Source").size().reset_index(name="Leads")

fig_src = px.bar(
    src.sort_values("Leads", ascending=False),
    x="Source",
    y="Leads",
    text="Leads",
    title="Leads by Source"
)
st.plotly_chart(fig_src, use_container_width=True)

# =============================
# MANAGER PERFORMANCE SCORE
# =============================
st.subheader("🏆 Manager Performance")

mgr = filtered.groupby(["Responsible", "Stage"]).size().reset_index(name="Count")

fig_mgr = px.bar(
    mgr,
    x="Responsible",
    y="Count",
    color="Stage",
    barmode="stack",
    title="Manager Performance by Stage"
)
st.plotly_chart(fig_mgr, use_container_width=True)

# =============================
# LEADS OVER TIME
# =============================
st.subheader("⏳ Leads Over Time")

time_df = (
    filtered
    .resample("D", on="Date of creation")
    .size()
    .reset_index(name="Leads")
)

fig_time = px.line(
    time_df,
    x="Date of creation",
    y="Leads",
    title="Daily Lead Creation Trend"
)
st.plotly_chart(fig_time, use_container_width=True)

# =============================
# TOP COMPANIES
# =============================
st.subheader("🏢 Top Companies")

top_comp = (
    filtered["Company name"]
    .value_counts()
    .head(15)
    .reset_index()
)
top_comp.columns = ["Company", "Leads"]

fig_comp = px.bar(
    top_comp,
    x="Company",
    y="Leads",
    text="Leads",
    title="Top Companies by Leads"
)
st.plotly_chart(fig_comp, use_container_width=True)

# =============================
# CONVERSION SPEED
# =============================
st.subheader("⚡ Lead Processing Time")

filtered["Processing Days"] = (
    filtered["Date modified"] - filtered["Date of creation"]
).dt.days

fig_speed = px.histogram(
    filtered,
    x="Processing Days",
    nbins=30,
    title="Lead Processing Time (Days)"
)
st.plotly_chart(fig_speed, use_container_width=True)

# =============================
# DATA TABLE
# =============================
st.subheader("📄 Filtered Data")
st.dataframe(filtered, use_container_width=True)

# =============================
# DOWNLOAD
# =============================
st.download_button(
    "⬇️ Download Filtered Data (CSV)",
    filtered.to_csv(index=False).encode("utf-8"),
    file_name="filtered_crm_data.csv",
    mime="text/csv"
)
