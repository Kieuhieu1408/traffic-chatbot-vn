from __future__ import annotations

import os
from time import perf_counter
from collections import OrderedDict
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from threading import Lock
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from rag_traffic.ab import ExperimentStore, ArmRetriever, variant
from rag_traffic.config import Settings
from rag_traffic.retriever import VectorRetriever, retrieval_query
from rag_traffic.tracing import ChatTracing


class QueryRequest(BaseModel):
    query: str = Field(min_length=2, max_length=2000)
    session_id: str | None = Field(default=None, max_length=128)


class FeedbackRequest(BaseModel):
    response_id: str = Field(min_length=32, max_length=32)
    helpful: bool


class ClearHistoryRequest(BaseModel):
    session_id: str | None = Field(default=None, max_length=128)


class SessionStore:
    def __init__(self, max_sessions: int = 500, max_turns: int = 6):
        self.max_sessions = max_sessions
        self.max_turns = max_turns
        self._sessions: OrderedDict[str, list[tuple[str, str]]] = OrderedDict()
        self._lock = Lock()

    def history(self, session_id: str) -> list[tuple[str, str]]:
        with self._lock:
            turns = self._sessions.get(session_id, [])
            if session_id in self._sessions:
                self._sessions.move_to_end(session_id)
            return list(turns)

    def add(self, session_id: str, query: str, answer: str) -> None:
        with self._lock:
            turns = self._sessions.setdefault(session_id, [])
            turns.append((query, answer))
            del turns[:-self.max_turns]
            self._sessions.move_to_end(session_id)
            while len(self._sessions) > self.max_sessions:
                self._sessions.popitem(last=False)

    def clear(self, session_id: str) -> bool:
        with self._lock:
            return self._sessions.pop(session_id, None) is not None


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings.from_env()
    sessions = SessionStore()
    ab_enabled = os.getenv("RAG_AB_ENABLED", "false").lower() == "true"
    ab_store = ExperimentStore(settings.index_dir.parent / "ab" / "events.sqlite3") if ab_enabled else None

    @asynccontextmanager
    async def lifespan(application: FastAPI) -> AsyncIterator[None]:
        application.state.tracing = ChatTracing(settings)
        application.state.retriever = None
        application.state.retriever_error = None
        required = (settings.chunks_file, settings.faiss_file, settings.manifest_file)
        if all(path.is_file() for path in required):
            try:
                application.state.retriever = await run_in_threadpool(
                    VectorRetriever,
                    settings.chunks_file,
                    settings.faiss_file,
                    settings.manifest_file,
                )
            except Exception as exc:
                application.state.retriever_error = str(exc)
        else:
            missing = ", ".join(str(path) for path in required if not path.is_file())
            application.state.retriever_error = f"Thiếu index: {missing}"
        try:
            yield
        finally:
            await run_in_threadpool(application.state.tracing.close)

    application = FastAPI(title="RAG Traffic VN", version="0.2.0", lifespan=lifespan)
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:8000", "http://127.0.0.1:8000"],
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type"],
    )

    @application.get("/", include_in_schema=False)
    async def index_page() -> FileResponse:
        page = settings.static_dir / "index.html"
        if not page.is_file():
            raise HTTPException(status_code=404, detail="Không tìm thấy giao diện")
        return FileResponse(page)

    @application.get("/health")
    async def health(request: Request) -> dict[str, object]:
        retriever = request.app.state.retriever
        return {
            "status": "ready" if retriever else "not_ready",
            "retriever_ready": retriever is not None,
            "detail": request.app.state.retriever_error,
            "generation_enabled": bool(settings.openai_api_key and settings.openai_model),
            "tracing_status": request.app.state.tracing.status,
        }

    @application.post("/search")
    async def search(payload: QueryRequest, request: Request) -> dict[str, object]:
        retriever: VectorRetriever | None = request.app.state.retriever
        if retriever is None:
            raise HTTPException(
                status_code=503,
                detail=request.app.state.retriever_error or "Retriever chưa sẵn sàng",
            )
        query = payload.query.strip()
        session_id = payload.session_id or uuid4().hex
        arm = variant(session_id) if ab_enabled and retrieval_query(query) != query else None
        selected = ArmRetriever(retriever, arm) if arm else retriever
        start = perf_counter()
        answer, mode, sources, trace_id = await run_in_threadpool(
            request.app.state.tracing.run,
            selected,
            query,
            sessions.history(session_id),
            session_id,
        )
        response_id = await run_in_threadpool(ab_store.record, session_id, arm, trace_id, perf_counter()-start, mode) if arm else None
        sessions.add(session_id, query, answer)
        return {
            "session_id": session_id,
            "response_id": response_id,
            "mode": mode,
            "answer": answer,
            "results": sources,
            "trace_id": trace_id,
            "disclaimer": "Thông tin dùng để tra cứu; cần đối chiếu văn bản gốc và tình trạng hiệu lực.",
        }

    @application.post("/feedback")
    async def feedback(payload: FeedbackRequest):
        if ab_store is None or not await run_in_threadpool(ab_store.feedback, payload.response_id, payload.helpful):
            raise HTTPException(status_code=404, detail="Response not found")
        return {"saved": True}

    @application.post("/clear_history")
    async def clear_history(payload: ClearHistoryRequest) -> dict[str, object]:
        cleared = sessions.clear(payload.session_id) if payload.session_id else False
        return {"message": "Đã xóa lịch sử phiên.", "cleared": cleared}

    return application


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=False)
