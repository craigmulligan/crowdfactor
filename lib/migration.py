import logging
import glob, os
from pathlib import Path
import sqlite3


def up(migration_dir: str, connection: sqlite3.Connection):
    if not os.path.exists(migration_dir):
        raise FileNotFoundError(f"{migration_dir} does not exist")

    row_factory = None

    if connection.row_factory:
        row_factory = connection.row_factory
        connection.row_factory = None

    cursor = connection.cursor()
    [current_version] = cursor.execute(
        """
        PRAGMA user_version;
    """
    ).fetchone()

    current_version = int(current_version)

    for filename in sorted(glob.glob(os.path.join(migration_dir, "*.sql"))):
        p = Path(filename)
        v = int(p.stem)

        """
        PRAGMA user_version;
        """
        if v <= current_version:
            logging.info(f"version: {v} applied")
        else:
            logging.info(f"applying version: {v}")
            with open(filename) as f:
                try:
                    # We add a begin because.
                    # Execute the SQL statements in sql_script. If there is a pending transaction, an implicit COMMIT statement is executed first.
                    # No other implicit transaction control is performed; any transaction control must be added to sql_script.
                    cursor.executescript("BEGIN;\n" + f.read())
                    cursor.execute(f"PRAGMA user_version = {v}")
                except:
                    cursor.execute("ROLLBACK")
                    raise

    # Add back any row factory.
    connection.row_factory = row_factory
