# app/validation.py

from decimal import Decimal


def validate_document(data: dict) -> list[str]:
    issues = []

    if not data.get("document_number"):
        issues.append("Missing invoice or receipt number")

    if not data.get("document_date"):
        issues.append("Missing document date")

    if data.get("total") is None:
        issues.append("Missing total amount")

    subtotal = data.get("subtotal")
    tax = data.get("tax_total")
    total = data.get("total")

    if subtotal is not None and tax is not None and total is not None:
        expected = Decimal(str(subtotal)) + Decimal(str(tax))

        if abs(expected - Decimal(str(total))) > Decimal("0.02"):
            issues.append("Subtotal plus tax does not match total")

    return issues