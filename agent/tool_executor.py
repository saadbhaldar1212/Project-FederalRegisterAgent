import aiomysql
import json
from config import global_config as config


async def get_db_pool_tool():
    return await aiomysql.create_pool(
        host=config.DB_HOST,
        port=config.DB_PORT,
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        db=config.DB_NAME,
        autocommit=True,
    )


async def query_federal_registry_db(**kwargs):
    """
    Actually executes the SQL query against the MySQL database based on LLM parameters.
    This is the function the agent_core will call, NOT eval().
    """
    pool = await get_db_pool_tool()
    results = []
    try:
        async with pool.acquire() as conn:
            async with conn.cursor(
                aiomysql.DictCursor
            ) as cur:  # DictCursor for easy conversion to JSON
                base_query = "SELECT document_number, title, type, abstract, publication_date, agencies, president, document_url FROM documents"
                conditions = []
                params = []

                if "query_keywords" in kwargs and kwargs["query_keywords"]:
                    keywords = kwargs["query_keywords"].split()
                    keyword_conditions = []
                    for kw in keywords:
                        keyword_conditions.append("(title LIKE %s OR abstract LIKE %s)")
                        params.extend([f"%{kw}%", f"%{kw}%"])
                    if keyword_conditions:
                        conditions.append(f"({' AND '.join(keyword_conditions)})")

                if (
                    "publication_date_exact" in kwargs
                    and kwargs["publication_date_exact"]
                ):
                    conditions.append("publication_date = %s")
                    params.append(kwargs["publication_date_exact"])
                elif (
                    "publication_date_start" in kwargs
                    and "publication_date_end" in kwargs
                    and kwargs["publication_date_start"]
                    and kwargs["publication_date_end"]
                ):
                    conditions.append("publication_date BETWEEN %s AND %s")
                    params.extend(
                        [
                            kwargs["publication_date_start"],
                            kwargs["publication_date_end"],
                        ]
                    )
                elif (
                    "publication_date_start" in kwargs
                    and kwargs["publication_date_start"]
                ):
                    conditions.append("publication_date >= %s")
                    params.append(kwargs["publication_date_start"])
                elif (
                    "publication_date_end" in kwargs and kwargs["publication_date_end"]
                ):
                    conditions.append("publication_date <= %s")
                    params.append(kwargs["publication_date_end"])

                if "document_type" in kwargs and kwargs["document_type"]:
                    doc_types = [
                        dt.strip() for dt in kwargs["document_type"].upper().split(",")
                    ]
                    if doc_types:
                        type_placeholders = ", ".join(["%s"] * len(doc_types))
                        conditions.append(f"UPPER(type) IN ({type_placeholders})")
                        params.extend(doc_types)

                if "president_name" in kwargs and kwargs["president_name"]:
                    conditions.append("president LIKE %s")
                    params.append(f"%{kwargs['president_name']}%")

                if "agency_name" in kwargs and kwargs["agency_name"]:

                    conditions.append(
                        "JSON_UNQUOTE(JSON_EXTRACT(agencies, '$[*]')) LIKE %s"
                    )
                    params.append(f"%{kwargs['agency_name']}%")

                if conditions:
                    base_query += " WHERE " + " AND ".join(conditions)

                sort_order = "DESC"
                if (
                    "sort_by_date" in kwargs
                    and kwargs["sort_by_date"]
                    and kwargs["sort_by_date"].lower() == "asc"
                ):
                    sort_order = "ASC"
                base_query += f" ORDER BY publication_date {sort_order}"

                limit = int(kwargs.get("limit", 5))
                limit = min(max(1, limit), 25)
                base_query += f" LIMIT %s"
                params.append(limit)

                await cur.execute(base_query, tuple(params))
                query_results = await cur.fetchall()

                if query_results:
                    for row in query_results:

                        if row.get("publication_date"):
                            row["publication_date"] = row[
                                "publication_date"
                            ].isoformat()

                        if row.get("agencies") and isinstance(row.get("agencies"), str):
                            try:
                                row["agencies"] = json.loads(row["agencies"])
                            except json.JSONDecodeError:
                                row["agencies"] = [row["agencies"]]  # or handle error
                        results.append(dict(row))
                    return json.dumps(
                        {"found_documents": results, "count": len(results)}
                    )
                else:
                    return json.dumps(
                        {
                            "message": "No documents found matching your criteria.",
                            "count": 0,
                        }
                    )
    except Exception as e:
        print(f"Database query error: {e}")
        return json.dumps({"error": f"Failed to query database: {str(e)}", "count": 0})
    finally:
        if pool:
            pool.close()
            await pool.wait_closed()
