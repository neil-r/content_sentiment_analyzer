import openai
import dotenv
import functools
import os

import csa_app.ai_processor_openai
from csa_app.database import DatabaseSqlLite

# Configuration

# Load environment variables from local ".env" file
dotenv.load_dotenv()

db_file_path = "data.db"
batch_size = 10
max_number_of_batches = 1
processor = functools.partial(
    csa_app.ai_processor_openai.process, model="gpt-3.5-turbo-1106"
)
api_key = os.getenv("OPENAI_API_KEY")
openai.api_key = api_key


if __name__ == "__main__":
    database = DatabaseSqlLite(db_file_path=db_file_path)

    for i in range(max_number_of_batches):
        content_batch = database.get_unanalyzed_content(batch_size)
        if len(content_batch) == 0:
            print("Finished end of content to process, exiting.")
            break
        summaries = []
        for content in content_batch:
            summary = processor(content)
            if summary is not None:
                summaries.append(content)
            else:
                print(
                    f"Odd, this content was skipped given processor did not like it: {content}"
                )

        database.add_summaries(summaries)
