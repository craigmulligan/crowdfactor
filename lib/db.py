from typing import Optional, Union, Any
import sqlite3
from flask import g, current_app


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
    def get_db():
        """
        only used in flask.
        """
        db_name = "thelocal.db"
        if current_app.config.get("TESTING"):
            db_name = ":memory:"

        db = getattr(g, "_database", None)
        if db is None:
            db = g._database = DB(db_name)
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
            CREATE TABLE IF NOT EXISTS crowd_log (timestamp TEXT PRIMARY KEY, crowd_count INTEGER, surf_rating TEXT);
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

    def insert(self, crowd_count: int, surf_rating: str, dt: Optional[str] = None):
        if dt is not None:
            self.conn.execute(
                """
                insert into crowd_log (timestamp, crowd_count, surf_rating) values (?, ?, ?)
                """,
                (
                    dt,
                    crowd_count,  # make crowd count equal to hour so it's easy to assert.
                    surf_rating,
                ),
            )
        else:
            self.conn.execute(
                """
                insert into crowd_log (timestamp, crowd_count, surf_rating) values (datetime("now"), ?, ?)
            """,
                (
                    crowd_count,
                    surf_rating,
                ),
            )

        self.conn.commit()

    def latest_reading(self):
        return self.query(
            """
                select surf_rating, crowd_count, strftime('%w-%H', timestamp) as timestamp from crowd_log order by strftime('%s', timestamp) desc limit 1;
            """,
            one=True,
        )

    def query(self, query, query_args=(), one=False) -> Union[Optional[Any], Any]:
        cur = self.conn.execute(query, query_args)
        rv = cur.fetchall()
        cur.close()
        return (rv[0] if rv else None) if one else rv
