"""The only place that talks to PL/SQL packages.

Repositories call these four helpers and nothing else, which is what keeps
the promise that the application never writes SQL.

Query procedures return a SYS_REFCURSOR as their last parameter: a cursor is
created with ``connection.cursor()`` and passed along, which is the documented
way of receiving a reference cursor in python-oracledb.

The packages never COMMIT. Python owns the transaction, so a request that
fails halfway leaves no partial data behind.
"""
from typing import Any, Sequence

import oracledb

from app.core.database import get_connection
from app.core.exceptions import translate

Row = dict[str, Any]


def fetch_all(procedure: str, params: Sequence[Any] = ()) -> list[Row]:
    """Call a procedure returning SYS_REFCURSOR and read every row."""
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            out_cursor = connection.cursor()
            cursor.callproc(procedure, list(params) + [out_cursor])
            with out_cursor:
                return _to_dicts(out_cursor)
    except oracledb.DatabaseError as error:
        raise translate(error) from error


def fetch_one(procedure: str, params: Sequence[Any] = ()) -> Row | None:
    """Same as fetch_all but for procedures that return at most one row."""
    rows = fetch_all(procedure, params)
    return rows[0] if rows else None


def call_procedure(procedure: str, params: Sequence[Any] = ()) -> None:
    """Run a writing procedure and commit, or roll back and raise AppError."""
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.callproc(procedure, list(params))
        connection.commit()
    except oracledb.DatabaseError as error:
        connection.rollback()
        raise translate(error) from error


def call_function(function: str, params: Sequence[Any] = (),
                  return_type: Any = oracledb.NUMBER,
                  commit: bool = True) -> Any:
    """Run a stored function and return its result.

    The create_* functions insert and return the generated id, so committing
    is the default. Read-only functions pass commit=False.
    """
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            result = cursor.callfunc(function, return_type, list(params))
        if commit:
            connection.commit()
        return result
    except oracledb.DatabaseError as error:
        connection.rollback()
        raise translate(error) from error


def _to_dicts(cursor: oracledb.Cursor) -> list[Row]:
    """Turn an open cursor into dicts keyed by lowercased column names."""
    columns = [column[0].lower() for column in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]
