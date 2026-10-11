"""LangSmith-backed review. Reading and labeling never invoke generation."""
from __future__ import annotations

import asyncio
import hashlib
import json
from datetime import datetime
from uuid import UUID, uuid5

from langsmith import Client
from rag_traffic.config import Settings

KEYS = ['answer_pass', 'review_reason']
NAMESPACE = UUID('717d818b-a9a7-463f-88ea-a37fcb77ab53')


def fingerprint(row):
    return hashlib.sha256(json.dumps(row, sort_keys=True, ensure_ascii=False, default=str).encode()).hexdigest()


def normalize_run(run):
    inputs, outputs = run.inputs or {}, run.outputs or {}
    extra = run.extra or {}
    metadata = run.metadata or extra.get('metadata', {})
    row = {
        'case_id': str(run.id), 'query': inputs.get('query', ''),
        'history': inputs.get('history', []), 'answer': outputs.get('answer', ''),
        'results': outputs.get('sources', []), 'mode': outputs.get('mode', 'error' if run.error else 'unknown'),
        'start_time': run.start_time.isoformat(), 'error': run.error,
        'model': metadata.get('model', '?'), 'top_k': metadata.get('top_k', '?'),
        'session_id': metadata.get('session_id'),
        'generation_seconds': round((run.end_time-run.start_time).total_seconds(), 2) if run.end_time else None,
    }
    row['trace_hash'] = fingerprint(row)
    return row


def label_from_feedback(feedback):
    latest = {}
    for item in sorted(feedback, key=lambda f: str(f.get('modified_at') or f.get('created_at') or '')):
        latest[item['key']] = item
    if not latest:
        return None
    answer = latest.get('answer_pass', {})
    score = answer.get('score')
    verdict = 'pass' if score == 1 else 'fail' if score == 0 else ''
    if not verdict:
        value = str(answer.get('value') or '').strip().casefold()
        verdict = {'đạt': 'pass', 'trượt': 'fail', 'pass': 'pass', 'fail': 'fail'}.get(value, '')
    reason_item = latest.get('review_reason')
    reason = reason_item.get('value', '') if reason_item else answer.get('comment') or ''
    if reason is None: reason = ''
    correction = answer.get('correction') or {}
    if not isinstance(correction, dict): correction = {}
    source = answer.get('feedback_source') or {}
    reviewer = (source.get('metadata') or {}).get('reviewer') or source.get('type') or 'unknown'
    if answer.get('comment') == 'Reviewed by a human in Shiny.': reviewer = 'human (Shiny)'
    return {'verdict': verdict, 'reason': str(reason),
            'correction': correction.get('answer', ''), 'errors': '[]',
            'updated_at': str(answer.get('modified_at') or answer.get('created_at') or ''),
            'reviewer': reviewer}


