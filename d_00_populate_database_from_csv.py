import csv
import json

from csa_app.database import DatabaseSqlLite
import csa_app.model as model


# Configuration

csv_files = ["tests/testdata.csv"]
field_mapping = {
    "body": "content",
    "author": "author",
    "written_date_time": "publish_date",
}
forum = "twitter"
db_file_path = "data.db"
batch_size = 1000


# Helper functions


def process_csv_as_json(csv_file_path, database, field_mapping):
    with open(csv_file_path, mode="r", encoding="utf-8") as csv_file:
        # Initialize the CSV reader
        csv_reader = csv.DictReader(csv_file)

        # Iterate over each row
        batch = []

        for i, row in enumerate(csv_reader):

            try:
                batch.append(
                    model.Content(
                        content_hash=model.create_content_id(row),
                        body=row[field_mapping["body"]],
                        author=row[field_mapping["author"]],
                        forum=forum,
                        raw_details=json.dumps(row),
                        written_date_time=row[field_mapping["written_date_time"]],
                    )
                )

                if (i + 1) % batch_size == 0:
                    database.add_content(batch)
                    batch.clear()
            except Exception as e:
                print(f"Skipping row due to parsing exception: {e}")

        if len(batch) > 0:
            database.add_content(batch)


if __name__ == "__main__":
    database = DatabaseSqlLite(db_file_path=db_file_path)
    for csv_file_path in csv_files:
        process_csv_as_json(csv_file_path, database, field_mapping)
