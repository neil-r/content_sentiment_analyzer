import sqlite3
import typing
import json
import pandas as pd
import datetime

from .model import SentimentSummary, Content


class DatabaseSqlLite:

    def __init__(self, db_file_path="data.db"):
        self.db_file_path = db_file_path

        with sqlite3.connect(self.db_file_path) as c:
            cur = c.cursor()

            cur.execute(
                """CREATE TABLE IF NOT EXISTS content (
                content_hash TEXT NOT NULL,
                body TEXT NOT NULL,
                author TEXT NOT NULL,
                forum TEXT NOT NULL,
                raw_details TEXT NOT NULL,
                written_date_time TEXT NOT NULL,
                region TEXT NOT NULL,
                PRIMARY KEY (content_hash));
            """
            )

            cur.execute(
                """CREATE TABLE IF NOT EXISTS sentiment_summaries (
                content_hash TEXT NOT NULL,
                model_id TEXT NOT NULL,
                prompt_strategy TEXT NOT NULL,
                sentiment INTEGER NULL,
                log TEXT NOT NULL,
                justifications TEXT NOT NULL,
                discussion_duration REAL NOT NULL,
                location TEXT NULL,
                content_datetime TEXT NULL,
                contributors TEXT NOT NULL,
                contributors_values TEXT NULL,
                method TEXT NOT NULL,
                method_lemma_id TEXT NULL,
                method_values TEXT NULL,
                topic TEXT NULL,
                topic_lemma_id TEXT NULL,
                topic_values TEXT NULL,
                PRIMARY KEY (content_hash, model_id, prompt_strategy));
            """
            )

            c.commit()

    def get_unanalyzed_content(self, number: int = 100) -> typing.List[Content]:
        with sqlite3.connect(self.db_file_path) as c:
            results = c.execute(
                "SELECT * FROM content c LEFT JOIN sentiment_summaries s ON c.content_hash = s.content_hash WHERE s.content_hash IS NULL LIMIT 0, ?",
                (number,),
            ).fetchall()

            if results is not None:
                return list(
                    Content(
                        o[0],
                        o[1],
                        o[2],
                        o[3],
                        json.loads(o[4]),
                        o[5],
                        o[6],
                    )
                    for o in results
                )
            else:
                return None

    def add_content(self, lst_content: typing.List[Content]):
        with sqlite3.connect(self.db_file_path) as c:
            cur = c.cursor()

            # Convert list of dataclass instances to list of tuples
            data_to_insert = [
                (
                    c.content_hash,
                    c.body,
                    c.author,
                    c.forum,
                    json.dumps(c.raw_details),
                    c.written_date_time,
                    c.region,
                )
                for c in lst_content
            ]

            cur.executemany(
                "INSERT INTO content VALUES (?,?,?,?,?,?,?);",
                data_to_insert,
            )

            c.commit()

    def add_summaries(self, lst_summaries: typing.List[SentimentSummary]):
        with sqlite3.connect(self.db_file_path) as c:
            cur = c.cursor()

            # Convert list of dataclass instances to list of tuples
            data_to_insert = [
                (
                    s.content_hash,
                    s.model_id,
                    s.prompt_strategy,
                    (1 if s.sentiment else 0 if s.sentiment is not None else None),
                    json.dumps(s.log),
                    json.dumps(s.justifications),
                    s.discussion_duration,
                    s.location,
                    s.content_datetime,
                    json.dumps(s.contributors),
                    (
                        " ".join(st + "!" for st in s.contributors_values)
                        if s.contributors_values is not None
                        else None
                    ),
                    s.method,
                    s.method_lemma,
                    (
                        " ".join(st + "!" for st in s.method_values)
                        if s.method_values is not None
                        else None
                    ),
                    s.topic,
                    s.topic_lemma,
                    (
                        " ".join(st + "!" for st in s.topic_values)
                        if s.topic_values is not None
                        else None
                    ),
                )
                for s in lst_summaries
            ]

            cur.executemany(
                "INSERT INTO sentiment_summaries VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?);",
                data_to_insert,
            )

            c.commit()

    def lookup_sentiment_summaries(
        self,
        topic_id: typing.Optional[str] = None,
        method_id: typing.Optional[str] = None,
        contributor_id: typing.Optional[str] = None,
        sentiment: typing.Optional[bool] = None,
        start_content_datetime: typing.Optional[datetime.datetime] = None,
        end_content_datetime: typing.Optional[datetime.datetime] = None,
        return_limit: typing.Optional[int] = None,
    ) -> pd.DataFrame:
        with sqlite3.connect(self.db_file_path) as c:
            base_query = """SELECT 
                c.content_hash AS content_hash, 
                s.sentiment AS sentiment,
                s.method_lemma_id AS method,
                s.topic_lemma_id AS topic,
                c.written_date_time AS content_datetime,
                s.contributors as contributors,
                c.region as region
              FROM sentiment_summaries s INNER JOIN content c ON c.content_hash = s.content_hash
            """
            where_clauses = []
            params = []

            if topic_id is not None:
                where_clauses.append("s.topic_values LIKE ?")
                params.append(f"{topic_id}!")

            if method_id is not None:
                where_clauses.append("s.method_values LIKE ?")
                params.append(f"{method_id}!")

            if contributor_id is not None:
                where_clauses.append("s.contributors_values LIKE ?")
                params.append(f"{contributor_id}!")

            if sentiment is not None:
                where_clauses.append("s.sentiment = ?")
                params.append(f"{1 if sentiment else 0}!")

            where_clause = ""
            if len(where_clauses) > 0:
                where_clause = " WHERE " + " AND ".join(where_clauses)

            limit_clause = ""
            if return_limit is not None:
                limit_clause = " LIMIT 0,?"
                params.append(return_limit)
            df = pd.read_sql_query(
                base_query + where_clause + limit_clause, c, params=params
            )
            return df
