from decimal import Decimal, InvalidOperation


def amount_value(value):
    if isinstance(value, dict):
        value = value.get("amount")

    if value is None:
        return None

    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return None


def currency_value(value):
    if isinstance(value, dict):
        return value.get("currency")

    return None


def first_field(fields, *names):
    """Return the first non-empty field from a list of possible names."""
    for name in names:
        value = fields.get(name)

        if value not in (None, ""):
            return value

    return None


def text_value(value):
    if value is None:
        return None

    if isinstance(value, dict):
        # Currency objects are handled separately.
        return None

    return str(value)