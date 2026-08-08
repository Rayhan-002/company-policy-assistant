import logging
from contextlib import asynccontextmanager

from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, HTTPException  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402

from ..generation import answer_question, get_llm_provider  # noqa: E402
from ..ingestion import list_documents  # noqa: E402
from ..retrieval import Retriever  # noqa: E402
from .schemas import ChatRequest, ChatResponse, CitationResponse, DocumentResponse  # noqa: E402

logger = logging.getLogger("company_policy_assistant.api")

state: dict = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    state["retriever"] = Retriever.load()
    try:
        state["llm"] = get_llm_provider()
    except KeyError as e:
        logger.warning(
            "LLM provider not configured (missing %s) - /chat will return 503 until it is. "
            "Copy .env.example to .env and fill in an API key.",
            e,
        )
        state["llm"] = None
    yield
    state.clear()


app = FastAPI(title="Company Policy Assistant", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def get_health() -> dict:
    return {"status": "ok", "llm_configured": state.get("llm") is not None}


@app.get("/documents", response_model=list[DocumentResponse])
def get_documents() -> list[DocumentResponse]:
    return [
        DocumentResponse(
            document_id=d.document_id,
            title=d.title,
            version=d.version,
            status=d.status,
            category=d.category,
            effective_from=d.effective_from,
        )
        for d in list_documents()
    ]


@app.post("/chat", response_model=ChatResponse)
def post_chat(request: ChatRequest) -> ChatResponse:
    if state.get("llm") is None:
        raise HTTPException(
            status_code=503,
            detail="LLM provider not configured. Copy .env.example to .env and fill in an API key.",
        )

    answer = answer_question(request.question, state["retriever"], state["llm"], top_k=request.top_k)
    return ChatResponse(
        answer=answer.text,
        citations=[
            CitationResponse(
                document_title=c.document_title,
                version=c.version,
                status=c.status,
                section=c.section,
                subsection=c.subsection,
            )
            for c in answer.citations
        ],
    )
