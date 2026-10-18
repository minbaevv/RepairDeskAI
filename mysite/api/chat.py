import logging

from fastapi import APIRouter, HTTPException, Request

from mysite.chain.agent import run_agent
from mysite.chain.validation import InputRejected, input_chain
from mysite.schemas.chat import AgentResponse, AskResponse, ChatRequest

router = APIRouter(tags=["AI"])
logger = logging.getLogger(__name__)


@router.post("/ask", response_model=AskResponse)
async def ask(data: ChatRequest, request: Request):
    message = await input_chain.ainvoke(data.message)
    if request.app.state.rag is None:
        raise HTTPException(status_code=503, detail="RAG недоступен. Проверьте лог сервера")
    try:
        return await request.app.state.rag.ask(message)
    except InputRejected:
        raise
    except Exception as error:
        logger.exception("RAG request failed")
        raise HTTPException(status_code=502, detail="Ошибка AI-провайдера") from error


@router.post("/agent", response_model=AgentResponse)
async def agent(data: ChatRequest, request: Request):
    message = await input_chain.ainvoke(data.message)
    if request.app.state.agent is None:
        raise HTTPException(status_code=503, detail="Агент недоступен. Проверьте лог сервера")
    try:
        return await run_agent(request.app.state.agent, message)
    except InputRejected:
        raise
    except Exception as error:
        logger.exception("Agent request failed")
        raise HTTPException(
            status_code=502,
            detail="Ошибка агента. Перед повтором проверьте список заявок: действие могло выполниться",
        ) from error
