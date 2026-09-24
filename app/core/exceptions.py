"""Turning Oracle failures into messages a reader can act on.

The PL/SQL packages raise business errors with RAISE_APPLICATION_ERROR in the
ORA-20001..ORA-20013 range. Those already carry a sentence written for the
end user, so we only strip the "ORA-xxxxx: " prefix and the PL/SQL stack.

Constraint violations (ORA-00001, ORA-02290, ...) name the internal
constraint instead, so those get a hand written message.
"""
import oracledb

# Oracle reserves -20000..-20999 for RAISE_APPLICATION_ERROR.
BUSINESS_ERROR_PREFIX = "ORA-2"

UNIQUE_CONSTRAINT_MESSAGES = {
    "UK_BLOG_USERS_EMAIL": "Ya existe un usuario con ese correo.",
    "UK_TAGS_NAME": "Ya existe una etiqueta con ese nombre.",
    "UK_TAGS_URL": "Ya existe una etiqueta con esa URL.",
    "UK_CATEGORIES_NAME": "Ya existe una categoria con ese nombre.",
    "UK_CATEGORIES_URL": "Ya existe una categoria con esa URL.",
}

CHECK_CONSTRAINT_MESSAGES = {
    "CK_BLOG_USERS_EMAIL":
        "El correo no tiene un formato valido (ejemplo: ana@correo.com).",
    "CK_ARTICLES_STATUS":
        "El estado debe ser borrador, publicado o archivado.",
}


class AppError(Exception):
    """A failure worth showing to the user as a flash message.

    Raised both by Oracle translation and by request parsing, so controllers
    only ever deal with one exception type.
    """

    def __init__(self, message: str, code: int | None = None):
        super().__init__(message)
        self.message = message
        self.code = code


def translate(error: oracledb.DatabaseError) -> AppError:
    """Map an oracledb error onto an AppError carrying a readable message."""
    info = error.args[0] if error.args else None
    code = getattr(info, "code", None)
    raw = getattr(info, "message", str(error)).strip()

    # Drop the PL/SQL call stack (ORA-06512 lines) and keep the real cause.
    first_line = raw.splitlines()[0] if raw else ""
    if not first_line:
        return AppError("Error de base de datos.", code)

    if first_line.startswith(BUSINESS_ERROR_PREFIX) and ": " in first_line:
        return AppError(first_line.split(": ", 1)[1], code)

    return AppError(_constraint_message(code, first_line), code)


def _constraint_message(code: int | None, text: str) -> str:
    """Replace a constraint name with a sentence about what went wrong."""
    upper = text.upper()

    if code == 1:  # ORA-00001: unique constraint violated
        return _lookup(UNIQUE_CONSTRAINT_MESSAGES, upper, "El registro ya existe.")
    if code == 2290:  # ORA-02290: check constraint violated
        return _lookup(CHECK_CONSTRAINT_MESSAGES, upper,
                       "Un dato no cumple las reglas de la tabla.")
    if code == 2291:  # ORA-02291: parent key not found
        return "El registro relacionado no existe."
    if code == 12899:  # ORA-12899: value too large for column
        return "Un texto es mas largo de lo que permite la columna."
    return text


def _lookup(messages: dict[str, str], haystack: str, fallback: str) -> str:
    for constraint, message in messages.items():
        if constraint in haystack:
            return message
    return fallback
