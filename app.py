import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="CRM Analytics Dashboard", layout="wide")
st.title("📊 CRM Leads Analytics Dashboard")

# =============================
# FILE UPLOADER
# =============================
uploaded_file = st.sidebar.file_uploader("📂 Excel fayl yuklang (.xlsx)", type=["xlsx"])

if uploaded_file is None:
    st.info("⬅️ Analizni boshlash uchun Excel yuklang")
    st.stop()

# =============================
# LOAD DATA
# =============================
df = pd.read_excel(uploaded_file)
st.success("✅ Excel muvaffaqiyatli yuklandi")

st.write("**Ustunlar:**", df.columns.tolist())

# =============================
# COLUMN MAPPING (dynamic)
# =============================
def get_col(possible_names):
    for name in possible_names:
        if name in df.columns:
            return name
    return None

stage_col = get_col(["Stage", "stage", "stage_name"])
source_col = get_col(["Source", "source", "lead_source"])
manager_col = get_col(["Responsible", "responsible", "manager"])
created_col = get_col(["Date of creation", "date of creation", "created_at"])
modified_col = get_col(["Date modified", "date modified", "modified_at"])
company_col = get_col(["Company name", "company name", "company"])

# Check required columns
required_cols = [stage_col, source_col, manager_col, created_col, modified_col, company_col]
if None in required_cols:
    st.error("❌ Excel’da kerakli ustunlar topilmadi. Quyidagilar kerak: Stage, Source, Responsible, Date of creation, Date modified, Company name")
    st.stop()

# =============================
# DATE PARSE
# =============================
df[created_col] = pd.to_datetime(df[created_col], errors="coerce", dayfirst=True)
df[modified_col] = pd.to_datetime(df[modified_col], errors="coerce", dayfirst=True)

# =============================
# SIDEBAR FILTERS
# =============================
st.sidebar.header("🔎 Filters")
stage_f = st.sidebar.multiselect("Stage", df[stage_col].unique(), df[stage_col].unique())
source_f = st.sidebar.multiselect("Source", df[source_col].unique(), df[source_col].unique())
manager_f = st.sidebar.multiselect("Responsible", df[manager_col].unique(), df[manager_col].unique())
date_range = st.sidebar.date_input(
    "Date of creation",
    [df[created_col].min(), df[created_col].max()]
)

filtered = df[
    (df[stage_col].isin(stage_f)) &
    (df[source_col].isin(source_f)) &
    (df[manager_col].isin(manager_f)) &
    (df[created_col].between(pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])))
]

# =============================
# KPI METRICS
# =============================
st.subheader("📌 KPI Overview")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Leads", len(filtered))
c2.metric("Companies", filtered[company_col].nunique())
c3.metric("Managers", filtered[manager_col].nunique())
c4.metric("Sources", filtered[source_col].nunique())

# =============================
# STAGE FUNNEL
# =============================
st.subheader("📈 Lead Funnel (Stage)")
stage_count = filtered[stage_col].value_counts().reset_index()
stage_count.columns = ["Stage", "Leads"]
fig_stage = px.bar(stage_count, x="Stage", y="Leads", text="Leads", title="Leads by Stage")
st.plotly_chart(fig_stage, use_container_width=True)

# =============================
# BEST SOURCE
# =============================
st.subheader("🔥 Best Lead Sources")
src = filtered.groupby(source_col).size().reset_index(name="Leads")
fig_src = px.bar(src.sort_values("Leads", ascending=False), x=source_col, y="Leads", text="Leads", title="Leads by Source")
st.plotly_chart(fig_src, use_container_width=True)

# =============================
# MANAGER PERFORMANCE
# =============================
st.subheader("🏆 Manager Performance")
mgr = filtered.groupby([manager_col, stage_col]).size().reset_index(name="Count")
fig_mgr = px.bar(mgr, x=manager_col, y="Count", color=stage_col, barmode="stack", title="Manager Performance by Stage")
st.plotly_chart(fig_mgr, use_container_width=True)

# =============================
# LEADS OVER TIME
# =============================
st.subheader("⏳ Leads Over Time")
time_df = filtered.resample("D", on=created_col).size().reset_index(name="Leads")
fig_time = px.line(time_df, x=created_col, y="Leads", title="Daily Lead Creation Trend")
st.plotly_chart(fig_time, use_container_width=True)

# =============================
# TOP COMPANIES
# =============================
st.subheader("🏢 Top Companies")
top_comp = filtered[company_col].value_counts().head(15).reset_index()
top_comp.columns = ["Company", "Leads"]
fig_comp = px.bar(top_comp, x="Company", y="Leads", text="Leads", title="Top Companies by Leads")
st.plotly_chart(fig_comp, use_container_width=True)

# =============================
# PROCESSING TIME
# =============================
st.subheader("⚡ Lead Processing Time")
filtered["Processing Days"] = (filtered[modified_col] - filtered[created_col]).dt.days
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
