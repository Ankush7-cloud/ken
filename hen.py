import streamlit as st
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime

# Function to compute statistics using Pandas
def compute_stats(df, columns):
    summary = {}
    for col in columns:
        clean_col = pd.to_numeric(df[col], errors='coerce')  # Convert to numeric
        summary[col] = {
            "mean": round(clean_col.mean(), 2),
            "std": round(clean_col.std(), 2),
            "max": round(clean_col.max(), 2),
            "min": round(clean_col.min(), 2)
        }
    return summary

# Function to generate PDF
def generate_pdf(stats, filename="summary_report.pdf"):
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    y = height - 50

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, "COVID Summary Report (via Pandas)")
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
st.title("📊 COVID Summary Report ")

uploaded_file = st.file_uploader("Upload counter_wise_latest2.csv", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.success("✅ File Uploaded Successfully")
    st.dataframe(df.head())

    # Ensure required columns exist
    required_cols = ['New cases', 'New deaths']
    if not all(col in df.columns for col in required_cols):
        st.error("❌ Required columns ('New cases', 'New deaths') not found in the file.")
    else:
        # Compute stats
        stats = compute_stats(df, required_cols)

        # Show stats table
        st.subheader("📋 Summary Statistics")
        stats_df = pd.DataFrame.from_dict(stats, orient='index')
        st.write(stats_df)

        # Generate PDF and provide download button
        pdf_file = generate_pdf(stats)
        with open(pdf_file, "rb") as f:
            st.download_button("📄 Download PDF Summary", f, file_name="summary_report.pdf")
