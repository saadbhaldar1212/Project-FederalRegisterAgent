# Federal Register Agent - Agentic RAG Qustion Answering System

## Overview
An agentic retrieval-augmented generation system designed to interface with a daily-updated structured relational database to provide conversational insights over policy documents.

## Project Structure
```
my-project/
├── data_pipeline/          # Contains the data processing pipeline
│   ├── __init__.py
│   ├── downloader.py       # Functions for downloading data
│   ├── processor.py        # Functions for processing data
│   ├── db_loader.py        # Loads processed data into a database
│   └── main_pipeline.py     # Main entry point for the data pipeline
├── agent/                  # Contains the agent for LLM interaction
│   ├── __init__.py
│   ├── llm_client.py       # Client for interacting with the LLM
│   ├── tool_executor.py     # Executes defined tools
│   └── agent_core.py        # Core logic of the agent
├── api/                    # Contains the API for external interaction
│   ├── __init__.py
│   ├── main.py             # Entry point for the API
│   ├── models.py           # Data models for the API
│   ├── templates/          # HTML templates
│   │   └── index.html
│   └── static/             # Static files (CSS/JS)
│       └── script.js
├── db_setup/               # Database setup files
│   └── schema.sql          # SQL schema for the database
├── config.py               # Configuration settings
├── requirements.txt        # Project dependencies
└── README.md               # Project documentation
```

## Setup Instructions
1. Clone the repository:
   ```
   git clone <repository-url>
   cd my-project
   ```

2. Install the required dependencies:
   ```
   py -m pip install -r requirements.txt
   ```

3. Set up the database using the provided schema:
   - Execute the SQL commands in `db_setup/schema.sql` to create the necessary tables.

4. Create a `.env` file in root folder and configure the environment variable as follows:

   ```
   DB_HOST=""
   DB_USER=""
   DB_PASSWORD=""
   DB_NAME=""
   DB_PORT=""
   
   OLLAMA_BASE_URL=""
   OLLAMA_MODEL=""
   OLLAMA_API_KEY=""
   ```

## Usage
- To run the data pipeline, execute:
  ```
  python -m data_pipeline.main_pipeline
  ```

- To start the API, run:
  ```
  python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
  ```
