import os
from openai import AsyncOpenAI

from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv())


class Config:
    def __init__(self):
        try:
            self.DB_HOST = os.getenv("DB_HOST")
            self.DB_USER = os.getenv("DB_USER")
            self.DB_PASSWORD = os.getenv("DB_PASSWORD")
            self.DB_NAME = os.getenv("DB_NAME")
            self.DB_PORT = int(os.getenv("DB_PORT"))
            print("Database configuration loaded successfully.")

            # Ollama Configuration
            self.OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL")
            self.OLLAMA_MODEL = os.getenv("OLLAMA_MODEL")
            self.OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY")
            self.aclient = AsyncOpenAI(
                base_url=self.OLLAMA_BASE_URL,
                api_key=str(self.OLLAMA_API_KEY),
            )

            print("Ollama configuration loaded successfully.")

            # Federal Registry API
            self.FEDERAL_REGISTER_API_URL = "https://www.federalregister.gov/api/v1/public-inspection-documents.json"
            print("Federal Register API URL loaded successfully.")

            # Data Pipeline Configuration
            self.RAW_DATA_DIR = "data_pipeline/raw_data"
            self.PROCESSED_DATA_DIR = "data_pipeline/processed_data"
            self.PIPELINE_DATA_RETENTION_DAYS = 7
            print("Data pipeline configuration loaded successfully.")

            # Tool Configuration
            self.FEDERAL_REGISTRY_TOOL_SCHEMA = [
                {
                    "type": "function",
                    "function": {
                        "name": "query_federal_registry_db",
                        "description": (
                            "Queries the local Federal Registry documents database. "
                            "Use this to find information about US federal documents like rules, proposed rules, notices, and presidential documents (executive orders, proclamations). "
                            "You can filter by keywords, publication dates, document types, and president names."
                        ),
                    },
                }
            ]

            self.SYSTEM_PROMPT = """You are a helpful AI assistant specializing in information from the US Federal Registry.
Your goal is to answer user questions based on documents found in the Federal Registry database.
You have a tool called 'query_federal_registry_db' to search this database.
When a user asks a question:
1. Understand the user's query.
2. If the query can be answered by searching the Federal Registry, decide to use the 'query_federal_registry_db' tool.
   Construct the appropriate parameters for the tool based on the user's query (e.g., keywords, dates, document types, president).
   If dates are relative like "last month" or "this year", calculate the absolute YYYY-MM-DD dates before calling the tool. Today's date is {current_date}.
3. If you use the tool, I will execute it and provide you with the results in JSON format.
4. Analyze the JSON results. If documents are found, synthesize the information into a concise, human-readable answer.
   Mention key details like titles, publication dates, and a brief summary or relevant snippets from the abstract if appropriate.
   Include document numbers or URLs if specifically asked or highly relevant.
5. If no documents are found, inform the user clearly.
6. If the question is a general greeting, chit-chat, or clearly outside the scope of the Federal Registry, answer appropriately without using the tool.
Do not make up information or answer from general knowledge if the query pertains to specific federal documents. Rely on the database.
Do not show the raw JSON from the tool to the user. Summarize it.
Tool calls should not be visible to the end user in your final response.
Keep your answers concise and directly address the user's question using the information retrieved.
"""
            print("Tool configuration loaded successfully.")

        except Exception as e:
            print(f"Error loading configuration: {e}")
            raise e


global_config = Config()
