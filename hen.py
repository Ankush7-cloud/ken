import streamlit as st
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime
import os

# Function to calculate statistics
def calculate_summary(df, columns):
    summary = {}
    for col in columns:
        if col in df.columns:
            summary[col] = {
                'max': df[col].max(),
                'min': df[col].min(),
                'average': df[col].mean()
            }
    return summary

# Function to generate PDF report
def generate_summary_pdf(summary_dict, filename="summary_report.pdf"):
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    y = height - 50

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, "COVID Data Summary Report")
    y -= 30

    c.setFont("Helvetica", 12)
    c.drawString(50, y, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    y -= 40

    c.setFont("Helvetica-Bold", 12)
    for col, stats in summary_dict.items():
        c.drawString(50, y, f"Column: {col}")
        y -= 20
        c.setFont("Helvetica", 11)
        c.drawString(70, y, f"Max: {stats['max']}")
        y -= 15
        c.drawString(70, y, f"Min: {stats['min']}")
        y -= 15
        c.drawString(70, y, f"Average: {round(stats['average'], 2)}")
        y -= 30
        c.setFont("Helvetica-Bold", 12)
        if y < 100:
            c.showPage()
            y = height - 50

    c.save()
    return filename

# Streamlit App
st.title("📊 COVID Summary Report Generator")

uploaded_file = st.file_uploader("Upload counter_wise_latest2.csv", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    st.success("✅ File uploaded successfully")
    st.dataframe(df.head())

    columns_to_summarize = ['new_deaths', 'new_cases', 'recovered']
    summary = calculate_summary(df, columns_to_summarize)

    st.subheader("📋 Summary Table")
    st.write(pd.DataFrame(summary).T)

    report_path = generate_summary_pdf(summary)
    with open(report_path, "rb") as f:
        st.download_button("📄 Download PDF Summary", f, file_name="summary_report.pdf")

