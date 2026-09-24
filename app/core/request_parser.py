"""Reading and validating form fields, the way Nest pipes do.

Controllers never touch request.form directly: they ask for a field by name
and get back a clean value or an AppError explaining what is missing.
"""
from flask import request

from app.core.exceptions import AppError


def text(field: str, required: bool = False, label: str | None = None) -> str | None:
    """Read a text field, trimmed.

    Returns None when empty, which is what Oracle expects for the nullable
    columns (comments.user_id and comments.url).
    """
    value = (request.form.get(field) or "").strip()
    if value:
        return value
    if required:
        raise AppError(f"El campo {label or field} es obligatorio.")
    return None


def integer(field: str, required: bool = False,
            label: str | None = None) -> int | None:
    """Read a field that must hold a whole number."""
    value = text(field, required, label)
    if value is None:
        return None
    try:
        return int(value)
    except ValueError:
        raise AppError(f"El campo {label or field} debe ser un numero.") from None
