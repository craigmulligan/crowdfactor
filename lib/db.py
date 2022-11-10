from typing import Optional, Union, Any, List
from lib.graph import CrowdCount, CrowdPrediction
from datetime import datetime
import sqlite3
from flask import g, current_app
from lib.utils import DATETIME_FORMAT


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
        Get db from app context
        else create a new connection.
        """
        db_url = current_app.config.get("DB_URL")

        db = getattr(g, "_database", None)
        if db is None:
            db = g._database = DB(db_url)
        return db

    @staticmethod
    def tear_down(_):
        """
        When app context is torn down
        close the db connection.
        """
        db = getattr(g, "_database", None)
        if db is not None:
            db.conn.close()

    def setup(self):
        """
        initializes schema
        """
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS crowd_log (timestamp TEXT PRIMARY KEY, crowd_count INTEGER, surf_rating TEXT, spot_id TEXT, model_version INTEGER);
        """
        )

        self.conn.execute(
            """
            CREATE INDEX IF NOT EXISTS crowd_log_crowd_count_idx ON crowd_log(crowd_count);
        """
        )

        self.conn.execute(
            """
            CREATE INDEX IF NOT EXISTS crowd_log_spot_id_idx ON crowd_log(spot_id);
        """
        )

        self.conn.execute(
            """
            CREATE INDEX IF NOT EXISTS crowd_log_surf_rating_idx ON crowd_log(surf_rating);
        """
        )

    def insert(
        self,
        crowd_count: int,
        surf_rating: str,
        spot_id: str,
        dt: str,
        model_version: int,
    ):
        self.conn.execute(
            """
            insert into crowd_log (timestamp, crowd_count, surf_rating, spot_id, model_version) values (?, ?, ?, ?, ?)
            """,
            (dt, crowd_count, surf_rating, spot_id, model_version),
        )

        self.conn.commit()

    def latest_reading(self, spot_id):
        return self.query(
            """
                select surf_rating, crowd_count, timestamp from crowd_log where spot_id = ? order by timestamp desc limit 1;
            """,
            [spot_id],
            one=True,
        )

    def predictions(
        self, spot_id: str, start: datetime, end: datetime
    ) -> List[CrowdPrediction]:
        """
        Get average of reading per hour for weekday, grouped by surf rating.
        """
        # NB isoweekday is needed not .weekday()
        # This is because sqlite3 uses sunday as 0.
        window_start = f"{start.isoweekday()}-{start.hour:02}"
        window_end = f"{end.isoweekday()}-{end.hour:02}"
        past = start.strftime(DATETIME_FORMAT)

        return self.query(
            f"""
                select 
                    avg(crowd_count) as avg_crowd_count, 
                    strftime('%H', timestamp) as hour, 
                    surf_rating, 
                    strftime('%w-%H', timestamp) as weekday
                from crowd_log
                where spot_id = ? 
                and timestamp < ?
                and strftime('%w-%H', timestamp) BETWEEN ? AND ? 
                group by strftime('%H', timestamp), surf_rating;
            """,
            [spot_id, past, window_start, window_end],
        )  # type:ignore

    def readings(
        self, spot_id: str, start: datetime, end: datetime
    ) -> List[CrowdCount]:
        """
        Get average of reading per hour for today.
        """
        return self.query(
            f"""
                SELECT avg(crowd_count) AS avg_crowd_count, strftime('%H', timestamp) AS hour 
                FROM crowd_log 
                where timestamp BETWEEN ? AND ?
                AND spot_id = ?
                GROUP BY strftime('%H', timestamp), surf_rating;
            """,
            [start.strftime(DATETIME_FORMAT), end.strftime(DATETIME_FORMAT), spot_id],
        )  # type:ignore

    def query(self, query, query_args=(), one=False) -> Union[Optional[Any], Any]:
        cur = self.conn.execute(query, query_args)
        rv = cur.fetchall()
        cur.close()
        return (rv[0] if rv else None) if one else rv
