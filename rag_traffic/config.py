from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")


def _path_from_env(name: str, default: Path) -> Path:
    value = os.getenv(name)
    if not value:
        return default.resolve()
    path = Path(value).expanduser()
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    return path.resolve()


@dataclass(frozen=True)
class Settings:
    source_dir: Path
    index_dir: Path
    static_dir: Path
    embedding_model: str
    openai_api_key: str | None
    openai_model: str | None
    top_k: int
    min_score: float
    langsmith_tracing: bool = False
    langsmith_api_key: str | None = None
    langsmith_project: str = "rag-traffic-vn"
    langsmith_endpoint: str = "https://api.smith.langchain.com"
    langsmith_workspace_id: str | None = None

    @property
    def chunks_file(self) -> Path:
        return self.index_dir / "chunks.jsonl"

    @property
    def faiss_file(self) -> Path:
        return self.index_dir / "faiss.index"

    @property
    def manifest_file(self) -> Path:
        return self.index_dir / "manifest.json"

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            source_dir=_path_from_env("RAG_SOURCE_DIR", PROJECT_ROOT / "data/raw/Thongtu"),
            index_dir=_path_from_env("RAG_INDEX_DIR", PROJECT_ROOT / "data/index"),
            static_dir=_path_from_env("RAG_STATIC_DIR", PROJECT_ROOT / "static"),
            embedding_model=os.getenv(
                "RAG_EMBEDDING_MODEL", "intfloat/multilingual-e5-small"
            ),
            openai_api_key=os.getenv("OPENAI_API_KEY", "").strip() or None,
            openai_model=os.getenv("OPENAI_MODEL", "gpt-5.4-mini").strip() or "gpt-5.4-mini",
            top_k=max(1, int(os.getenv("RAG_TOP_K", "6"))),
            min_score=float(os.getenv("RAG_MIN_SCORE", "0.55")),
            langsmith_tracing=os.getenv("LANGSMITH_TRACING", "false").strip().lower() == "true",
            langsmith_api_key=os.getenv("LANGSMITH_API_KEY", "").strip() or None,
            langsmith_project=os.getenv("LANGSMITH_PROJECT", "rag-traffic-vn").strip() or "rag-traffic-vn",
            langsmith_endpoint=os.getenv("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com").strip(),
            langsmith_workspace_id=os.getenv("LANGSMITH_WORKSPACE_ID", "").strip() or None,
        )
