import streamlit as st
import pandas as pd
import plotly.express as px
import io

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(page_title="📊 CRM Campaign Dashboard", layout="wide")
st.title("📊 CRM Campaign Dashboard")
st.markdown("""
Upload your Excel file to visualize **manager-wise campaign interactions, stages, and company contacts**.
The dashboard includes multiple charts for interactive analysis.
""")

# -----------------------------
# FILE UPLOAD
# -----------------------------
uploaded_file = st.file_uploader("📂 Upload Excel (.xlsx/.xls)", type=["xlsx", "xls"])
if uploaded_file is None:
    st.stop()

df = pd.read_excel(uploaded_file, engine="openpyxl")
st.write("Columns detected:", df.columns.tolist())
st.dataframe(df.head(5))

# -----------------------------
# SAFE DATE PARSING
# -----------------------------
date_cols = ["Date of creation", "Date modified"]
for col in date_cols:
    if col in df.columns:
        series_parsed = pd.to_datetime(df[col], errors="coerce", dayfirst=True)
        if series_parsed.isnull().all():
            series_parsed = pd.to_datetime(df[col], errors="coerce", infer_datetime_format=True)
        df[col] = series_parsed

# -----------------------------
# DATE FILTER
# -----------------------------
available_date_cols = [c for c in date_cols if c in df.columns and df[c].notna().any()]
if available_date_cols:
    date_col = st.selectbox("Select date column for filtering", available_date_cols)
    min_date = df[date_col].min().date()
    max_date = df[date_col].max().date()
    start_date = st.sidebar.date_input("Start date", min_date, min_value=min_date, max_value=max_date)
    end_date = st.sidebar.date_input("End date", max_date, min_value=min_date, max_value=max_date)
    filtered_df = df[(df[date_col] >= pd.to_datetime(start_date)) & (df[date_col] <= pd.to_datetime(end_date))]
else:
    filtered_df = df

st.subheader(f"Filtered Data ({len(filtered_df)} records)")
st.dataframe(filtered_df.head(10))

# -----------------------------
# KPI METRICS
# -----------------------------
st.subheader("📌 Key Metrics")
total_campaigns = len(filtered_df)
total_managers = filtered_df["Responsible"].nunique() if "Responsible" in df.columns else 0
st.markdown(f"**Total campaigns:** {total_campaigns}  \n**Total managers:** {total_managers}")

# -----------------------------
# 1️⃣ Campaigns by Stage (Doughnut)
# -----------------------------
if "Stage" in filtered_df.columns:
    stage_counts = filtered_df["Stage"].value_counts().reset_index()
    stage_counts.columns = ["Stage", "Count"]
    fig_stage = px.pie(stage_counts, names="Stage", values="Count", title="Campaigns by Stage", hole=0.4)
    st.plotly_chart(fig_stage, use_container_width=True)

# -----------------------------
# 2️⃣ Campaigns per Manager (Bar)
# -----------------------------
if "Responsible" in filtered_df.columns:
    manager_counts = filtered_df["Responsible"].value_counts().reset_index()
    manager_counts.columns = ["Manager", "Count"]
    fig_manager = px.bar(manager_counts, x="Manager", y="Count", title="Campaigns per Manager", text="Count")
    st.plotly_chart(fig_manager, use_container_width=True)

# -----------------------------
# 3️⃣ Companies per Manager (Pie)
# -----------------------------
if "Responsible" in filtered_df.columns and "Company name" in filtered_df.columns:
    company_mgr = filtered_df.groupby("Responsible")["Company name"].nunique().reset_index()
    company_mgr.columns = ["Manager", "Companies"]
    fig_comp_mgr = px.pie(company_mgr, names="Manager", values="Companies", title="Number of Companies Managed by Each Manager")
    st.plotly_chart(fig_comp_mgr, use_container_width=True)

# -----------------------------
# 4️⃣ Timeline of Campaigns (Line)
# -----------------------------
if available_date_cols:
    timeline = filtered_df.groupby(date_col, as_index=False).size()
    timeline.columns = [date_col, "Campaign Count"]
    fig_timeline = px.line(timeline, x=date_col, y="Campaign Count", markers=True, title="Campaigns Over Time")
    st.plotly_chart(fig_timeline, use_container_width=True)

# -----------------------------
# 5️⃣ Manager Stage Analysis (Stacked Bar)
# -----------------------------
if "Responsible" in filtered_df.columns and "Stage" in filtered_df.columns:
    mgr_stage = filtered_df.groupby(["Responsible", "Stage"]).size().reset_index(name="Count")
    fig_mgr_stage = px.bar(mgr_stage, x="Responsible", y="Count", color="Stage", title="Manager vs Stage Analysis")
    st.plotly_chart(fig_mgr_stage, use_container_width=True)

# -----------------------------
# 6️⃣ Campaigns per Source (Bar)
# -----------------------------
if "Source" in filtered_df.columns:
    src_counts = filtered_df["Source"].value_counts().reset_index()
    src_counts.columns = ["Source", "Count"]
    fig_source = px.bar(src_counts, x="Source", y="Count", title="Campaigns by Source", text="Count")
    st.plotly_chart(fig_source, use_container_width=True)

# -----------------------------
# 7️⃣ Companies Overview (Pie)
# -----------------------------
if "Company name" in filtered_df.columns:
    comp_counts = filtered_df["Company name"].value_counts().reset_index().head(10)
    comp_counts.columns = ["Company", "Count"]
    fig_comp = px.pie(comp_counts, names="Company", values="Count", title="Top Companies by Campaigns")
    st.plotly_chart(fig_comp, use_container_width=True)

# -----------------------------
# 8️⃣ Export Excel
# -----------------------------
st.subheader("⬇️ Download Analysis (Excel)")
output = io.BytesIO()
with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
    filtered_df.to_excel(writer, index=False, sheet_name="Filtered_Data")
output.seek(0)
st.download_button(
    label="📥 Download Excel Report",
    data=output,
    file_name="crm_campaign_analysis.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

st.success("✅ Dashboard ready with multiple interactive charts for managers and campaigns!")
