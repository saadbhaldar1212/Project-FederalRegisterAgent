import os
import uvicorn
import pymysql

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from api.models import ChatRequest, ChatResponse, ChatMessage
from agent.agent_core import process_user_query

app = FastAPI()


current_dir = os.path.dirname(os.path.abspath(__file__))
app.mount(
    "/static", StaticFiles(directory=os.path.join(current_dir, "static")), name="static"
)
templates = Jinja2Templates(directory=os.path.join(current_dir, "templates"))


@app.get("/", response_class=HTMLResponse)
async def get_chat_ui(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/chat", response_model=ChatResponse)
async def chat_with_agent(chat_request: ChatRequest):
    user_query = chat_request.query
    history = chat_request.history if chat_request.history else []
    history_for_agent = [msg.model_dump() for msg in history]
    agent_answer_content = await process_user_query(user_query, history_for_agent)
    updated_history = history + [
        ChatMessage(role="user", content=user_query),
        ChatMessage(role="assistant", content=agent_answer_content),
    ]

    return ChatResponse(answer=agent_answer_content, history=updated_history)


@app.post("/run_data_pipeline")
async def run_data_pipeline():
    """Endpoint to trigger the data pipeline."""
    # Importing here to avoid circular import issues
    from data_pipeline.main_pipeline import run_pipeline

    await run_pipeline()
    return {"message": "Data pipeline run triggered."}


@app.get("/get_database")
async def get_database():
    """
    Returns all rows from your MySQL database table as a list of dicts.
    Update connection details and table name as needed.
    """

    try:
        conn = pymysql.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
            cursorclass=pymysql.cursors.DictCursor,
        )
        with conn.cursor() as cursor:
            cursor.execute(f"SELECT * FROM documents")
            rows = cursor.fetchall()
        conn.close()
        return rows
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"MySQL error: {e}")


if __name__ == "__main__":
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
