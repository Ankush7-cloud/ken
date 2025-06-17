import streamlit as st
import pandas as pd
import duckdb
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime

# Function to compute stats using DuckDB
def compute_stats_duckdb(df, columns):
    # Create virtual DuckDB table from DataFrame using relation
    stats_query = "SELECT "
    stats_parts = []
    for col in columns:
        stats_parts.append(f"AVG({col}) AS {col}_mean")
        stats_parts.append(f"STDDEV_SAMP({col}) AS {col}_std")
        stats_parts.append(f"MAX({col}) AS {col}_max")
        stats_parts.append(f"MIN({col}) AS {col}_min")
    stats_query += ", ".join(stats_parts)
    stats_query += " FROM df"

    # DuckDB query using relation
    result = duckdb.query(stats_query).to_df()

    # Build summary dictionary
    summary = {}
    for col in columns:
        summary[col] = {
            "mean": round(result[f"{col}_mean"][0], 2),
            "std": round(result[f"{col}_std"][0], 2),
            "max": round(result[f"{col}_max"][0], 2),
            "min": round(result[f"{col}_min"][0], 2)
        }
    return summary

# Function to generate PDF report
def generate_pdf(stats, filename="summary_report.pdf"):
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    y = height - 50

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, "COVID Summary Report (via DuckDB)")
    y -= 30

    c.setFont("Helvetica", 12)
    c.drawString(50, y, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    y -= 40

    c.setFont("Helvetica-Bold", 12)
    for col, stat in stats.items():
        c.drawString(50, y, f"Column: {col}")
        y -= 20
        c.setFont("Helvetica", 11)
        c.drawString(70, y, f"Mean: {stat['mean']}")
        y -= 15
        c.drawString(70, y, f"Standard Deviation: {stat['std']}")
        y -= 15
        c.drawString(70, y, f"Max: {stat['max']}")
        y -= 15
        c.drawString(70, y, f"Min: {stat['min']}")
        y -= 30
        c.setFont("Helvetica-Bold", 12)
        if y < 100:
            c.showPage()
            y = height - 50

    c.save()
    return filename

# Streamlit App
st.title("📊 COVID Summary Report Using DuckDB")

uploaded_file = st.file_uploader("Upload counter_wise_latest2.csv", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.success("✅ File Uploaded Successfully")
    st.dataframe(df.head())

    # Ensure numeric conversion
    df['New cases'] = pd.to_numeric(df['New cases'], errors='coerce')
    df['New deaths'] = pd.to_numeric(df['New deaths'], errors='coerce')

    columns = ['New cases', 'New deaths']
    stats = compute_stats_duckdb(df, columns)

    # ✅ Correct line 85 fix:
    stats_df = pd.DataFrame.from_dict(stats, orient='index')
    st.subheader("📋 Summary Statistics")
    st.write(stats_df)

    pdf_path = generate_pdf(stats)
    with open(pdf_path, "rb") as f:
        st.download_button("📄 Download PDF Summary", f, file_name="summary_report_duckdb.pdf")
