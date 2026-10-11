"""Opt-in local A/B pilot. User feedback is separate from evaluator labels."""
import hashlib
import sqlite3
from pathlib import Path
from uuid import uuid4

EXPERIMENT = 'idp-alias-v1'


def variant(session_id):
    return 'A' if hashlib.sha256((EXPERIMENT+session_id).encode()).digest()[0] < 128 else 'B'


class ArmRetriever:
    def __init__(self, base, arm):
        self.base = base
        self.manifest = base.manifest
        self.ab_metadata = {'experiment': EXPERIMENT, 'variant': arm}
        self.arm = arm

    def search(self, query, k, min_score):
        return self.base.search(query, k, min_score, expand_alias=self.arm == 'B')


class ExperimentStore:
    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.execute('''CREATE TABLE IF NOT EXISTS events (
                id TEXT PRIMARY KEY, experiment TEXT, session TEXT, arm TEXT,
                trace_id TEXT, elapsed REAL, mode TEXT, helpful INTEGER,
                created TEXT DEFAULT CURRENT_TIMESTAMP)''')

    def connect(self):
        return sqlite3.connect(self.path, timeout=10)

    def record(self, session, arm, trace_id, elapsed, mode):
        id = uuid4().hex
        session_hash = hashlib.sha256(session.encode()).hexdigest()
        with self.connect() as db:
            db.execute('INSERT INTO events(id,experiment,session,arm,trace_id,elapsed,mode) VALUES (?,?,?,?,?,?,?)',
                       (id,EXPERIMENT,session_hash,arm,trace_id,elapsed,mode))
        return id

    def feedback(self, id, helpful):
        with self.connect() as db:
            cursor = db.execute('UPDATE events SET helpful=? WHERE id=?', (int(helpful),id))
            return cursor.rowcount == 1
