import asyncio
import os
from datetime import datetime

from .downloader import download_daily_data
from .processor import process_all_new_raw_data
from .db_loader import load_data_to_db

from config import global_config as config


def cleanup_old_files(directory, retention_days: int):
    """Removes files older than retention_days from the specified directory."""
    now = datetime.now()
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path):
            try:
                # Try to extract date from filename like YYYY-MM-DD_*.json
                file_date_str = filename.split("_")[0]
                file_date = datetime.strptime(file_date_str, "%Y-%m-%d")
                if (now - file_date).days > retention_days:
                    os.remove(file_path)
                    print(f"Cleaned up old file: {file_path}")
            except (ValueError, IndexError):

                file_mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                if (now - file_mod_time).days > retention_days:
                    os.remove(file_path)
                    print(f"Cleaned up old file by mod time: {file_path}")


async def run_pipeline():
    print("Starting data pipeline run...")

    # Adjust days_ago as needed. For a truly daily run, it's typically 1.
    print("\n--- Downloading Data ---")
    await download_daily_data(days_ago=1)  # Fetches yesterday's data

    print("\n--- Processing Data ---")
    processed_data = process_all_new_raw_data()

    if processed_data:
        print("\n--- Loading Data to DB ---")
        await load_data_to_db(processed_data)
    else:
        print("\nNo new data processed to load into DB.")

    print("\n--- Cleaning up old files ---")
    cleanup_old_files(config.RAW_DATA_DIR, int(config.PIPELINE_DATA_RETENTION_DAYS))
    cleanup_old_files(
        config.PROCESSED_DATA_DIR, int(config.PIPELINE_DATA_RETENTION_DAYS)
    )

    print("\nData pipeline run finished.")


if __name__ == "__main__":
    asyncio.run(run_pipeline())
