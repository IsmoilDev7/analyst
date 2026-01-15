import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="CRM Leads Analytics", layout="wide")
st.title("📊 CRM Leads – Full Analytics Dashboard")

# =============================
# DATA LOAD
# =============================
def load_from_github():
    try:
        url = "https://raw.githubusercontent.com/USERNAME/REPO/main/data/leads.csv"
        df = pd.read_csv(url)
        return df
    except:
        return None

uploaded_file = st.sidebar.file_uploader(
    "📂 Upload CSV file",
    type=["csv"]
)

df = None

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
elif load_from_github() is not None:
    df = load_from_github()
else:
    st.error("❌ No data loaded. Upload CSV or fix GitHub raw link.")
    st.stop()

# =============================
# DATE PARSE
# =============================
df["Date of creation"] = pd.to_datetime(df["Date of creation"], dayfirst=True, errors="coerce")
df["Date modified"] = pd.to_datetime(df["Date modified"], dayfirst=True, errors="coerce")

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

filtered = df[
    (df["Stage"].isin(stage)) &
    (df["Source"].isin(source)) &
    (df["Responsible"].isin(manager)) &
    (df["Date of creation"].between(pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])))
]

# =============================
# KPI
# =============================
st.subheader("📌 KPI")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Leads", len(filtered))
c2.metric("Companies", filtered["Company name"].nunique())
c3.metric("Managers", filtered["Responsible"].nunique())
c4.metric("Sources", filtered["Source"].nunique())

# =============================
# STAGE PIE
# =============================
st.subheader("📈 Stage Distribution")
st.plotly_chart(
    px.pie(filtered, names="Stage"),
    use_container_width=True
)

# =============================
# BEST SOURCE
# =============================
st.subheader("🔥 Best Source")
src = filtered.groupby("Source").size().reset_index(name="Leads")
st.plotly_chart(
    px.bar(src, x="Source", y="Leads", text_auto=True),
    use_container_width=True
)

# =============================
# MANAGER PERFORMANCE
# =============================
st.subheader("🏆 Manager Performance Score")
mgr = filtered.groupby(["Responsible", "Stage"]).size().reset_index(name="Count")
st.plotly_chart(
    px.bar(mgr, x="Responsible", y="Count", color="Stage", barmode="stack"),
    use_container_width=True
)

# =============================
# TIME SERIES
# =============================
st.subheader("⏳ Leads Over Time")
time_df = filtered.resample("D", on="Date of creation").size().reset_index(name="Leads")
st.plotly_chart(
    px.line(time_df, x="Date of creation", y="Leads"),
    use_container_width=True
)

# =============================
# TOP COMPANIES
# =============================
st.subheader("🏢 Top Companies")
top = filtered["Company name"].value_counts().head(10).reset_index()
top.columns = ["Company", "Leads"]
st.plotly_chart(
    px.bar(top, x="Company", y="Leads"),
    use_container_width=True
)

# =============================
# TABLE
# =============================
st.subheader("📄 Data Table")
st.dataframe(filtered, use_container_width=True)
