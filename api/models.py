from pydantic import BaseModel
from typing import List, Optional


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    query: str
    history: Optional[List[ChatMessage]] = None


class ChatResponse(BaseModel):
    answer: str
    history: List[ChatMessage]
