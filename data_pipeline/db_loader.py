import os
import json
import asyncio
import aiomysql

from config import global_config as config


async def get_db_pool():
    return await aiomysql.create_pool(
        host=config.DB_HOST,
        port=config.DB_PORT,
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        db=config.DB_NAME,
        autocommit=False,
    )


async def load_data_to_db(processed_data_list):
    if not processed_data_list:
        print("No data to load into the database.")
        return

    pool = await get_db_pool()
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            insert_query = """
            INSERT INTO documents (document_number, title, type, abstract, publication_date,
                                   agencies, document_url, pdf_url, raw_text_url, president, executive_order_number)
            VALUES (%(document_number)s, %(title)s, %(type)s, %(abstract)s, %(publication_date)s,
                    %(agencies)s, %(document_url)s, %(pdf_url)s, %(raw_text_url)s, %(president)s, %(executive_order_number)s)
            ON DUPLICATE KEY UPDATE
                title = VALUES(title),
                type = VALUES(type),
                abstract = VALUES(abstract),
                publication_date = VALUES(publication_date),
                agencies = VALUES(agencies),
                document_url = VALUES(document_url),
                pdf_url = VALUES(pdf_url),
                raw_text_url = VALUES(raw_text_url),
                president = VALUES(president),
                executive_order_number = VALUES(executive_order_number),
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
                await cur.executemany(insert_query, data_for_execution)
                await conn.commit()
                print(f"Successfully inserted/updated {cur.rowcount} records.")
            except Exception as e:
                await conn.rollback()
                print(f"Error during database load: {e}")
            finally:
                pool.close()
                print("Database connection closed.")
                await pool.wait_closed()
                print("Pool closed.")


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
