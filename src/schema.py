"""Dublin Core and library inventory field definitions."""

from dataclasses import dataclass, field


@dataclass
class FieldRule:
    name: str
    dublin_core: str
    required: bool
    description: str
    aliases: list[str] = field(default_factory=list)


# Standard library inventory schema mapped to Dublin Core elements
INVENTORY_SCHEMA: list[FieldRule] = [
    FieldRule("title", "dc:title", True, "Title of the item"),
    FieldRule("creator", "dc:creator", True, "Author or creator"),
    FieldRule("subject", "dc:subject", False, "Subject keywords or classification"),
    FieldRule("description", "dc:description", False, "Physical description or summary"),
    FieldRule("publisher", "dc:publisher", False, "Publisher name"),
    FieldRule("date", "dc:date", False, "Publication date (YYYY or YYYY-MM-DD)"),
    FieldRule("identifier", "dc:identifier", False, "ISBN or other identifier", ["isbn"]),
    FieldRule("type", "dc:type", False, "Material type (book, dvd, journal, etc.)"),
    FieldRule("language", "dc:language", False, "Language code (ISO 639-1)"),
    FieldRule("barcode", "local:barcode", True, "Item barcode for circulation"),
    FieldRule("rfid_tag", "local:rfid", False, "RFID tag identifier"),
    FieldRule("call_number", "local:call_number", False, "Shelving location / call number"),
    FieldRule("location", "local:location", False, "Branch or collection location"),
    FieldRule("status", "local:status", False, "Circulation status"),
]

REQUIRED_FIELDS = [f.name for f in INVENTORY_SCHEMA if f.required]

# Map common column header variants to canonical field names
FIELD_ALIASES: dict[str, str] = {}
for rule in INVENTORY_SCHEMA:
    FIELD_ALIASES[rule.name.lower()] = rule.name
    for alias in rule.aliases:
        FIELD_ALIASES[alias.lower()] = rule.name

# Common alternate headers found in real library exports
EXTRA_ALIASES = {
    "author": "creator",
    "authors": "creator",
    "pub_date": "date",
    "publication_date": "date",
    "pubdate": "date",
    "isbn": "identifier",
    "isbn13": "identifier",
    "isbn10": "identifier",
    "item_barcode": "barcode",
    "item id": "barcode",
    "item_id": "barcode",
    "rfid": "rfid_tag",
    "rfid tag": "rfid_tag",
    "call no": "call_number",
    "call_no": "call_number",
    "callnumber": "call_number",
    "branch": "location",
    "material_type": "type",
    "format": "type",
    "lang": "language",
}

FIELD_ALIASES.update(EXTRA_ALIASES)

VALID_MATERIAL_TYPES = {
    "book", "ebook", "dvd", "cd", "audiobook", "journal",
    "magazine", "newspaper", "map", "score", "reference",
    "kit", "game", "equipment", "other",
}

VALID_STATUSES = {
    "available", "checked out", "on hold", "in transit",
    "missing", "lost", "withdrawn", "processing", "on order",
}
