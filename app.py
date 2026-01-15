import streamlit as st
import pandas as pd
import plotly.express as px

# =============================
# PAGE CONFIG
# =============================
st.set_page_config(
    page_title="CRM Leads Full Analytics",
    layout="wide"
)

st.title("📊 CRM Leads – Full Analytics Dashboard")

# =============================
# LOAD DATA FROM GITHUB
# =============================
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/USERNAME/REPO/main/data/leads.csv"
    df = pd.read_csv(url)

    df["Date of creation"] = pd.to_datetime(df["Date of creation"], dayfirst=True)
    df["Date modified"] = pd.to_datetime(df["Date modified"], dayfirst=True)

    return df

df = load_data()

# =============================
# SIDEBAR FILTERS
# =============================
st.sidebar.header("🔍 Filters")

stage = st.sidebar.multiselect("Stage", df["Stage"].unique(), df["Stage"].unique())
source = st.sidebar.multiselect("Source", df["Source"].unique(), df["Source"].unique())
manager = st.sidebar.multiselect("Responsible", df["Responsible"].unique(), df["Responsible"].unique())

date_range = st.sidebar.date_input(
    "Date of creation",
    [df["Date of creation"].min(), df["Date of creation"].max()]
)

# =============================
# APPLY FILTERS
# =============================
filtered = df[
    (df["Stage"].isin(stage)) &
    (df["Source"].isin(source)) &
    (df["Responsible"].isin(manager)) &
    (df["Date of creation"].between(pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])))
]

# =============================
# KPI METRICS
# =============================
st.subheader("📌 Key Metrics")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Leads", len(filtered))
col2.metric("Unique Companies", filtered["Company name"].nunique())
col3.metric("Managers", filtered["Responsible"].nunique())
col4.metric("Sources", filtered["Source"].nunique())

# =============================
# STAGE DISTRIBUTION
# =============================
st.subheader("📈 Lead Stage Distribution")

fig_stage = px.pie(
    filtered,
    names="Stage",
    title="Leads by Stage"
)
st.plotly_chart(fig_stage, use_container_width=True)

# =============================
# SOURCE ANALYSIS (🔥 BEST SOURCE)
# =============================
st.subheader("🔥 Best Lead Source")

source_count = filtered.groupby("Source").size().reset_index(name="Leads")

fig_source = px.bar(
    source_count,
    x="Source",
    y="Leads",
    title="Leads by Source",
    text_auto=True
)
st.plotly_chart(fig_source, use_container_width=True)

# =============================
# MANAGER PERFORMANCE SCORE
# =============================
st.subheader("🏆 Manager Performance")

manager_score = (
    filtered.groupby(["Responsible", "Stage"])
    .size()
    .reset_index(name="Count")
)

fig_manager = px.bar(
    manager_score,
    x="Responsible",
    y="Count",
    color="Stage",
    title="Manager Performance by Stage",
    barmode="stack"
)
st.plotly_chart(fig_manager, use_container_width=True)

# =============================
# TIME ANALYSIS
# =============================
st.subheader("⏳ Leads Over Time")

time_df = filtered.resample("D", on="Date of creation").size().reset_index(name="Leads")

fig_time = px.line(
    time_df,
    x="Date of creation",
    y="Leads",
    title="Leads Created Over Time"
)
st.plotly_chart(fig_time, use_container_width=True)

# =============================
# TOP COMPANIES
# =============================
st.subheader("🏢 Top Companies")

top_companies = (
    filtered["Company name"]
    .value_counts()
    .head(10)
    .reset_index()
)
top_companies.columns = ["Company", "Leads"]

fig_comp = px.bar(
    top_companies,
    x="Company",
    y="Leads",
    title="Top 10 Companies"
)
st.plotly_chart(fig_comp, use_container_width=True)

# =============================
# RAW DATA
# =============================
st.subheader("📄 Filtered Data Table")
st.dataframe(filtered, use_container_width=True)
