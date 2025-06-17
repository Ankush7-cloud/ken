import streamlit as st
import pandas as pd
import duckdb
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime

# Function to compute stats using DuckDB
def compute_stats_duckdb(df, columns):
    # Register dataframe as DuckDB view
    duckdb.register("covid_data", df)

    stats_query = "SELECT "
    stats_parts = []
    for col in columns:
        stats_parts.append(f"AVG({col}) as {col}_mean")
        stats_parts.append(f"STDDEV_SAMP({col}) as {col}_std")
        stats_parts.append(f"MAX({col}) as {col}_max")
        stats_parts.append(f"MIN({col}) as {col}_min")
    stats_query += ", ".join(stats_parts)
    stats_query += " FROM covid_data"

    result = duckdb.sql(stats_query).fetchdf()
    summary = {}
    for col in columns:
        summary[col] = {
            "mean": round(result[f"{col}_mean"][0], 2),
            "std": round(result[f"{col}_std"][0], 2),
            "max": round(result[f"{col}_max"][0], 2),
            "min": round(result[f"{col}_min"][0], 2)
        }
    return summary

# Generate PDF report
def generate_pdf(stats, filename="summary_report.pdf"):
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    y = height - 50

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, "COVID Data Summary Report (via DuckDB)")
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

# Streamlit UI
st.title("📊 COVID Summary Report Using DuckDB")

uploaded_file = st.file_uploader("Upload counter_wise_latest2.csv", type="csv")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.success("✅ File Uploaded Successfully")
    st.dataframe(df.head())

    # Clean numeric columns
    numeric_cols = ["New cases", "New deaths"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Compute stats using DuckDB
    stats = compute_stats_duckdb(df, numeric_cols)

    # Show summary table
    st.subheader("📋 Summary Statistics (via DuckDB)")
    st.write(pd.DataFrame(stats).T)

    # Generate and download PDF
    report_file = generate_pdf(stats)
    with open(report_file, "rb") as f:
        st.download_button("📄 Download PDF Summary", f, file_name="summary_report_duckdb.pdf")
