import typing
import openai
import json
from pydantic import BaseModel
import time

from .model import Content, SentimentSummary

client = openai.OpenAI()


class SentimentResponse(BaseModel):
    justifications_of_sentiment:typing.List[str]
    sentiment: typing.Literal["negative", "positive", "neutral"]
    names_of_contributors_that_cause_sentiment: typing.List[str]
    how_contributors_cause_sentiment:str
    how_contributors_cause_sentiment_lemma:str
    how_tense: typing.Literal["past", "present", "future"]
    topic:str
    topic_lemma:str
    #stated_as_fact: bool
    #stated_by: typing.Literal["author"] | str
    lat_lng_of_topic_location:str | None # or null if not stated,
    datetime_of_topic:str | None # or null if not stated,


def process(
    content: Content,
    model: str = "gpt-3.5-turbo",
    max_tokens=4096,
    temperature=0,
) -> typing.Optional[SentimentSummary]:
    
    prompt_strategy = "v1"

    # TODO address prompt injection attack vector
    prompt = f"""
    {content.body}
    """

    # Make an API request to OpenAI's language model
    start = time.time()
    messages = [
        {"role": "system", "content": "Summarize the sentiment expressed in the user content. Reason about the entity that caused the sentiment, how the entity caused the sentiment, the topic affected by the sentiment, and the contextual details. Extract the content as JSON."},
        {"role": "user", "content": prompt},
    ]
    completion = client.beta.chat.completions.parse(
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
        messages=messages,
        response_format=SentimentResponse,
    )
    duration = time.time() - start

    try:
        sr = completion.choices[0].message.parsed

        #response_text = response.choices[0].text.strip()
        #response_json = json.loads(response_text)  # Parse the response as JSON
        print("Valid JSON received:")
        print(json.dumps(sr.dict(), indent=4))  # Print formatted JSON
        messages.append(completion.choices[0].message.dict())
        return SentimentSummary(
            content_hash=content.content_hash,
            model_id=model,
            prompt_strategy=prompt_strategy,
            sentiment=True if sr.sentiment == 'positive' else (False if sr.sentiment == 'negative' else None),
            justifications=sr.justifications_of_sentiment,
            topic=sr.topic,
            topic_lemma=sr.topic_lemma,
            location=sr.lat_lng_of_topic_location,
            content_datetime=sr.datetime_of_topic,
            method=sr.how_contributors_cause_sentiment,
            method_lemma=sr.how_contributors_cause_sentiment_lemma,
            contributors=sr.names_of_contributors_that_cause_sentiment,
            discussion_duration=duration,
            log=messages,
            topic_values=None,
            contributors_values=None,
            method_values=None,
        )
    except json.JSONDecodeError:
        print("The response was not valid JSON. Here is the raw output:")
        print(response_text)
        return None
