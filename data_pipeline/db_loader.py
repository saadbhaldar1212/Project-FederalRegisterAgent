import os
import json
import asyncio
import pymysql

from config import global_config as config


def get_db_pool():
    timeout = 10
    connection = pymysql.connect(
        charset="utf8mb4",
        connect_timeout=timeout,
        cursorclass=pymysql.cursors.DictCursor,
        db=config.DB_NAME,
        host=config.DB_HOST,
        password=config.DB_PASSWORD,
        read_timeout=timeout,
        port=config.DB_PORT,
        user=config.DB_USER,
        write_timeout=timeout,
    )
    return connection


def load_data_to_db(processed_data_list):
    if not processed_data_list:
        print("No data to load into the database.")
        return

    connection = get_db_pool()
    with connection.cursor() as cur:
        insert_query = """
        INSERT INTO documents (document_number, title, type, abstract, publication_date, agencies, document_url, pdf_url, raw_text_url, president, executive_order_number)
        VALUES (%(document_number)s, %(title)s, %(type)s, %(abstract)s, %(publication_date)s,%(agencies)s, %(document_url)s, %(pdf_url)s, %(raw_text_url)s, %(president)s, %(executive_order_number)s) AS alias
        ON DUPLICATE KEY UPDATE
            title = alias.title,
            type = alias.type,
            abstract = alias.abstract,
            publication_date = alias.publication_date,
            agencies = alias.agencies,
            document_url = alias.document_url,
            pdf_url = alias.pdf_url,
            raw_text_url = alias.raw_text_url,
            president = alias.president,
            executive_order_number = alias.executive_order_number,
            updated_at = CURRENT_TIMESTAMP
        """

        default_keys = [
            "document_number",
            "title",
            "type",
            "abstract",
            "publication_date",
            "agencies",
            "document_url",
            "pdf_url",
            "raw_text_url",
            "president",
            "executive_order_number",
        ]

        data_for_execution = []
        for record in processed_data_list:

            normalized_record = {key: record.get(key) for key in default_keys}
            data_for_execution.append(normalized_record)

        try:
            cur.executemany(insert_query, data_for_execution)
            connection.commit()
            print(f"Successfully inserted/updated {cur.rowcount} records.")
        except Exception as e:
            connection.rollback()
            print(f"Error during database load: {e}")
        finally:
            connection.close()
            print("Database connection closed.")


if __name__ == "__main__":

    sample_processed_file = os.path.join(
        config.PROCESSED_DATA_DIR, "processed_YYYY-MM-DD_federal_register.json"
    )  # replace YYYY-MM-DD
    if os.path.exists(sample_processed_file):
        with open(sample_processed_file, "r") as f:
            test_data = json.load(f)
        asyncio.run(load_data_to_db(test_data))
    else:
        print(f"Sample processed file not found: {sample_processed_file}")
