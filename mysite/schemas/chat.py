from typing import Any

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=3000)


class KnowledgeAnswer(BaseModel):
    answer: str = Field(description="Краткий ответ на русском языке по контексту")


class AskResponse(KnowledgeAnswer):
    sources: list[str]


class ToolResult(BaseModel):
    tool: str
    result: dict[str, Any]


class AgentResponse(BaseModel):
    answer: str
    results: list[ToolResult]
