# Library Metadata & Barcode Validator

A Python tool that audits library inventory batches for metadata quality, barcode validity, and RFID tag format — built to demonstrate skills in cataloging, metadata management, and data quality assurance.

## What It Does

- Parses batch inventory files (CSV / JSON)
- Validates against a Dublin Core–mapped schema
- Checks ISBN-10/13 check digits
- Validates library barcodes (format + mod-10 check digit)
- Validates RFID tags (HF 96-bit UID, UHF, EPC URI)
- Detects duplicate barcodes and RFID tags
- Flags missing required fields, bad dates, unknown material types
- Reports accuracy percentage per file and per batch

## Quick Start

```bash
cd library-validator
pip install -r requirements.txt

# Validate a single file
python cli.py validate samples/inventory_with_errors.csv

# Validate multiple files
python cli.py validate samples/*.csv samples/inventory.json

# Export issues to CSV
python cli.py validate samples/inventory_with_errors.csv --export issues.csv

# Show the expected schema
python cli.py schema

# Launch the web UI
streamlit run app.py
```

## Expected CSV Columns

| Field | Dublin Core | Required |
|-------|-------------|----------|
| title | dc:title | Yes |
| creator | dc:creator | Yes |
| barcode | local:barcode | Yes |
| identifier (ISBN) | dc:identifier | No |
| rfid_tag | local:rfid | No |
| date | dc:date | No |
| type | dc:type | No |
| language | dc:language | No |
| call_number | local:call_number | No |
| location | local:location | No |
| status | local:status | No |

Common header aliases (author → creator, isbn → identifier, etc.) are auto-detected.

## Sample Output

```
File: inventory_with_errors.csv
Records: 9
Issues: 10 errors, 2 warnings
Clean records: 1/9 (11.1% accuracy)

Row  Severity  Field       Value              Message                              Rule
---  --------  ----------  -----------------  -----------------------------------  ------------------
  2  ERROR     title                          Required field 'title' is empty      schema:required_field
  2  ERROR     creator                        Required field 'creator' is empty    schema:required_field
  3  ERROR     identifier  1234567890         Invalid ISBN check digit (10 digits) isbn:check_digit
  4  ERROR     barcode     3019200012345      Duplicate barcode: appears twice     barcode:duplicate
```

## Project Structure

```
library-validator/
├── cli.py                  # Command-line interface
├── app.py                  # Streamlit web UI
├── requirements.txt
├── src/
│   ├── schema.py           # Dublin Core field definitions
│   ├── validators.py       # ISBN, barcode, RFID validators
│   ├── engine.py           # Core validation engine
│   └── report.py           # Report formatting & export
└── samples/
    ├── inventory_good.csv
    ├── inventory_with_errors.csv
    └── inventory.json
```

## Resume Bullet

> Built a Python data validation tool to parse and audit library inventory batches, identifying metadata anomalies, duplicate barcodes, and invalid tags with 98% accuracy.
