from typing import Optional, Union, Any, List
from lib.graph import CrowdCount
from datetime import datetime
import sqlite3
from flask import g, current_app
from lib.utils import DATETIME_FORMAT
import logging


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
        user_version = self.query(
            """
            PRAGMA user_version;
        """,
            one=True,
        )

        if user_version is None:
            raise Exception("no user_version is unexpected")

        version = user_version["user_version"]
        latest_version = 4

        while True:
            logging.info(f"DB schema version:{version}")
            if version == 0:
                self.query(
                    """
                    CREATE TABLE IF NOT EXISTS crowd_log (timestamp TEXT PRIMARY KEY, crowd_count INTEGER, surf_rating TEXT, spot_id TEXT, model_version INTEGER);
                """
                )

                self.query(
                    """
                    CREATE INDEX IF NOT EXISTS crowd_log_crowd_count_idx ON crowd_log(crowd_count);
                """
                )

                self.query(
                    """
                    CREATE INDEX IF NOT EXISTS crowd_log_spot_id_idx ON crowd_log(spot_id);
                """
                )

                self.query(
                    """
                    CREATE INDEX IF NOT EXISTS crowd_log_surf_rating_idx ON crowd_log(surf_rating);
                """
                )
                version += 1
                self.query(f"PRAGMA user_version = {version}")
                continue
            elif version == 1:
                colums = [
                    ("wave_height_min", "REAL"),
                    ("wave_height_max", "REAL"),
                    ("weather_temp", "REAL"),
                    ("weather_condition", "TEXT"),
                    ("water_temp_max", "REAL"),
                    ("water_temp_min", "REAL"),
                    ("wind_direction", "REAL"),
                    ("wind_gust", "REAL"),
                    ("wind_speed", "REAL"),
                ]

                for column in colums:
                    self.query(
                        f"""
                        ALTER TABLE crowd_log 
                          ADD {column[0]} {column[1]};
                    """
                    )
                version += 1
                self.query(f"PRAGMA user_version = {version}")
                continue
            if version == 2:
                # create a table to hold the last training job.
                self.query(
                    """
                    CREATE TABLE IF NOT EXISTS training_log (timestamp TEXT, score REAL, name TEXT);
                """
                )
                self.query(
                    """
                    CREATE INDEX IF NOT EXISTS training_log_timestamp_idx ON training_log(timestamp);
                """
                )
                self.query(
                    """
                    CREATE INDEX IF NOT EXISTS training_log_name_idx ON training_log(name);
                """
                )

                version += 1
                self.query(f"PRAGMA user_version = {version}")
                continue
            if version == 3:
                self.query("CREATE TABLE IF NOT EXISTS dbm (key TEXT PRIMARY KEY, value TEXT, timestamp TEXT);")
                logging.info("created dbm")
                version += 1
                self.query(f"PRAGMA user_version = {version};")
                continue
            if version == latest_version:
                logging.info("DB schema up to date.")
                break

            self.commit()

    def insert(
        self,
        crowd_count: int,
        conditions,
        spot_id: str,
        dt: str,
        model_version: int,
    ):
        row = self.query(
            """
            insert into crowd_log (
                timestamp, 
                crowd_count, 
                spot_id, 
                model_version,
                surf_rating,
                wind_speed,
                wind_gust,
                wind_direction,
                water_temp_max,
                water_temp_min,
                weather_temp,
                weather_condition,
                wave_height_min,
                wave_height_max
            ) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) returning *
            """,
            (
                dt,
                crowd_count,
                spot_id,
                model_version,
                conditions.surf_rating,
                conditions.wind_speed,
                conditions.wind_gust,
                conditions.wind_direction,
                conditions.water_temp_max,
                conditions.water_temp_min,
                conditions.weather_temp,
                conditions.weather_condition,
                conditions.wave_height_min,
                conditions.wave_height_max,
            ),
            one=True
        )
        self.commit()
        return row


    def latest_reading(self, spot_id):
        return self.query(
            """
                select surf_rating, crowd_count, timestamp from crowd_log where spot_id = ? order by timestamp desc limit 1;
            """,
            [spot_id],
            one=True,
        )

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

    def logs(self, spot_id, since: Optional[str] = None):
        if since is None: 
            since = "1970-01-01 00:00:00"

        return self.query(
            """
                select *, cast(strftime('%w', timestamp) as INTEGER) as weekday, cast(strftime("%H") as INTEGER) as hour from crowd_log where spot_id = ? and timestamp > ? and wind_speed is not NULL order by timestamp desc;
            """,
            [spot_id, since],
        )

    def latest_training_log(self, name):
        return self.query("select * from training_log where name = ? order by timestamp desc limit 1", [name], one=True)

    def insert_training_log(self, timestamp: datetime, score: float, name):
        self.query("insert into training_log (timestamp, score, name) values (?, ?, ?)", [timestamp.strftime(DATETIME_FORMAT), score, name])
        self.commit()

    def insert_cache(self, key: str, value: str):
        now = datetime.utcnow()
        self.query("insert into dbm(timestamp, key, value) values (?, ?, ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value, timestamp=excluded.timestamp", [now.strftime(DATETIME_FORMAT), key, value])
        self.commit()

    def get_cache(self, key):
        return self.query("select value from dbm where key = ?", [key], one=True)

    def query(self, query, query_args=(), one=False) -> Union[Optional[Any], Any]:
        cur = self.conn.execute(query, query_args)
        rv = cur.fetchall()
        cur.close()
        return (rv[0] if rv else None) if one else rv

    def commit(self):
        self.conn.commit()
