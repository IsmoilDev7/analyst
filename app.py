import streamlit as st
import pandas as pd
import plotly.express as px

# =============================
# PAGE CONFIG
# =============================
st.set_page_config(page_title="Excel Analytics Dashboard", layout="wide")
st.title("📊 Excel Data Analytics Dashboard")

st.info("⬅️ Chap tomondan Excel fayl yuklang (.xlsx)")

# =============================
# FILE UPLOADER
# =============================
uploaded_file = st.sidebar.file_uploader(
    "📂 Excel fayl yuklang",
    type=["xlsx"]
)

if uploaded_file is None:
    st.warning("Excel yuklanmagan. Analiz boshlanishi uchun fayl yuklang.")
    st.stop()

# =============================
# LOAD EXCEL
# =============================
df = pd.read_excel(uploaded_file)

st.success("✅ Excel muvaffaqiyatli yuklandi")

# =============================
# DATE COLUMNS AUTO PARSE
# =============================
for col in df.columns:
    if "date" in col.lower():
        df[col] = pd.to_datetime(df[col], errors="coerce", dayfirst=True)

# =============================
# SIDEBAR FILTERS (AUTO)
# =============================
st.sidebar.header("🔎 Filterlar")

filtered_df = df.copy()

for col in df.select_dtypes(include=["object"]).columns:
    values = st.sidebar.multiselect(
        f"{col}",
        df[col].dropna().unique(),
        df[col].dropna().unique()
    )
    filtered_df = filtered_df[filtered_df[col].isin(values)]

# =============================
# KPI METRICS
# =============================
st.subheader("📌 KPI")

c1, c2, c3 = st.columns(3)
c1.metric("Rows", len(filtered_df))
c2.metric("Columns", filtered_df.shape[1])
c3.metric("Unique Values", filtered_df.nunique().sum())

# =============================
# CATEGORICAL ANALYSIS
# =============================
st.subheader("📊 Kategoriyalar bo‘yicha analiz")

cat_cols = filtered_df.select_dtypes(include=["object"]).columns

for col in cat_cols:
    fig = px.bar(
        filtered_df[col].value_counts().reset_index(),
        x="index",
        y=col,
        title=f"{col} bo‘yicha taqsimot",
        text_auto=True
    )
    fig.update_layout(xaxis_title=col, yaxis_title="Count")
    st.plotly_chart(fig, use_container_width=True)

# =============================
# NUMERIC ANALYSIS
# =============================
st.subheader("📈 Sonli ustunlar analizi")

num_cols = filtered_df.select_dtypes(include=["int64", "float64"]).columns

for col in num_cols:
    fig = px.histogram(
        filtered_df,
        x=col,
        nbins=30,
        title=f"{col} distribution"
    )
    st.plotly_chart(fig, use_container_width=True)

# =============================
# TIME ANALYSIS
# =============================
date_cols = filtered_df.select_dtypes(include=["datetime64[ns]"]).columns

for col in date_cols:
    time_df = filtered_df.resample("D", on=col).size().reset_index(name="Count")
    fig = px.line(
        time_df,
        x=col,
        y="Count",
        title=f"{col} bo‘yicha vaqt analizi"
    )
    st.plotly_chart(fig, use_container_width=True)

# =============================
# DATA TABLE
# =============================
st.subheader("📄 Filterlangan ma’lumotlar")
st.dataframe(filtered_df, use_container_width=True)

# =============================
# DOWNLOAD
# =============================
st.download_button(
    "⬇️ Filterlangan datani yuklab olish (CSV)",
    filtered_df.to_csv(index=False).encode("utf-8"),
    file_name="filtered_data.csv",
    mime="text/csv"
)
