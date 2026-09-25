"""Running a .sql script through python-oracledb.

The driver executes one statement per call and knows nothing about SQL*Plus
conventions, so the file has to be split first: a lone "/" closes a PL/SQL
block (where ";" is part of the code), and outside those blocks every
statement ends with ";".
"""
import os

import oracledb

# Understood by SQL*Plus but not by the server. blog_database.sql opens with
# SET SERVEROUTPUT ON, which would come back as ORA-00922 if sent along.
SQLPLUS_COMMANDS = ("SET ", "SHOW ", "SPOOL", "PROMPT", "EXIT", "QUIT",
                    "WHENEVER ", "CONNECT ")

# Statements that open a PL/SQL block, where ";" does not end the statement.
PLSQL_OBJECTS = ("PACKAGE", "PROCEDURE", "FUNCTION", "TRIGGER", "TYPE")


def split_statements(script: str, base_dir: str = ".") -> list[str]:
    """Split a script into statements Oracle can accept one at a time.

    A line starting with "@" is a SQL*Plus include (blog_database.sql uses it
    to pull in create_tables.sql); the server has no equivalent, so it is
    resolved here by splicing in that file's own statements.
    """
    statements: list[str] = []
    buffer: list[str] = []

    for line in script.splitlines():
        if line.strip() == "/":
            block = "\n".join(buffer).strip()
            if block:
                statements.append(block)
            buffer = []
            continue

        if line.strip().startswith("@"):
            # Comments queued ahead of the include (e.g. a section banner)
            # describe the include itself, not a statement of their own, so
            # they are dropped rather than sent to the server on their own.
            if not _is_blank_or_comment_only(buffer):
                pending = "\n".join(buffer).strip()
                if pending:
                    statements.append(pending)
            buffer = []

            included_path = os.path.join(base_dir, line.strip()[1:].strip())
            with open(included_path, encoding="utf-8") as handle:
                statements.extend(split_statements(handle.read(), base_dir))
            continue

        buffer.append(line)

        if line.rstrip().endswith(";") and not _opens_plsql_block(buffer):
            statement = "\n".join(buffer).strip().rstrip(";").strip()
            if statement:
                statements.append(statement)
            buffer = []

    remainder = "\n".join(buffer).strip()
    if remainder:
        statements.append(remainder)
    return statements


def _is_blank_or_comment_only(lines: list[str]) -> bool:
    """Whether the buffered lines are nothing but comments and blank lines."""
    for line in lines:
        text = line.strip()
        if not text or text.startswith("--"):
            continue
        return False
    return True


def _opens_plsql_block(lines: list[str]) -> bool:
    """Whether the buffered lines started a PL/SQL block that is still open."""
    for line in lines:
        text = line.strip().upper()
        if not text or text.startswith("--"):
            continue
        if text.startswith(("DECLARE", "BEGIN")):
            return True
        if text.startswith("CREATE"):
            return any(keyword in text for keyword in PLSQL_OBJECTS)
        return False
    return False


def _is_sqlplus_command(statement: str) -> bool:
    """Whether the statement is a SQL*Plus directive that must be skipped.

    Only the first meaningful line is inspected. Inside a PL/SQL block that
    line is always DECLARE, BEGIN or CREATE, so the SET of an UPDATE is never
    mistaken for the SET of SQL*Plus.
    """
    for line in statement.splitlines():
        text = line.strip()
        if not text or text.startswith("--"):
            continue
        return text.upper().startswith(SQLPLUS_COMMANDS)
    return False


def run_script(connection: oracledb.Connection, path: str) -> int:
    """Execute a .sql file statement by statement, reporting progress.

    Returns how many statements failed, so the caller can stop before
    loading data into a half built schema.
    """
    with open(path, encoding="utf-8") as handle:
        statements = split_statements(handle.read(), os.path.dirname(path) or ".")

    print(f"\n{path}: {len(statements)} statement(s)")
    failures = 0

    with connection.cursor() as cursor:
        for number, statement in enumerate(statements, 1):
            label = " ".join(statement.split()[:4])
            if _is_sqlplus_command(statement):
                print(f"  [{number:>2}] skip  {label}  (SQL*Plus directive)")
                continue
            try:
                cursor.execute(statement)
                print(f"  [{number:>2}] ok    {label}")
            except oracledb.DatabaseError as error:
                failures += 1
                print(f"  [{number:>2}] ERROR {label}  ->  "
                      f"{str(error).splitlines()[0]}")

    connection.commit()
    if failures:
        print(f"  {failures} statement(s) failed.")
    return failures


def report_compilation_errors(connection: oracledb.Connection,
                              names: tuple[str, ...]) -> bool:
    """Check that the packages compiled, since CREATE PACKAGE can fail quietly.

    A package may end up "created with compilation errors" without raising,
    and then the application breaks later with no obvious cause.
    """
    placeholders = ", ".join(f":{index}" for index in range(len(names)))
    with connection.cursor() as cursor:
        cursor.execute(
            f"SELECT name, type, line, text FROM user_errors "
            f"WHERE name IN ({placeholders}) ORDER BY name, sequence",
            list(names))
        errors = cursor.fetchall()

    if not errors:
        print("\nAll packages compiled without errors.")
        return True

    print("\nCompilation errors:")
    for name, kind, line, text in errors:
        print(f"  {name} ({kind}) line {line}: {text.strip()}")
    return False
