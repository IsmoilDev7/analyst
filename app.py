import streamlit as st
import pandas as pd
import plotly.express as px
import io

# -----------------------------
# PAGE CONFIG | SAHIFA SOZLAMALARI
# -----------------------------
st.set_page_config(page_title="📊 CRM Campaign Dashboard", layout="wide")
st.title("📊 CRM Campaign Dashboard")
st.markdown("""
**English:** Upload your Excel file to visualize manager-wise campaign interactions, stages, and company contacts.  
**O‘zbekcha:** Excel faylni yuklab, menejerlar bo‘yicha kampaniyalar, bosqichlar va kompaniyalar bilan aloqalarni ko‘ring.

**English:** The dashboard includes multiple charts for interactive analysis.  
**O‘zbekcha:** Dashboard interaktiv tahlil uchun ko‘plab diagrammalarni o‘z ichiga oladi.
""")

# -----------------------------
# FILE UPLOAD | FAYL YUKLASH
# -----------------------------
uploaded_file = st.file_uploader(
    "📂 Upload Excel (.xlsx/.xls) | Excel fayl yuklang",
    type=["xlsx", "xls"]
)

if uploaded_file is None:
    st.stop()

# Excel faylni o‘qish
df = pd.read_excel(uploaded_file, engine="openpyxl")

# Ustun nomlarini ko‘rsatish
st.write("Columns detected | Aniqlangan ustunlar:", df.columns.tolist())
st.dataframe(df.head(5))

# -----------------------------
# SAFE DATE PARSING | SANANI XAVFSIZ O‘GIRISH
# -----------------------------
date_cols = ["Date of creation", "Date modified"]

for col in date_cols:
    if col in df.columns:
        # Avval day-first format bilan o‘giramiz (DD.MM.YYYY)
        series_parsed = pd.to_datetime(df[col], errors="coerce", dayfirst=True)

        # Agar barchasi NaT bo‘lsa, avtomatik format bilan qayta urinib ko‘ramiz
        if series_parsed.isnull().all():
            series_parsed = pd.to_datetime(
                df[col],
                errors="coerce",
                infer_datetime_format=True
            )

        df[col] = series_parsed

# -----------------------------
# DATE FILTER | SANA BO‘YICHA FILTR
# -----------------------------
available_date_cols = [
    c for c in date_cols if c in df.columns and df[c].notna().any()
]

if available_date_cols:
    # Foydalanuvchi sanani qaysi ustundan olishini tanlaydi
    date_col = st.selectbox(
        "Select date column for filtering | Filtrlash uchun sana ustuni",
        available_date_cols
    )

    min_date = df[date_col].min().date()
    max_date = df[date_col].max().date()

    start_date = st.sidebar.date_input(
        "Start date | Boshlanish sanasi",
        min_date,
        min_value=min_date,
        max_value=max_date
    )

    end_date = st.sidebar.date_input(
        "End date | Tugash sanasi",
        max_date,
        min_value=min_date,
        max_value=max_date
    )

    # Sana oralig‘i bo‘yicha filtrlash
    filtered_df = df[
        (df[date_col] >= pd.to_datetime(start_date)) &
        (df[date_col] <= pd.to_datetime(end_date))
    ]
else:
    # Agar sana topilmasa, filtrsiz ishlaydi
    filtered_df = df

st.subheader(f"Filtered Data | Filtrlangan ma’lumotlar ({len(filtered_df)} ta)")
st.dataframe(filtered_df.head(10))

# -----------------------------
# KPI METRICS | ASOSIY KO‘RSATKICHLAR
# -----------------------------
st.subheader("📌 Key Metrics | Asosiy ko‘rsatkichlar")

total_campaigns = len(filtered_df)
total_managers = (
    filtered_df["Responsible"].nunique()
    if "Responsible" in filtered_df.columns
    else 0
)

st.markdown(f"""
**English:**  
• Total campaigns: **{total_campaigns}**  
• Total managers: **{total_managers}**

**O‘zbekcha:**  
• Jami kampaniyalar: **{total_campaigns}**  
• Jami menejerlar: **{total_managers}**
""")

# -----------------------------
# 1️⃣ Campaigns by Stage (Doughnut)
#     BOSQICHLAR BO‘YICHA KAMPANIYALAR
# -----------------------------
if "Stage" in filtered_df.columns:
    stage_counts = filtered_df["Stage"].value_counts().reset_index()
    stage_counts.columns = ["Stage", "Count"]

    fig_stage = px.pie(
        stage_counts,
        names="Stage",
        values="Count",
        title="Campaigns by Stage | Bosqichlar bo‘yicha kampaniyalar",
        hole=0.4
    )
    st.plotly_chart(fig_stage, use_container_width=True)

