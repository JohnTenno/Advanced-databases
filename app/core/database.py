"""Oracle connection lifecycle, one connection per request.

python-oracledb runs in thin mode, so no Oracle client install is needed.
Flask serves one request at a time per thread and keeps per-request state in
``g``, so every call made while rendering a page shares a connection and
therefore a single transaction.
"""
import oracledb
from flask import Flask, current_app, g

CONNECTION_KEY = "oracle_connection"

# CLOB columns (articles.body_text) arrive as plain str instead of LOB
# objects that would need an explicit .read() on every field.
oracledb.defaults.fetch_lobs = False


def connect() -> oracledb.Connection:
    """Open a standalone connection using the configured credentials."""
    config = current_app.config["APP_CONFIG"]
    return oracledb.connect(
        user=config.db_user, password=config.db_password, dsn=config.db_dsn)


def get_connection() -> oracledb.Connection:
    """Return this request's connection, opening it on first use."""
    if CONNECTION_KEY not in g:
        g.oracle_connection = connect()
    return g.oracle_connection


def close_connection(error: BaseException | None = None) -> None:
    """Close the request connection, rolling back if the request blew up."""
    connection = g.pop(CONNECTION_KEY, None)
    if connection is None:
        return
    try:
        if error is not None:
            connection.rollback()
    finally:
        connection.close()


def register(app: Flask) -> None:
    """Hook connection cleanup into the application lifecycle."""
    app.teardown_appcontext(close_connection)