class LangSmithReview:
    def __init__(self, settings=None, client=None):
        self.settings = settings or Settings.from_env()
        if client is None and not self.settings.langsmith_api_key:
            raise ValueError('Add LANGSMITH_API_KEY to .env, then restart the reviewer.')
        self.client = client or Client(api_key=self.settings.langsmith_api_key,
                                      api_url=self.settings.langsmith_endpoint,
                                      workspace_id=self.settings.langsmith_workspace_id,
                                      timeout_ms=10000)
        self.project_id = None
        self.feedback = {}
        self.rows = {}
        self.values = {0: 'Trượt ', 1: 'Đạt '}

    def read_feedback(self, ids):
        items = list(self.client.list_feedback(run_ids=ids, feedback_key=KEYS))
        grouped = {rid: [] for rid in ids}
        for item in items:
            data = item.model_dump(mode='json')
            grouped.setdefault(str(data['run_id']), []).append(data)
        return grouped

    async def load(self, limit=100):
        project = await asyncio.to_thread(self.client.read_project, project_name=self.settings.langsmith_project)
        project_id = str(project.id)
        rows = []
        async for run in self.client.runs.query(
            project_ids=[project_id], is_root=True, filter='eq(name, "rag-traffic-chat")',
            page_size=min(limit, 100),
            selects=['ID','INPUTS','OUTPUTS','NAME','START_TIME','END_TIME','ERROR','METADATA','EXTRA'],
        ):
            if run.end_time and (run.inputs or {}).get('query'):
                rows.append(normalize_run(run))
            if len(rows) >= limit: break
        rows.sort(key=lambda row: row['start_time'], reverse=True)
        feedback = {}
        for offset in range(0, len(rows), 50):
            ids = [r['case_id'] for r in rows[offset:offset+50]]
            feedback.update(await asyncio.to_thread(self.read_feedback, ids))
        configs = await asyncio.to_thread(lambda: list(self.client.list_feedback_configs(feedback_key=['answer_pass'])))
        values = self.values.copy()
        for config in configs:
            raw = config.model_dump(mode='json').get('feedback_config') or {}
            for category in raw.get('categories') or []:
                if category['value'] in (0, 1): values[category['value']] = category['label']
        # Only replace the visible snapshot when the complete refresh succeeds.
        self.project_id, self.feedback, self.values = project_id, feedback, values
        self.rows = {r['case_id']: r for r in rows}
        return {'rows': rows, 'manifest': {'model': 'mixed', 'project': self.settings.langsmith_project},
                'comments': {}, 'cases': {}, 'dataset_matches': False, 'cloud': True}

    def get(self, run_id):
        return label_from_feedback(self.feedback.get(run_id, []))

    async def url(self, run_id):
        link = await self.client.runs.get_url(run_id, project_id=self.project_id, trace_id=run_id)
        return link.url

    def save(self, run_id, trace_hash, verdict, reason, correction):
        if verdict not in ('pass', 'fail'): raise ValueError('Choose Pass or Fail before saving.')
        if verdict == 'fail' and not reason.strip(): raise ValueError('Explain the failure using the source evidence.')
        row = self.rows[run_id]
        if row['trace_hash'] != trace_hash: raise ValueError('This trace changed. Refresh before reviewing it.')
        old = self.feedback.get(run_id, [])
        current = self.read_feedback([run_id])[run_id]
        if fingerprint(sorted(old, key=lambda f: f['id'])) != fingerprint(sorted(current, key=lambda f: f['id'])):
            raise ValueError('Feedback changed on LangSmith. Keep a copy of your edits, discard them and refresh before saving.')
        latest = {}
        for f in sorted(current, key=lambda f: str(f.get('modified_at') or f.get('created_at') or '')):
            latest[f['key']] = f
        score = 1 if verdict == 'pass' else 0
        # Reason first: a partial failure must never be presented as a completed save.
        for key, value, numeric in [('review_reason', reason.strip(), None),
                                    ('answer_pass', self.values[score], score)]:
            kwargs = {'value': value, 'comment': 'Reviewed by a human in Shiny.'}
            if key == 'answer_pass':
                kwargs.update(score=numeric, correction={'answer': correction.strip()})
            if key in latest:
                self.client.update_feedback(latest[key]['id'], **kwargs)
            else:
                # Stable IDs make retrying an interrupted create idempotent.
                self.client.create_feedback(
                    run_id=run_id, key=key, feedback_id=uuid5(NAMESPACE, run_id+':'+key),
                    session_id=self.project_id, start_time=datetime.fromisoformat(row['start_time']),
                    feedback_source_type='api', source_info={'reviewer': 'human', 'interface': 'shiny'}, **kwargs)
        verified = self.read_feedback([run_id])[run_id]
        label = label_from_feedback(verified)
        if not label or label['verdict'] != verdict or label['reason'] != reason.strip() or label['correction'] != correction.strip():
            raise ValueError('Could not verify both feedback fields. Keep your edits and refresh to check the cloud state.')
        self.feedback[run_id] = verified
        return label
