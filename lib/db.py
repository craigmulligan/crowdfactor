import time
import sqlite3


class DB:
    def __init__(self, filename) -> None:
        self.conn = sqlite3.connect(filename)

    def setup(self):
        """
        initializes tables
        """
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS crowd_log (timestamp INTEGER PRIMARY KEY, crowd_count INTEGER, surf_rating INTEGER);
        """
        )

        self.conn.execute(
            """
            CREATE INDEX IF NOT EXISTS crowd_log_crowd_count_idx ON crowd_log(crowd_count);
        """
        )

        self.conn.execute(
            """
            CREATE INDEX IF NOT EXISTS crowd_log_surf_rating_idx ON crowd_log(surf_rating);
        """
        )

    def insert(self, crowd_count: int, surf_rating: int):
        timestamp = int(time.time())

        self.conn.execute(
            """
            insert into crowd_count (timestamp, crowd_count, surf_rating) values (?, ?, ?),
        """,
            (
                timestamp,
                crowd_count,
                surf_rating,
            ),
        )

        self.conn.commit()
