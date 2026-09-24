"""Install the schema and optionally fill it with demo content.

  1. blog_database.sql  tables, sequences and the blog_pkg CRUD package
  2. blog_extras.sql    the blog_web_pkg query package
  3. seed               demo rows, inserted through the stored programs

Usage:
    .venv\\Scripts\\python.exe -m scripts.setup_db              everything
    .venv\\Scripts\\python.exe -m scripts.setup_db --schema-only steps 1 and 2
    .venv\\Scripts\\python.exe -m scripts.setup_db --seed-only   step 3
"""
import sys

import oracledb
from flask import g

from app import create_app
from app.core.database import CONNECTION_KEY, connect
from scripts import seed
from scripts.sql_runner import report_compilation_errors, run_script

SCHEMA_SCRIPTS = ("blog_database.sql", "blog_extras.sql")
PACKAGES = ("BLOG_PKG", "BLOG_WEB_PKG")


def main() -> None:
    schema_only = "--schema-only" in sys.argv
    seed_only = "--seed-only" in sys.argv

    app = create_app()
    target = app.config["APP_CONFIG"].db_target
    print(f"Connecting to {target} ...")

    # The seeding step runs through the normal service layer, which expects a
    # Flask app context, so the whole script borrows one and lends it the
    # connection that would otherwise be opened per request.
    with app.app_context():
        try:
            connection = connect()
        except oracledb.DatabaseError as error:
            print(f"Could not connect: {str(error).splitlines()[0]}")
            print("Check that the Oracle XE container is running.")
            sys.exit(1)

        setattr(g, CONNECTION_KEY, connection)
        print("Connected.")

        # The connection is not closed by hand: leaving the app context tears
        # it down, rolling back first if we are on our way out with an error.
        if not seed_only:
            for script in SCHEMA_SCRIPTS:
                if run_script(connection, script):
                    print(f"\n{script} had failures; stopping.")
                    sys.exit(1)
            if not report_compilation_errors(connection, PACKAGES):
                sys.exit(1)

        if not schema_only:
            seed.run()

    print("\nDone. Now run:  .venv\\Scripts\\python.exe main.py")


if __name__ == "__main__":
    main()
