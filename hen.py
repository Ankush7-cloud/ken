import streamlit as st
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime

# Function to calculate stats
def compute_stats(df, columns):
    stats = {}
    for col in columns:
        if col in df.columns:
            series = pd.to_numeric(df[col], errors='coerce')  # handles any non-numeric entries
            stats[col] = {
                'mean': round(series.mean(), 2),
                'std': round(series.std(), 2),
                'max': round(series.max(), 2),
                'min': round(series.min(), 2)
            }
    return stats

# Function to generate PDF report
def generate_pdf(stats, filename="summary_report.pdf"):
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
st.title("📈 COVID Summary: Mean & Standard Deviation")

uploaded_file = st.file_uploader("Upload counter_wise_latest2.csv", type="csv")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.success("✅ File Uploaded Successfully")
    st.dataframe(df.head())

    selected_columns = ["New cases", "New deaths"]
    summary_stats = compute_stats(df, selected_columns)

    st.subheader("📋 Summary Table")
    st.write(pd.DataFrame(summary_stats).T)

    report_path = generate_pdf(summary_stats)
    with open(report_path, "rb") as f:
        st.download_button("📄 Download PDF Summary", f, file_name="summary_report.pdf")
