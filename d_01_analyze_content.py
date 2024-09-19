import openai
import dotenv
import functools
import os

import csa_app.ai_processor_openai
from csa_app.ambiguty_processor import extract_synset_id
from csa_app.database import DatabaseSqlLite
from csa_app.model import SentimentSummary
from csa_app.synset_database import SynsetDatabaseWordNet

# Configuration

# Load environment variables from local ".env" file
dotenv.load_dotenv()

db_file_path = "data.db"
batch_size = 10
max_number_of_batches = 1
processor = functools.partial(
    csa_app.ai_processor_openai.process, model="gpt-4o-mini"
)
ambiguity_clarifier = functools.partial(csa_app.ai_processor_openai.process_multiple_choice_prompt, model="gpt-4o-mini")
api_key = os.getenv("OPENAI_API_KEY")
openai.api_key = api_key


if __name__ == "__main__":
    database = DatabaseSqlLite(db_file_path=db_file_path)
    synset_database = SynsetDatabaseWordNet()

    for i in range(max_number_of_batches):
        content_batch = database.get_unanalyzed_content(batch_size)
        if len(content_batch) == 0:
            print("Finished end of content to process, exiting.")
            break
        summaries = []
        for content in content_batch:
            summary:SentimentSummary = processor(content)

            if summary.topic_values is None and summary.topic_lemma is not None and summary.topic_lemma != "":
                        
                synset_id, duration, msg = extract_synset_id(ambiguity_clarifier, content,summary.topic_lemma, synset_database, consider_verbs=False)
                if synset_id is not None:
                    topic_values = synset_database.get_parent_ids(synset_id)
                    topic_values.append(synset_id)
                    summary.topic_values = topic_values
                    
                summary.discussion_duration += duration
                summary.log.append(msg)

            if summary.method_values is None and summary.method_lemma is not None and summary.method_lemma != "":
                synset_id, duration, msg = extract_synset_id(ambiguity_clarifier, content,summary.method_lemma, synset_database, consider_verbs=True)
                if synset_id is not None:
                    method_values = synset_database.get_parent_ids(synset_id)
                    method_values.append(synset_id)
                    summary.method_values = method_values
                    
                summary.discussion_duration += duration
                summary.log.append(msg)

            if summary is not None:
                summaries.append(summary)
            else:
                print(
                    f"Odd, this content was skipped given processor did not like it: {content}"
                )

        database.add_summaries(summaries)
