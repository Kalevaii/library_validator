"""Barcode, ISBN, and RFID validation using regex and check-digit algorithms."""

import re
from dataclasses import dataclass


@dataclass
class ValidationResult:
    valid: bool
    value: str
    message: str = ""
    is_warning: bool = False


# --- ISBN ---

ISBN10_RE = re.compile(r"^(?:\d{9}[\dXx]|\d{1,5}-\d{1,7}-\d{1,6}-[\dXx])$")
ISBN13_RE = re.compile(r"^(?:97[89]\d{10}|97[89]-\d-?\d{3}-?\d{5}-?\d)$")


def _strip_isbn(value: str) -> str:
    return re.sub(r"[^0-9Xx]", "", value.strip())


def _isbn10_check(digits: str) -> bool:
    if len(digits) != 10:
        return False
    total = sum((10 - i) * int(digits[i]) for i in range(9))
    check = digits[9].upper()
    expected = 11 - (total % 11)
    if expected == 11:
        expected = 0
    elif expected == 10:
        expected = "X"
    else:
        expected = str(expected)
    return str(expected) == check


def _isbn13_check(digits: str) -> bool:
    if len(digits) != 13:
        return False
    total = sum(int(digits[i]) * (1 if i % 2 == 0 else 3) for i in range(12))
    check = (10 - (total % 10)) % 10
    return check == int(digits[12])


def validate_isbn(value: str) -> ValidationResult:
    if not value or not str(value).strip():
        return ValidationResult(False, value, "ISBN is empty")

    raw = str(value).strip()
    digits = _strip_isbn(raw)

    if len(digits) == 10 and _isbn10_check(digits):
        return ValidationResult(True, raw, "Valid ISBN-10")
    if len(digits) == 13 and _isbn13_check(digits):
        return ValidationResult(True, raw, "Valid ISBN-13")

    if len(digits) in (10, 13):
        return ValidationResult(False, raw, f"Invalid ISBN check digit ({len(digits)} digits)")
    return ValidationResult(False, raw, f"Invalid ISBN format ({len(digits)} digits, expected 10 or 13)")


# --- Barcode ---

# Common library barcode patterns:
#   Code 39:  alphanumeric + limited symbols, often 8-14 chars
#   Code 128: numeric, often 14 digits (includes check digit)
#   Generic library item barcodes: typically 8-20 alphanumeric chars
LIBRARY_BARCODE_RE = re.compile(r"^[A-Za-z0-9\-]{6,20}$")
NUMERIC_BARCODE_RE = re.compile(r"^\d{8,14}$")


def validate_barcode(value: str) -> ValidationResult:
    if not value or not str(value).strip():
        return ValidationResult(False, value, "Barcode is empty")

    raw = str(value).strip()

    if not LIBRARY_BARCODE_RE.match(raw):
        return ValidationResult(
            False, raw,
            "Invalid barcode format (must be 6-20 alphanumeric characters or hyphens)",
        )

    # Warn on suspicious patterns but still accept structurally valid barcodes
    if raw.lower() in ("test", "null", "none", "00000000", "12345678"):
        return ValidationResult(False, raw, "Barcode appears to be a placeholder value")

    if NUMERIC_BARCODE_RE.match(raw) and not _numeric_barcode_check(raw):
        return ValidationResult(
            True, raw,
            "Numeric barcode check digit could not be verified",
            is_warning=True,
        )

    return ValidationResult(True, raw, "Valid barcode")


def _numeric_barcode_check(barcode: str) -> bool:
    """Mod-10 check for standard numeric library barcodes (EAN-13 style)."""
    if len(barcode) < 8:
        return True  # too short for check digit validation
    digits = barcode[:-1]
    check = int(barcode[-1])
    total = sum(int(d) * (3 if i % 2 == 0 else 1) for i, d in enumerate(reversed(digits)))
    expected = (10 - (total % 10)) % 10
    return check == expected


# --- RFID ---

# HF tags: 24 hex chars (96-bit UID)
# UHF EPC Gen2: variable length hex, typically 24-32 chars
RFID_HF_RE = re.compile(r"^[0-9A-Fa-f]{24}$")
RFID_UHF_RE = re.compile(r"^[0-9A-Fa-f]{16,32}$")
RFID_EPC_URI_RE = re.compile(r"^urn:epc:(?:id|tag|raw):[\w.:]+$", re.IGNORECASE)


def validate_rfid(value: str) -> ValidationResult:
    if not value or not str(value).strip():
        return ValidationResult(False, value, "RFID tag is empty")

    raw = str(value).strip()

    if RFID_EPC_URI_RE.match(raw):
        return ValidationResult(True, raw, "Valid EPC URI format")

    if RFID_HF_RE.match(raw):
        return ValidationResult(True, raw, "Valid HF RFID tag (96-bit UID)")

    if RFID_UHF_RE.match(raw):
        return ValidationResult(True, raw, "Valid UHF RFID tag")

    return ValidationResult(
        False, raw,
        "Invalid RFID format (expected 24-char hex for HF, 16-32 hex for UHF, or EPC URI)",
    )


# --- Date ---

DATE_RE = re.compile(r"^\d{4}(-\d{2}(-\d{2})?)?$")


def validate_date(value: str) -> ValidationResult:
    if not value or not str(value).strip():
        return ValidationResult(False, value, "Date is empty")
    raw = str(value).strip()
    if DATE_RE.match(raw):
        return ValidationResult(True, raw, "Valid date format")
    return ValidationResult(False, raw, "Invalid date (expected YYYY or YYYY-MM-DD)")


# --- Language ---

LANG_RE = re.compile(r"^[a-z]{2,3}(-[A-Z]{2})?$")


def validate_language(value: str) -> ValidationResult:
    if not value or not str(value).strip():
        return ValidationResult(False, value, "Language code is empty")
    raw = str(value).strip()
    if LANG_RE.match(raw):
        return ValidationResult(True, raw, "Valid ISO 639 language code")
    return ValidationResult(False, raw, "Invalid language code (expected ISO 639, e.g. 'en')")
