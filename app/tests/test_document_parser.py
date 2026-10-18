from decimal import Decimal

from app.document_parser import parse_invoice,extract_document
from app.validation import validate_document


def test_parse_basic_invoice():
    text = """
    Invoice No: INV-2026-001
    Invoice Date: 17/10/2026
    Subtotal: RM 100.00
    SST: RM 8.00
    Grand Total: RM 108.00
    """

    result = extract_document(text)

    assert result["document_number"] == "INV-2026-001"
    assert result["subtotal"] == Decimal("100.00")
    assert result["tax_total"] == Decimal("8.00")
    assert result["total"] == Decimal("108.00")


def test_validation_flags_missing_total():
    result = {
        "document_number": "INV-001",
        "document_date": "17/10/2026",
        "subtotal": Decimal("100.00"),
        "tax_total": Decimal("8.00"),
        "total": None,
    }

    issues = validate_document(result)

    assert "Missing total amount" in issues