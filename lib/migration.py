import logging
import glob, os
from pathlib import Path
import sqlite3

for file in glob.glob("*.txt"):
    print(file)


def up(migration_dir, connection):
    cursor = connection.cursor()
    [current_version] = cursor.execute(
    """
        PRAGMA user_version;
    """
    ).fetchone()

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
                connection.execute(f.read())


if __name__ == "__main__":
    con = sqlite3.connect(":memory:")
    up("migrations", con)
