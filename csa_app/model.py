import typing
import dataclasses
import hashlib
import json


def convert_to_id(wse_str):
    id = hashlib.sha256(wse_str.encode("utf-8")).hexdigest()
    return id


def create_content_id(raw_details: dict):
    return convert_to_id(json.dumps(raw_details, sort_keys=True))


@dataclasses.dataclass
class Content:
    content_hash: str
    body: str
    author: str
    forum: str
    raw_details: dict
    written_date_time: str


@dataclasses.dataclass
class SentimentSummary:
    content_hash: str
    model_id: str
    prompt_strategy: str

    log: typing.List
    discussion_duration: float

    sentiment: typing.Optional[bool]
    justifications: typing.List[str]

    location: typing.Optional[str]
    content_datetime: typing.Optional[str]

    topic: str
    topic_lemma: typing.Optional[str]
    topic_values: typing.Optional[typing.List[str]]

    contributors: typing.List[str]
    contributors_values: typing.Optional[str]

    method: str
    method_lemma: typing.Optional[str]
    method_values: typing.Optional[typing.List[str]]
