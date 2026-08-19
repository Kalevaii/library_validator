"""Format validation reports for CLI and export."""

from __future__ import annotations

import csv
import io
from tabulate import tabulate

from .engine import Severity, ValidationReport


def format_summary(report: ValidationReport) -> str:
    lines = [
        f"File: {report.filename}",
        f"Records: {report.total_records}",
        f"Issues: {report.error_count} errors, {report.warning_count} warnings",
        f"Clean records: {report.clean_records}/{report.total_records} ({report.accuracy_pct}% accuracy)",
    ]
    if report.columns_missing:
        lines.append(f"Missing columns: {', '.join(report.columns_missing)}")
    return "\n".join(lines)


def format_issues_table(report: ValidationReport, severity: Severity | None = None) -> str:
    issues = report.issues
    if severity:
        issues = [i for i in issues if i.severity == severity]

    if not issues:
        return "No issues found."

    rows = [
        [i.row, i.severity.value, i.field, i.value[:30], i.message, i.rule]
        for i in issues
    ]
    headers = ["Row", "Severity", "Field", "Value", "Message", "Rule"]
    return tabulate(rows, headers=headers, tablefmt="simple")


def export_issues_csv(report: ValidationReport) -> str:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["row", "severity", "field", "value", "message", "rule"])
    for i in report.issues:
        writer.writerow([i.row, i.severity.value, i.field, i.value, i.message, i.rule])
    return output.getvalue()


def format_batch_summary(reports: list[ValidationReport]) -> str:
    total = sum(r.total_records for r in reports)
    total_errors = sum(r.error_count for r in reports)
    total_warnings = sum(r.warning_count for r in reports)
    total_clean = sum(r.clean_records for r in reports)
    accuracy = round(total_clean / total * 100, 1) if total else 100.0

    lines = [
        f"Batch validation complete — {len(reports)} file(s)",
        f"Total records: {total}",
        f"Total issues: {total_errors} errors, {total_warnings} warnings",
        f"Overall accuracy: {accuracy}%",
        "",
    ]
    for r in reports:
        lines.append(f"  {r.filename}: {r.clean_records}/{r.total_records} clean ({r.accuracy_pct}%)")
    return "\n".join(lines)
