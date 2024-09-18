import typing
import openai
import json

from .model import Content, SentimentSummary

client = openai.OpenAI()


def process(
    content: Content,
    model: str = "gpt-3.5-turbo-1106",
    max_tokens=10000,
    temperature=0,
) -> typing.Optional[SentimentSummary]:

    # TODO address prompt injection attack vector
    prompt = f"""
    Consider the following text.
     
    {content.body}

    Summarize this text, identify the feeling trying to be made. Return the summarization as a JSON object with the following schema for the feeling in the text:

    {{
        "topic":str,
        "topic_common_noun_type":str,
        "negative":bool,
        "cause": name of person or natural cause source or null if not applicable,
        "cause_method_verb_lemma":str,
        "when": either "past" "present" or "future",
        "stated_as_fact": bool,
        "stated_by": "author" or name of person making the statement
        "lat_lng_of_topic_location":str or null if not stated,
        "datetime_of_topic":str or null if not stated,
    }}

    """

    # Make an API request to OpenAI's language model

    response = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model=model,
        response_format={"type": "json_object"},
    )

    try:
        p = response.parse()
        response_text = response.choices[0].text.strip()
        response_json = json.loads(response_text)  # Parse the response as JSON
        print("Valid JSON received:")
        print(json.dumps(response_json, indent=4))  # Print formatted JSON

        # return SentimentSummary(
        #    content_hash=content.content_hash,
        # )
        return None
    except json.JSONDecodeError:
        print("The response was not valid JSON. Here is the raw output:")
        print(response_text)
        return None
