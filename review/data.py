from __future__ import annotations
import hashlib
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_runs(root: Path = ROOT) -> dict:
    runs = {}
    dataset = root / 'evals/corpus-seed-10.jsonl'
    cases = {c['case_id']: c for c in map(json.loads, dataset.read_text().splitlines())} if dataset.exists() else {}
    dataset_hash = hashlib.sha256(dataset.read_bytes()).hexdigest() if dataset.exists() else None
    for path in sorted((root / 'evals/runs').glob('*/answers.jsonl'), reverse=True):
        rows = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
        if not rows:
            continue
        manifest = json.loads((path.parent / 'manifest.json').read_text())
        review_file = path.parent / 'answer-review.json'
        comments = {c['case_id']: c for c in json.loads(review_file.read_text())} if review_file.exists() else {}
        for row in rows:
            row['trace_hash'] = hashlib.sha256(json.dumps(row, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
        runs[path.parent.name] = {'rows': rows, 'manifest': manifest, 'comments': comments,
                                 'cases': cases if manifest.get('dataset_sha256') == dataset_hash else {},
                                 'dataset_matches': manifest.get('dataset_sha256') == dataset_hash}
    return runs


class LabelStore:
    def __init__(self, path: Path):
        self.path = path
        path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.execute('''CREATE TABLE IF NOT EXISTS labels (
                run_id TEXT, case_id TEXT, trace_hash TEXT, verdict TEXT,
                reason TEXT, errors TEXT, correction TEXT, updated_at TEXT,
                PRIMARY KEY(run_id, case_id, trace_hash))''')

    def connect(self):
        db = sqlite3.connect(self.path, timeout=10)
        db.row_factory = sqlite3.Row
        return db

    def get(self, run_id, case_id, trace_hash):
        with self.connect() as db:
            row = db.execute('SELECT * FROM labels WHERE run_id=? AND case_id=? AND trace_hash=?',
                             (run_id, case_id, trace_hash)).fetchone()
        return dict(row) if row else None

    def save(self, run_id, case_id, trace_hash, verdict, reason, errors, correction):
        if verdict not in {'pass', 'fail'}:
            raise ValueError('Choose Pass or Fail before saving.')
        if verdict == 'fail' and not reason.strip():
            raise ValueError('Explain the failure using the source evidence.')
        with self.connect() as db:
            db.execute('INSERT OR REPLACE INTO labels VALUES (?,?,?,?,?,?,?,?)',
                       (run_id, case_id, trace_hash, verdict, reason.strip(), json.dumps(errors, ensure_ascii=False),
                        correction.strip(), datetime.now(timezone.utc).isoformat()))

    def export(self):
        with self.connect() as db:
            rows = [dict(r) for r in db.execute('SELECT * FROM labels ORDER BY run_id,case_id')]
        for row in rows:
            row['errors'] = json.loads(row['errors'])
            row['reviewer'] = 'human'
        return rows
