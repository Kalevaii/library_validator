#!/usr/bin/env python3
"""Streamlit web UI for the Library Metadata & Barcode Validator."""

import sys
import tempfile
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent))

from src.engine import Severity, validate_inventory
from src.report import export_issues_csv, format_issues_table
from src.schema import INVENTORY_SCHEMA

ROOT = Path(__file__).parent
SAMPLES = ROOT / "samples"


def render_report(report, filename: str) -> None:
    st.subheader(f"Results: {filename}")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Records", report.total_records)
    col2.metric("Errors", report.error_count)
    col3.metric("Warnings", report.warning_count)
    col4.metric("Accuracy", f"{report.accuracy_pct}%")

    if report.columns_missing:
        st.error(f"Missing required columns: {', '.join(report.columns_missing)}")

    if report.issues:
        severity_filter = st.radio(
            "Filter by severity",
            ["All", "Errors only", "Warnings only"],
            horizontal=True,
            key=f"filter_{filename}",
        )

        sev = None
        if severity_filter == "Errors only":
            sev = Severity.ERROR
        elif severity_filter == "Warnings only":
            sev = Severity.WARNING

        st.code(format_issues_table(report, sev), language="text")

        st.download_button(
            "Download issues as CSV",
            export_issues_csv(report),
            file_name=f"{Path(filename).stem}_issues.csv",
            mime="text/csv",
            key=f"download_{filename}",
        )
    else:
        st.success("All records passed validation!")


st.set_page_config(
    page_title="Library Metadata Validator",
    page_icon="📚",
    layout="wide",
)

st.title("Library Metadata & Barcode Validator")
st.markdown(
    "Upload library inventory files (CSV or JSON) to check metadata quality, "
    "barcode validity, and RFID tag format against Dublin Core schema guidelines."
)

with st.sidebar:
    st.header("About")
    st.markdown(
        "**Checks performed:**\n"
        "- Required field completeness\n"
        "- ISBN-10/13 check digit validation\n"
        "- Barcode format & check digit\n"
        "- RFID tag format (HF/UHF/EPC)\n"
        "- Duplicate barcode & RFID detection\n"
        "- Date, language, and material type validation"
    )

    with st.expander("Expected Schema"):
        for rule in INVENTORY_SCHEMA:
            req = " **(required)**" if rule.required else ""
            st.markdown(f"- `{rule.name}` → {rule.dublin_core}{req}")

    st.divider()
    st.caption("Built by Pranaya Poudel · Python · Pandas · Streamlit")

col_demo, col_upload = st.columns([1, 2])
with col_demo:
    run_demo = st.button("Try demo with sample data", use_container_width=True, type="primary")

uploaded_files = st.file_uploader(
    "Or upload your own inventory file(s)",
    type=["csv", "json"],
    accept_multiple_files=True,
)

if run_demo:
    st.divider()
    demo_path = SAMPLES / "inventory_with_errors.csv"
    report = validate_inventory(demo_path)
    render_report(report, "inventory_with_errors.csv (demo)")

    with st.expander("View sample data"):
        st.dataframe(pd.read_csv(demo_path), use_container_width=True)

elif uploaded_files:
    for uploaded in uploaded_files:
        st.divider()

        with tempfile.NamedTemporaryFile(suffix=Path(uploaded.name).suffix, delete=False) as tmp:
            tmp.write(uploaded.getvalue())
            tmp_path = tmp.name

        report = validate_inventory(tmp_path)
        Path(tmp_path).unlink(missing_ok=True)
        render_report(report, uploaded.name)

else:
    st.info("Click **Try demo with sample data** or upload a CSV/JSON inventory file.")

    sample_path = SAMPLES / "inventory_with_errors.csv"
    if sample_path.exists():
        st.markdown("**Preview of sample inventory data:**")
        st.dataframe(pd.read_csv(sample_path), use_container_width=True)
