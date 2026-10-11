"""Explicit trace inputs: credentials/settings objects are never serialized."""
from __future__ import annotations

import hashlib
import logging
from pathlib import Path

from langsmith import Client as LangSmithClient, trace, tracing_context

from .ab import ArmRetriever
from .citations import citation_metadata
from .config import Settings
from .retriever import retrieval_query
from .generation import SYSTEM_PROMPT, generate_answer

logger = logging.getLogger(__name__)


class Client(LangSmithClient):
    """An observability transport error must not interrupt or repeat generation."""

    def __init__(self, **kwargs):
        self.report_error = kwargs.get('tracing_error_callback', lambda exc: None)
        super().__init__(**kwargs)

    def create_run(self, *args, **kwargs):
        try:
            return super().create_run(*args, **kwargs)
        except Exception as exc:
            self.report_error(exc)

    def update_run(self, *args, **kwargs):
        try:
            return super().update_run(*args, **kwargs)
        except Exception as exc:
            self.report_error(exc)


class ChatTracing:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.client = None
        self.status = 'disabled'
        if settings.langsmith_tracing:
            if not settings.langsmith_api_key:
                self.status = 'missing_api_key'
            else:
                try:
                    self.client = Client(
                        api_key=settings.langsmith_api_key,
                        api_url=settings.langsmith_endpoint,
                        workspace_id=settings.langsmith_workspace_id,
                        timeout_ms=5000,
                        tracing_error_callback=self._upload_error,
                    )
                    self.status = 'configured'
                except Exception:
                    self.status = 'initialization_error'
                    logger.warning('LangSmith initialization failed; tracing unavailable.')
        folder = Path(__file__).resolve().parent
        self.source_hashes = {
            name: hashlib.sha256((folder / name).read_bytes()).hexdigest()
            for name in ('tracing.py', 'retriever.py', 'generation.py', 'config.py')
        }

    def _upload_error(self, error: Exception) -> None:
        self.status = 'upload_error'
        logger.warning('LangSmith upload failed; check key, workspace and endpoint.')

    def close(self) -> None:
        if self.client is not None:
            try:
                self.client.flush()
            except Exception as exc:
                self._upload_error(exc)

    def run(self, retriever, query, history, session_id):
        settings = self.settings
        enabled = self.client is not None
        metadata = {
            'session_id': session_id,
            **(retriever.ab_metadata if isinstance(retriever, ArmRetriever) else {}),
            'top_k': settings.top_k, 'min_score': settings.min_score,
            'model': settings.openai_model,
            'index_manifest': getattr(retriever, 'manifest', {}),
            'source_sha256': self.source_hashes,
        }
        with tracing_context(enabled=enabled, client=self.client,
                             project_name=settings.langsmith_project):
            with trace('rag-traffic-chat', inputs={'query': query, 'history': history},
                       metadata=metadata, tags=['ui-api', 'rag']) as root:
                with trace('retrieve-sources', run_type='retriever',
                           inputs={'query': query, 'retrieval_query': query if getattr(retriever, 'arm', None) == 'A' else retrieval_query(query), 'top_k': settings.top_k,
                                   'min_score': settings.min_score}) as retrieval:
                    results = retriever.search(query, settings.top_k, settings.min_score)
                    sources = [result.to_dict() for result in results]
                    retrieval.end(outputs={'documents': sources})
                # This span includes fallback behavior; it is not always an LLM call.
                with trace('generate-answer', inputs={
                    'query': query, 'history_used': history[-3:],
                    'sources': sources, 'system_prompt': SYSTEM_PROMPT,
                    'model': settings.openai_model,
                    'generation_enabled': bool(settings.openai_api_key and settings.openai_model),
                }) as generation:
                    answer, mode = generate_answer(
                        query, results, settings.openai_api_key,
                        settings.openai_model, history,
                    )
                    generation.end(outputs={'answer': answer, 'mode': mode})
                root.end(outputs={'answer': answer, 'mode': mode, 'sources': sources,
                                  **citation_metadata(answer, sources)})
                return answer, mode, sources, str(root.id) if enabled else None
