import re
from decimal import Decimal, InvalidOperation
import httpx
import json


def find_value(patterns: list[str], text: str) -> str | None:
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        if match:
            return match.group(1).strip()

    return None


def parse_amount(value: str | None) -> Decimal | None:
    if not value:
        return None

    cleaned = value.replace(",", "").strip()

    try:
        return Decimal(cleaned)
    except InvalidOperation:
        return None


def parse_invoice(text: str) -> dict:
    document_number = find_value(
        [
            r"(?:invoice\s*(?:no|number|#))\s*[:#-]?\s*([A-Z0-9/-]+)",
            r"(?:receipt\s*(?:no|number|#))\s*[:#-]?\s*([A-Z0-9/-]+)",
        ],
        text,
    )

    document_date = find_value(
        [
            r"(?:invoice\s*date|receipt\s*date|date)\s*[:#-]?\s*"
            r"(\d{1,4}[/-]\d{1,2}[/-]\d{1,4})",
        ],
        text,
    )

    total_text = find_value(
        [
            r"(?:grand\s*total|total\s*due|amount\s*due|total)"
            r"\s*[:\-]?\s*(?:RM|MYR|USD|SGD)?\s*"
            r"(\d[\d,]*\.\d{2})",
        ],
        text,
    )

    subtotal_text = find_value(
        [
            r"(?:subtotal|sub-total)\s*[:\-]?\s*"
            r"(?:RM|MYR|USD|SGD)?\s*(\d[\d,]*\.\d{2})",
        ],
        text,
    )

    tax_text = find_value(
        [
            r"(?:tax|SST|GST|VAT)\s*[:\-]?\s*"
            r"(?:RM|MYR|USD|SGD)?\s*(\d[\d,]*\.\d{2})",
        ],
        text,
    )

    return {
        "document_number": document_number,
        "document_date": document_date,
        "subtotal": parse_amount(subtotal_text),
        "tax_total": parse_amount(tax_text),
        "total": parse_amount(total_text),
        "currency": (
            "MYR" if re.search(r"\b(?:RM|MYR)\b", text, re.I)
            else "USD" if re.search(r"\bUSD\b", text, re.I)
            else "SGD" if re.search(r"\bSGD\b", text, re.I)
            else None
        ),
    }

document_schema = {
    "type": "object",
    "properties": {
        "document_number": {
            "type": ["string", "null"]
        },
        "vendor": {
            "type": ["string", "null"]
        },
        "document_date": {
            "type": ["string", "null"]
        },
        "currency": {
            "type": ["string", "null"]
        },
        "subtotal": {
            "type": ["number", "null"]
        },
        "tax_total": {
                    "type": ["number", "null"]
                },
        "total": {
                    "type": ["number", "null"]
                }
    },
    "required": [
        "document_number",
        "vendor",
        "document_date",
        "currency",
        "subtotal",
        "tax_total",
        "total"
    ],
    "additionalProperties": False
}

async def extract_document(ocr_text: str)-> dict:
    messages = [
            {
                "role": "system",
                "content": """
        You are an invoice data extraction assistant.

        Extract the following fields from the provided invoice text:
        - document_number
        - vendor
        - document_date
        - currency
        - subtotal
        - tax_total
        - total

        Return ONLY a valid JSON object using exactly this format:

        {
            "document_number": "INV-001",
            "vendor": "ABC Trading",
            "document_date": "2026-10-18",
            "currency": "MYR",
            "subtotal": 120.00,
            "tax_total": 5.50,
            "total": 125.50
        }

        Rules:
        1. Return only valid JSON. Do not include explanations, Markdown, or code fences.
        2. Use null for any field that cannot be determined from the OCR text.
        3. Format document_date as YYYY-MM-DD when possible.
        4. Return currency as a three-letter ISO code, such as MYR, USD, or SGD.
        5. Return subtotal, tax_total, and total as JSON numbers, not strings.
        6. Extract values only from the provided text. Never invent values.
        7. Distinguish subtotal, tax_total, and the final total or amount due.
        8. Do not assume tax is zero if the tax amount is missing.
        9. Return all seven fields, even when some values are null.
        """
            },
            {
                "role": "user",
                "content": f"Extract invoice data from this OCR text:\n\n{ocr_text}"
            }
        ]

    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            "http://host.docker.internal:11465/api/chat",
            json={
                "model": "qwen3:1.7b",
                "messages": messages,
                "stream": False,
                "format": document_schema,
            },
        )

    response.raise_for_status()

    data = response.json()
    assistant_message = data["message"]["content"]

    try:
        document_data = json.loads(assistant_message)
    except json.JSONDecodeError as exc:
        raise ValueError(
            "LLM returned invalid JSON"
        ) from exc

    if not isinstance(document_data, dict):
        raise ValueError("LLM response must be a JSON object")

    return document_data