# -----------------------------
# 2️⃣ Campaigns per Manager (Bar)
#     MENEJERLAR BO‘YICHA KAMPANIYALAR
# -----------------------------
if "Responsible" in filtered_df.columns:
    manager_counts = filtered_df["Responsible"].value_counts().reset_index()
    manager_counts.columns = ["Manager", "Count"]

    fig_manager = px.bar(
        manager_counts,
        x="Manager",
        y="Count",
        title="Campaigns per Manager | Menejerlar bo‘yicha kampaniyalar",
        text="Count"
    )
    st.plotly_chart(fig_manager, use_container_width=True)

# -----------------------------
# 3️⃣ Companies per Manager (Pie)
#     MENEJERLAR BO‘YICHA KOMPANIYALAR
# -----------------------------
if "Responsible" in filtered_df.columns and "Company name" in filtered_df.columns:
    company_mgr = (
        filtered_df
        .groupby("Responsible")["Company name"]
        .nunique()
        .reset_index()
    )
    company_mgr.columns = ["Manager", "Companies"]

    fig_comp_mgr = px.pie(
        company_mgr,
        names="Manager",
        values="Companies",
        title="Companies per Manager | Menejer boshqarayotgan kompaniyalar"
    )
    st.plotly_chart(fig_comp_mgr, use_container_width=True)

# -----------------------------
# 4️⃣ Timeline of Campaigns (Line)
#     VAQT BO‘YICHA KAMPANIYALAR
# -----------------------------
if available_date_cols:
    timeline = filtered_df.groupby(date_col, as_index=False).size()
    timeline.columns = [date_col, "Campaign Count"]

    fig_timeline = px.line(
        timeline,
        x=date_col,
        y="Campaign Count",
        markers=True,
        title="Campaigns Over Time | Kampaniyalar vaqt bo‘yicha"
    )
    st.plotly_chart(fig_timeline, use_container_width=True)

# -----------------------------
# 5️⃣ Manager Stage Analysis (Stacked Bar)
#     MENEJER + BOSQICH TAHLILI
# -----------------------------
if "Responsible" in filtered_df.columns and "Stage" in filtered_df.columns:
    mgr_stage = (
        filtered_df
        .groupby(["Responsible", "Stage"])
        .size()
        .reset_index(name="Count")
    )

    fig_mgr_stage = px.bar(
        mgr_stage,
        x="Responsible",
        y="Count",
        color="Stage",
        title="Manager vs Stage | Menejer va bosqichlar"
    )
    st.plotly_chart(fig_mgr_stage, use_container_width=True)

# -----------------------------
# 6️⃣ Campaigns per Source (Bar)
#     MANBA BO‘YICHA KAMPANIYALAR
# -----------------------------
if "Source" in filtered_df.columns:
    src_counts = filtered_df["Source"].value_counts().reset_index()
    src_counts.columns = ["Source", "Count"]

    fig_source = px.bar(
        src_counts,
        x="Source",
        y="Count",
        title="Campaigns by Source | Manba bo‘yicha kampaniyalar",
        text="Count"
    )
    st.plotly_chart(fig_source, use_container_width=True)

# -----------------------------
# 7️⃣ Companies Overview (Pie)
#     KOMPANIYALAR UMUMIY KO‘RINISHI
# -----------------------------
if "Company name" in filtered_df.columns:
    comp_counts = (
        filtered_df["Company name"]
        .value_counts()
        .reset_index()
        .head(10)
    )
    comp_counts.columns = ["Company", "Count"]

    fig_comp = px.pie(
        comp_counts,
        names="Company",
        values="Count",
        title="Top Companies by Campaigns | Eng faol kompaniyalar"
    )
    st.plotly_chart(fig_comp, use_container_width=True)

# -----------------------------
# 8️⃣ Export Excel | EXCELGA YUKLAB OLISH
# -----------------------------
st.subheader("⬇️ Download Analysis (Excel) | Tahlilni yuklab olish")

output = io.BytesIO()
with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
    filtered_df.to_excel(writer, index=False, sheet_name="Filtered_Data")

output.seek(0)

st.download_button(
    label="📥 Download Excel Report | Excel hisobotni yuklash",
    data=output,
    file_name="crm_campaign_analysis.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

st.success(
    "✅ Dashboard ready with multiple interactive charts | "
    "Ko‘plab interaktiv diagrammalar bilan dashboard tayyor!"
)
