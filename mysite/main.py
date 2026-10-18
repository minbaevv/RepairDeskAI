import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from mysite.api.chat import router as chat_router
from mysite.api.repair import router as repair_router
from mysite.chain.agent import build_agent
from mysite.chain.rag import RepairRAG
from mysite.chain.validation import InputRejected

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.agent = None
    app.state.rag = None
    try:
        app.state.agent = build_agent()
    except Exception:
        logger.exception("Agent initialization failed")
    try:
        app.state.rag = RepairRAG()
    except Exception:
        logger.exception("RAG initialization failed")
    yield
    app.state.agent = None
    app.state.rag = None


app = FastAPI(title="RepairDesk AI", version="1.0.0", lifespan=lifespan)
app.include_router(repair_router)
app.include_router(chat_router)


@app.exception_handler(InputRejected)
async def input_rejected(request: Request, error: InputRejected):
    return JSONResponse(status_code=422, content={"detail": str(error)})


@app.get("/health")
def health(request: Request):
    return {
        "status": "ok",
        "agent_ready": request.app.state.agent is not None,
        "rag_ready": request.app.state.rag is not None,
    }
