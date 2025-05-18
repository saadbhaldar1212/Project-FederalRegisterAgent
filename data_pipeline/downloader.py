import os
import asyncio
import aiohttp
import aiofiles
import json

from datetime import datetime, timedelta

from config import global_config as config


async def fetch_documents_for_date_range(
    session, start_date_str, end_date_str, per_page=200
):
    """Fetches documents for a given date range, handling pagination."""
    all_results = []
    page = 1
    params = {
        "fields[]": [
            "document_number",
            "title",
            "type",
            "abstract",
            "publication_date",
            "agencies",
            "cfr_references",
            "html_url",
            "pdf_url",
            "raw_text_url",
            "president",
            "executive_order_number",
        ],
        "conditions[publication_date][gte]": start_date_str,
        "conditions[publication_date][lte]": end_date_str,
        "per_page": per_page,
        "page": page,
    }

    print(f"Fetching documents from {start_date_str} to {end_date_str}")
    while True:
        params["page"] = page
        try:
            async with session.get(config.FEDERAL_REGISTER_API_URL) as response:
                response.raise_for_status()
                data = await response.json()
                results = data.get("results", [])
                if not results:
                    break
                all_results.extend(results)
                print(
                    f"Fetched page {page}, {len(results)} results. Total so far: {len(all_results)}"
                )
                if "next_page_url" not in data or not data["next_page_url"]:
                    break
                page += 1
                await asyncio.sleep(0.5)
        except aiohttp.ClientError as e:
            print(f"Error fetching page {page}: {e}")
            break
    return all_results


async def download_daily_data(days_ago=1):
    """Downloads data for N days ago until today."""
    if not os.path.exists(config.RAW_DATA_DIR):
        os.makedirs(config.RAW_DATA_DIR)

    end_date = datetime.now()
    start_date = end_date - timedelta(
        days=days_ago
    )  # Fetch for 'days_ago' up to yesterday.

    date_to_fetch = start_date
    conn = aiohttp.TCPConnector(limit_per_host=5)  # Limit concurrent connections
    async with aiohttp.ClientSession(connector=conn) as session:
        while date_to_fetch < end_date:  # Fetch one day at a time to manage file size
            date_str = date_to_fetch.strftime("%Y-%m-%d")
            print(f"Attempting to download data for: {date_str}")

            daily_documents = await fetch_documents_for_date_range(
                session, date_str, date_str
            )

            if daily_documents:
                file_path = os.path.join(
                    config.RAW_DATA_DIR, f"{date_str}_federal_register.json"
                )
                async with aiofiles.open(file_path, mode="w", encoding="utf-8") as f:
                    await f.write(json.dumps(daily_documents, indent=2))
                print(
                    f"Successfully downloaded {len(daily_documents)} documents for {date_str} to {file_path}"
                )
            else:
                print(f"No documents found for {date_str} or failed to fetch.")

            date_to_fetch += timedelta(days=1)


if __name__ == "__main__":

    asyncio.run(download_daily_data(days_ago=2))
