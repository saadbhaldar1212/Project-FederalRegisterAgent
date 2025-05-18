import json
import os
from datetime import datetime
from config import global_config as config


def process_raw_file(raw_file_path):
    """Processes a single raw JSON file into a list of dictionaries for DB insertion."""
    processed_documents = []
    try:
        with open(raw_file_path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)

        for doc in raw_data:
            agencies = [
                agency["name"] for agency in doc.get("agencies", []) if "name" in agency
            ]

            publication_date_str = doc.get("publication_date")
            if not publication_date_str:
                print(
                    f"Skipping document {doc.get('document_number')} due to missing publication_date."
                )
                continue
            try:

                datetime.strptime(publication_date_str, "%Y-%m-%d")
            except ValueError:
                print(
                    f"Skipping document {doc.get('document_number')} due to invalid publication_date format: {publication_date_str}"
                )
                continue

            processed_doc = {
                "document_number": doc.get("document_number"),
                "title": doc.get("title"),
                "type": doc.get("type"),
                "abstract": doc.get("abstract"),
                "publication_date": publication_date_str,
                "agencies": (
                    json.dumps(agencies) if agencies else None
                ),  # Store as JSON string
                "document_url": doc.get("html_url"),
                "pdf_url": doc.get("pdf_url"),
                "raw_text_url": doc.get("raw_text_url"),
                "president": doc.get("president"),
                "executive_order_number": doc.get("executive_order_number"),
            }

            processed_doc = {k: v for k, v in processed_doc.items() if v is not None}
            processed_documents.append(processed_doc)
        return processed_documents
    except json.JSONDecodeError:
        print(f"Error decoding JSON from {raw_file_path}")
        return []
    except Exception as e:
        print(f"Error processing file {raw_file_path}: {e}")
        return []


def process_all_new_raw_data():
    if not os.path.exists(config.PROCESSED_DATA_DIR):
        os.makedirs(config.PROCESSED_DATA_DIR)

    processed_files_log = os.path.join(config.PROCESSED_DATA_DIR, "processed_log.txt")
    processed_file_names = set()
    if os.path.exists(processed_files_log):
        with open(processed_files_log, "r") as log_f:
            processed_file_names = set(line.strip() for line in log_f)

    all_processed_data = []
    newly_processed_files = []

    for filename in os.listdir(config.RAW_DATA_DIR):
        if filename.endswith(".json") and filename not in processed_file_names:
            raw_file_path = os.path.join(config.RAW_DATA_DIR, filename)
            print(f"Processing raw file: {filename}")
            data_for_db = process_raw_file(raw_file_path)
            if data_for_db:
                # Save processed data (optional, but good for record keeping)
                processed_file_path = os.path.join(
                    config.PROCESSED_DATA_DIR, f"processed_{filename}"
                )
                with open(processed_file_path, "w", encoding="utf-8") as pf:
                    json.dump(data_for_db, pf, indent=2)
                print(f"Saved processed data to {processed_file_path}")
                all_processed_data.extend(data_for_db)
                newly_processed_files.append(filename)

    if newly_processed_files:
        with open(processed_files_log, "a") as log_f:
            for fname in newly_processed_files:
                log_f.write(f"{fname}\n")

    return all_processed_data


if __name__ == "__main__":

    data_to_load = process_all_new_raw_data()
    if data_to_load:
        print(f"Processed {len(data_to_load)} documents ready for database loading.")
    else:
        print("No new raw data to process or an error occurred.")
