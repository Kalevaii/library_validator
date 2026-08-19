"""Core validation engine — loads inventory files and runs all checks."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

import pandas as pd

from .schema import (
    FIELD_ALIASES,
    INVENTORY_SCHEMA,
    REQUIRED_FIELDS,
    VALID_MATERIAL_TYPES,
    VALID_STATUSES,
)
from .validators import (
    validate_barcode,
    validate_date,
    validate_isbn,
    validate_language,
    validate_rfid,
)


class Severity(str, Enum):
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"


@dataclass
class Issue:
    row: int  # 1-indexed data row (excluding header)
    field: str
    value: str
    severity: Severity
    message: str
    rule: str


@dataclass
class ValidationReport:
    filename: str
    total_records: int
    issues: list[Issue] = field(default_factory=list)
    columns_found: list[str] = field(default_factory=list)
    columns_missing: list[str] = field(default_factory=list)

    @property
    def error_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == Severity.ERROR)

    @property
    def warning_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == Severity.WARNING)

    @property
    def clean_records(self) -> int:
        bad_rows = {i.row for i in self.issues if i.severity == Severity.ERROR}
        return self.total_records - len(bad_rows)

    @property
    def accuracy_pct(self) -> float:
        if self.total_records == 0:
            return 100.0
        return round(self.clean_records / self.total_records * 100, 1)


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Rename columns to canonical field names using alias map."""
    rename_map = {}
    for col in df.columns:
        key = col.strip().lower()
        if key in FIELD_ALIASES:
            rename_map[col] = FIELD_ALIASES[key]
    return df.rename(columns=rename_map)


def load_inventory(path: str | Path) -> pd.DataFrame:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    suffix = path.suffix.lower()
    if suffix == ".csv":
        df = pd.read_csv(path, dtype=str, keep_default_na=False)
    elif suffix == ".json":
        with open(path) as f:
            data = json.load(f)
        if isinstance(data, list):
            df = pd.DataFrame(data)
        elif isinstance(data, dict) and "records" in data:
            df = pd.DataFrame(data["records"])
        else:
            raise ValueError("JSON must be a list of records or {\"records\": [...]}")
        df = df.astype(str).replace("nan", "")
    else:
        raise ValueError(f"Unsupported file type: {suffix} (use .csv or .json)")

    return _normalize_columns(df)


def validate_inventory(path: str | Path) -> ValidationReport:
    df = load_inventory(path)
    report = ValidationReport(
        filename=str(Path(path).name),
        total_records=len(df),
        columns_found=list(df.columns),
    )

    # Check for missing required columns
    for req in REQUIRED_FIELDS:
        if req not in df.columns:
            report.columns_missing.append(req)
            report.issues.append(Issue(
                row=0,
                field=req,
                value="",
                severity=Severity.ERROR,
                message=f"Required column '{req}' is missing from file",
                rule="schema:required_column",
            ))

    if report.columns_missing:
        return report  # can't validate rows without required columns

    # Row-level validation
    for idx, row in df.iterrows():
        row_num = idx + 1  # 1-indexed for human readability
        _check_required_fields(row, row_num, report)
        _check_barcode(row, row_num, report)
        _check_isbn(row, row_num, report)
        _check_rfid(row, row_num, report)
        _check_date(row, row_num, report)
        _check_language(row, row_num, report)
        _check_type(row, row_num, report)
        _check_status(row, row_num, report)

    # Cross-record checks (duplicates)
    _check_duplicates(df, report)

    return report


def _check_required_fields(row: pd.Series, row_num: int, report: ValidationReport) -> None:
    for field_name in REQUIRED_FIELDS:
        val = str(row.get(field_name, "")).strip()
        if not val:
            report.issues.append(Issue(
                row=row_num,
                field=field_name,
                value=val,
                severity=Severity.ERROR,
                message=f"Required field '{field_name}' is empty",
                rule="schema:required_field",
            ))


def _check_barcode(row: pd.Series, row_num: int, report: ValidationReport) -> None:
    val = str(row.get("barcode", "")).strip()
    if not val:
        return  # already flagged by required check
    result = validate_barcode(val)
    if not result.valid:
        report.issues.append(Issue(
            row=row_num, field="barcode", value=val,
            severity=Severity.ERROR, message=result.message,
            rule="barcode:format",
        ))
    elif result.is_warning:
        report.issues.append(Issue(
            row=row_num, field="barcode", value=val,
            severity=Severity.WARNING, message=result.message,
            rule="barcode:check_digit",
        ))


def _check_isbn(row: pd.Series, row_num: int, report: ValidationReport) -> None:
    val = str(row.get("identifier", "")).strip()
    if not val:
        return
    result = validate_isbn(val)
    if not result.valid:
        report.issues.append(Issue(
            row=row_num, field="identifier", value=val,
            severity=Severity.ERROR, message=result.message,
            rule="isbn:check_digit",
        ))


def _check_rfid(row: pd.Series, row_num: int, report: ValidationReport) -> None:
    val = str(row.get("rfid_tag", "")).strip()
    if not val:
        return
    result = validate_rfid(val)
    if not result.valid:
        report.issues.append(Issue(
            row=row_num, field="rfid_tag", value=val,
            severity=Severity.ERROR, message=result.message,
            rule="rfid:format",
        ))


def _check_date(row: pd.Series, row_num: int, report: ValidationReport) -> None:
    val = str(row.get("date", "")).strip()
    if not val:
        return
    result = validate_date(val)
    if not result.valid:
        report.issues.append(Issue(
            row=row_num, field="date", value=val,
            severity=Severity.WARNING, message=result.message,
            rule="date:format",
        ))


def _check_language(row: pd.Series, row_num: int, report: ValidationReport) -> None:
    val = str(row.get("language", "")).strip()
    if not val:
        return
    result = validate_language(val)
    if not result.valid:
        report.issues.append(Issue(
            row=row_num, field="language", value=val,
            severity=Severity.WARNING, message=result.message,
            rule="language:format",
        ))


def _check_type(row: pd.Series, row_num: int, report: ValidationReport) -> None:
    val = str(row.get("type", "")).strip().lower()
    if not val:
        return
    if val not in VALID_MATERIAL_TYPES:
        report.issues.append(Issue(
            row=row_num, field="type", value=val,
            severity=Severity.WARNING,
            message=f"Unknown material type '{val}' (expected one of: {', '.join(sorted(VALID_MATERIAL_TYPES))})",
            rule="type:enum",
        ))


def _check_status(row: pd.Series, row_num: int, report: ValidationReport) -> None:
    val = str(row.get("status", "")).strip().lower()
    if not val:
        return
    if val not in VALID_STATUSES:
        report.issues.append(Issue(
            row=row_num, field="status", value=val,
            severity=Severity.WARNING,
            message=f"Unknown status '{val}'",
            rule="status:enum",
        ))


def _check_duplicates(df: pd.DataFrame, report: ValidationReport) -> None:
    for col, rule in [("barcode", "barcode:duplicate"), ("rfid_tag", "rfid:duplicate")]:
        if col not in df.columns:
            continue
        series = df[col].str.strip()
        series = series[series != ""]
        dupes = series[series.duplicated(keep=False)]
        for idx, val in dupes.items():
            report.issues.append(Issue(
                row=idx + 1,
                field=col,
                value=val,
                severity=Severity.ERROR,
                message=f"Duplicate {col}: '{val}' appears more than once",
                rule=rule,
            ))


def validate_batch(paths: list[str | Path]) -> list[ValidationReport]:
    return [validate_inventory(p) for p in paths]
