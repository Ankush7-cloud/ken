import streamlit as st
import pandas as pd
import sqlite3
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime
import os

# Function to insert data into SQLite using sqlite3
def insert_into_db(df, table_name, db_name="uploaded_data.db"):
    conn = sqlite3.connect(db_name)
    df.to_sql(table_name, conn, if_exists="replace", index=False)
    conn.commit()
    conn.close()

# Function to generate a summary report PDF using ReportLab
def generate_pdf_report(df, filename="summary_report.pdf"):
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, "Summary Report")

    c.setFont("Helvetica", 12)
    c.drawString(50, height - 80, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    c.drawString(50, height - 100, f"Number of Rows: {df.shape[0]}")
    c.drawString(50, height - 120, f"Number of Columns: {df.shape[1]}")

    y = height - 160
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Column Summary:")
    y -= 20
    c.setFont("Helvetica", 10)
    for col in df.columns:
        col_type = str(df[col].dtype)
        c.drawString(60, y, f"{col}: {col_type}")
        y -= 15
        if y < 50:
            c.showPage()
            y = height - 50

    c.save()
    return filename

# Streamlit UI
st.title("📥 CSV Ingestion Page ")

uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.success("✅ File Uploaded Successfully")
    st.dataframe(df.head())

    table_name = os.path.splitext(uploaded_file.name)[0].replace("-", "").replace(" ", "")
    
    # Save to database using sqlite3
    insert_into_db(df, table_name)
    st.success(f"✅ Data successfully saved into SQLite table: {table_name}")

    # Generate and download summary report
    report_file = generate_pdf_report(df)
    with open(report_file, "rb") as f:
        st.download_button("📄 Download Summary Report (PDF)", f, file_name=report_file)

