import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="CRM Dashboard / CRM Boshqaruv Paneli", layout="wide")
st.title("📊 CRM Leads Analytics Dashboard / CRM Yetakchilar Tahlili")
st.info("⬅️ Chap tomondan Excel fayl yuklang (.xlsx)")

# =============================
# FILE UPLOADER
# =============================
uploaded_file = st.sidebar.file_uploader("📂 Excel fayl yuklang / Excel fayl yuklash", type=["xlsx"])
if uploaded_file is None:
    st.stop()

# =============================
# LOAD EXCEL
# =============================
df = pd.read_excel(uploaded_file, header=0)

# =============================
# AUTOMATIC COLUMN RENAMING
# =============================
required_cols = ["Stage", "Source", "Responsible", "Date of creation", "Date modified", "Company name"]
if len(df.columns) < len(required_cols):
    for i in range(len(required_cols) - len(df.columns)):
        df[f"extra_{i}"] = ""
elif len(df.columns) > len(required_cols):
    df = df.iloc[:, :len(required_cols)]
df.columns = required_cols
st.success("✅ Excel muvaffaqiyatli yuklandi")
st.write("**Ustunlar / Columns:**", df.columns.tolist())

# =============================
# DATETIME PARSING
# =============================
for col in ["Date of creation", "Date modified"]:
    # Agar string formatida bo'lsa, dd.mm.yyyy hh:mm:ss ni parse qiladi
    df[col] = pd.to_datetime(df[col].astype(str), dayfirst=True, errors="coerce")

# =============================
# SIDEBAR FILTERS
# =============================
st.sidebar.header("🔎 Filters / Filtrlar")
stage_f = st.sidebar.multiselect("Stage / Bosqich", df["Stage"].unique(), df["Stage"].unique())
source_f = st.sidebar.multiselect("Source / Manba", df["Source"].unique(), df["Source"].unique())
manager_f = st.sidebar.multiselect("Responsible / Mas'ul shaxs", df["Responsible"].unique(), df["Responsible"].unique())
company_f = st.sidebar.multiselect("Company / Kompaniya", df["Company name"].unique(), df["Company name"].unique())

# =============================
# DATE RANGE FILTER
# =============================
if df["Date of creation"].notna().sum() > 0:
    min_date = df["Date of creation"].min().date()
    max_date = df["Date of creation"].max().date()
    date_range = st.sidebar.date_input("Date of creation / Yaratilgan sana (from - to)", [min_date, max_date])

    df_filtered = df[
        (df["Stage"].isin(stage_f)) &
        (df["Source"].isin(source_f)) &
        (df["Responsible"].isin(manager_f)) &
        (df["Company name"].isin(company_f)) &
        (df["Date of creation"].dt.date.between(date_range[0], date_range[1]))
    ]
else:
    st.sidebar.warning("⚠️ Date of creation / Yaratilgan sana ustuni bo‘sh, filter ishlamaydi")
    df_filtered = df[
        (df["Stage"].isin(stage_f)) &
        (df["Source"].isin(source_f)) &
        (df["Responsible"].isin(manager_f)) &
        (df["Company name"].isin(company_f))
    ]

# =============================
# KPI METRICS
# =============================
st.subheader("📌 KPI Overview / KPI Umumiy ko‘rsatkichlar")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Leads / Jami yetakchilar", len(df_filtered))
c2.metric("Companies / Kompaniyalar", df_filtered["Company name"].nunique())
c3.metric("Managers / Mas'ullar", df_filtered["Responsible"].nunique())
c4.metric("Sources / Manbalar", df_filtered["Source"].nunique())

# =============================
# STAGE FUNNEL
# =============================
st.subheader("📈 Lead Funnel / Bosqichlar bo‘yicha yetakchilar")
stage_count = df_filtered["Stage"].value_counts().reset_index()
stage_count.columns = ["Stage", "Leads"]
fig_stage = px.bar(stage_count, x="Stage", y="Leads", text="Leads",
                   title="Leads by Stage / Bosqichlar bo‘yicha yetakchilar")
st.plotly_chart(fig_stage, use_container_width=True)

# =============================
# BEST SOURCE
# =============================
st.subheader("🔥 Best Lead Sources / Eng samarali manbalar")
src = df_filtered.groupby("Source").size().reset_index(name="Leads")
fig_src = px.bar(src.sort_values("Leads", ascending=False), x="Source", y="Leads", text="Leads",
                 title="Leads by Source / Manbalar bo‘yicha yetakchilar")
st.plotly_chart(fig_src, use_container_width=True)

# =============================
# MANAGER PERFORMANCE
# =============================
st.subheader("🏆 Manager Performance / Mas'ullar ishlashi")
mgr = df_filtered.groupby(["Responsible", "Stage"]).size().reset_index(name="Count")
fig_mgr = px.bar(mgr, x="Responsible", y="Count", color="Stage", barmode="stack",
                 title="Manager Performance by Stage / Mas'ullar bo‘yicha")
st.plotly_chart(fig_mgr, use_container_width=True)

# =============================
# LEADS OVER TIME
# =============================
st.subheader("⏳ Leads Over Time / Yetakchilar vaqti bo‘yicha")
if df_filtered["Date of creation"].notna().sum() > 0:
    time_df = df_filtered.resample("D", on="Date of creation").size().reset_index(name="Leads")
    fig_time = px.line(time_df, x="Date of creation", y="Leads",
                       title="Daily Lead Creation Trend / Har kunlik yetakchilar soni")
    st.plotly_chart(fig_time, use_container_width=True)

# =============================
# TOP COMPANIES
# =============================
st.subheader("🏢 Top Companies / Eng faol kompaniyalar")
top_comp = df_filtered["Company name"].value_counts().head(15).reset_index()
top_comp.columns = ["Company", "Leads"]
fig_comp = px.bar(top_comp, x="Company", y="Leads", text="Leads",
                  title="Top Companies by Leads / Kompaniyalar bo‘yicha yetakchilar")
st.plotly_chart(fig_comp, use_container_width=True)

# =============================
# PROCESSING TIME
# =============================
st.subheader("⚡ Lead Processing Time / Yetakchi ishlash vaqti (kun)")
df_filtered["Processing Days"] = (df_filtered["Date modified"] - df_filtered["Date of creation"]).dt.days
fig_speed = px.histogram(df_filtered, x="Processing Days", nbins=30,
                         title="Lead Processing Time (Days) / Yetakchi ishlash vaqti")
st.plotly_chart(fig_speed, use_container_width=True)

# =============================
# RESPONSIBLE ANALYSIS
# =============================
st.subheader("👤 Responsible Analysis / Mas'ullar bo‘yicha tahlil")
resp_count = df_filtered.groupby("Responsible").size().reset_index(name="Leads")
fig_resp = px.bar(resp_count.sort_values("Leads", ascending=False), x="Responsible", y="Leads", text="Leads",
                  title="Leads by Responsible / Mas'ullar bo‘yicha yetakchilar")
st.plotly_chart(fig_resp, use_container_width=True)

# =============================
# DATA TABLE + DOWNLOAD
# =============================
st.subheader("📄 Filtered Data / Tanlangan ma’lumotlar")
st.dataframe(df_filtered, use_container_width=True)

st.download_button(
    "⬇️ Download Filtered Data (CSV) / CSV yuklab olish",
    df_filtered.to_csv(index=False).encode("utf-8"),
    file_name="filtered_crm_data.csv",
    mime="text/csv"
)
