import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="CRM Analytics Dashboard", layout="wide")
st.title("📊 CRM Leads Analytics Dashboard")

st.info("⬅️ Chap tomondan Excel fayl yuklang (.xlsx)")

# =============================
# FILE UPLOADER
# =============================
uploaded_file = st.sidebar.file_uploader("📂 Excel fayl yuklang", type=["xlsx"])
if uploaded_file is None:
    st.stop()

# =============================
# LOAD EXCEL
# =============================
df = pd.read_excel(uploaded_file, header=0)

# =============================
# AUTOMATIC COLUMN RENAMING
# =============================
# Asosiy ustunlar
required_cols = ["Stage", "Source", "Responsible", "Date of creation", "Date modified", "Company name"]

# Agar columnlar “Unnamed” bo‘lsa yoki soni farq qilsa:
if len(df.columns) < len(required_cols):
    # yetmaydigan joyga bo‘sh ustun qo‘shamiz
    for i in range(len(required_cols) - len(df.columns)):
        df[f"extra_{i}"] = ""
elif len(df.columns) > len(required_cols):
    # ortiqcha ustunlarni olib tashlaymiz
    df = df.iloc[:, :len(required_cols)]

# Endi nom beramiz
df.columns = required_cols

st.success("✅ Excel muvaffaqiyatli yuklandi")
st.write("**Ustunlar:**", df.columns.tolist())

# =============================
# DATE PARSE
# =============================
for col in ["Date of creation", "Date modified"]:
    df[col] = pd.to_datetime(df[col], errors="coerce", dayfirst=True)

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
fig_stage = px.bar(stage_count, x="Stage", y="Leads", text="Leads", title="Leads by Stage")
st.plotly_chart(fig_stage, use_container_width=True)

# =============================
# BEST SOURCE
# =============================
st.subheader("🔥 Best Lead Sources")
src = filtered.groupby("Source").size().reset_index(name="Leads")
fig_src = px.bar(src.sort_values("Leads", ascending=False), x="Source", y="Leads", text="Leads", title="Leads by Source")
st.plotly_chart(fig_src, use_container_width=True)

# =============================
# MANAGER PERFORMANCE
# =============================
st.subheader("🏆 Manager Performance")
mgr = filtered.groupby(["Responsible", "Stage"]).size().reset_index(name="Count")
fig_mgr = px.bar(mgr, x="Responsible", y="Count", color="Stage", barmode="stack", title="Manager Performance by Stage")
st.plotly_chart(fig_mgr, use_container_width=True)

# =============================
# LEADS OVER TIME
# =============================
st.subheader("⏳ Leads Over Time")
time_df = filtered.resample("D", on="Date of creation").size().reset_index(name="Leads")
fig_time = px.line(time_df, x="Date of creation", y="Leads", title="Daily Lead Creation Trend")
st.plotly_chart(fig_time, use_container_width=True)

# =============================
# TOP COMPANIES
# =============================
st.subheader("🏢 Top Companies")
top_comp = filtered["Company name"].value_counts().head(15).reset_index()
top_comp.columns = ["Company", "Leads"]
fig_comp = px.bar(top_comp, x="Company", y="Leads", text="Leads", title="Top Companies by Leads")
st.plotly_chart(fig_comp, use_container_width=True)

# =============================
# PROCESSING TIME
# =============================
st.subheader("⚡ Lead Processing Time")
filtered["Processing Days"] = (filtered["Date modified"] - filtered["Date of creation"]).dt.days
fig_speed = px.histogram(filtered, x="Processing Days", nbins=30, title="Lead Processing Time (Days)")
st.plotly_chart(fig_speed, use_container_width=True)

# =============================
# DATA TABLE + DOWNLOAD
# =============================
st.subheader("📄 Filtered Data")
st.dataframe(filtered, use_container_width=True)

st.download_button(
    "⬇️ Download Filtered Data (CSV)",
    filtered.to_csv(index=False).encode("utf-8"),
    file_name="filtered_crm_data.csv",
    mime="text/csv"
)
