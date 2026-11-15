from datetime import date, datetime
from decimal import Decimal


def first(response):
    """Return the first returned row, or None, like cursor.fetchone()."""
    return response.data[0] if response.data else None


def serialize(value):
    """Convert Pydantic Python values into JSON-compatible Supabase payloads."""
    if isinstance(value, dict):
        return {key: serialize(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [serialize(item) for item in value]
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    return value
