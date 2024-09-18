import sqlite3
import typing
import json

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
                )
                for c in lst_content
            ]

            cur.executemany(
                "INSERT INTO content VALUES (?,?,?,?,?,?);",
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
                    json.dumps(s.contributors_values),
                    s.method,
                    s.method_lemma,
                    json.dumps(s.method_values),
                    s.topic,
                    s.topic_lemma,
                    json.dumps(s.topic_values),
                )
                for s in lst_summaries
            ]

            cur.executemany(
                "INSERT INTO sentiment_summaries VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?);",
                data_to_insert,
            )

            c.commit()

    def lookup_sentiment_summaries(
        self, evaluation_id
    ) -> typing.List[SentimentSummary]:
        with sqlite3.connect(self.db_file_path) as c:
            results = c.execute(
                "SELECT * FROM sentiment_summaries WHERE evaluation_id = ?",
                (evaluation_id,),
            ).fetchall()

            l = []
            """
            TODO implement
            if results is not None:
                for o in results:
                    l.append(
                        SentimentSummary(
                            o[0],
                            json.loads(o[1]),
                            json.loads(o[2]),
                            o[3],
                            o[4],
                            o[5],
                            o[6],
                            o[7],
                            o[8] == 1,
                        )
                    )
            """
            return l
