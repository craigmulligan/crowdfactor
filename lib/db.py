import time
import sqlite3
from flask import g


class DB:
    def __init__(self, filename) -> None:
        self.conn = sqlite3.connect(filename)
        self.conn.row_factory = self.make_dicts

    @staticmethod
    def make_dicts(cursor, row):
        return dict(
            (cursor.description[idx][0], value) for idx, value in enumerate(row)
        )

    @staticmethod
    def get_db(filename):
        """
        only used in flask.
        """
        db = getattr(g, "_database", None)
        if db is None:
            db = g._database = DB(filename)
        return db

    @staticmethod
    def tear_down(_):
        db = getattr(g, "_database", None)
        if db is not None:
            db.conn.close()

    def setup(self):
        """
        initializes schema
        """
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS crowd_log (timestamp INTEGER PRIMARY KEY, crowd_count INTEGER, surf_rating TEXT);
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

    def insert(self, crowd_count: int, surf_rating: str):
        timestamp = int(time.time())

        self.conn.execute(
            """
            insert into crowd_log (timestamp, crowd_count, surf_rating) values (?, ?, ?)
        """,
            (
                timestamp,
                crowd_count,
                surf_rating,
            ),
        )

        self.conn.commit()

    def query(self, query, one=False):
        cur = self.conn.execute(query)
        rv = cur.fetchall()
        cur.close()
        return (rv[0] if rv else None) if one else rv
