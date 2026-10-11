"""Version metadata from an explicit source allowlist; never read .env."""
from __future__ import annotations

import hashlib
import platform
import subprocess
from importlib.metadata import distributions
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def version_metadata(root: Path = ROOT) -> dict:
    paths = set()
    for folder in ('rag_traffic', 'tests', 'evals', 'review'):
        paths.update((root / folder).glob('*.py'))
    for name in ('app.py', 'Makefile', 'pyproject.toml', 'requirements.txt', 'requirements-review.txt'):
        paths.add(root / name)
    hashes = {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in sorted(paths) if p.is_file()}
    def git(*args):
        result = subprocess.run(['git', '-C', str(root), *args], capture_output=True, text=True)
        return result.stdout.strip() if result.returncode == 0 else None
    return {
        'git_commit': git('rev-parse', 'HEAD'),
        'git_dirty': bool(git('status', '--porcelain')),
        'source_sha256': hashes,
        'python': platform.python_version(),
        'packages': {d.metadata['Name']: d.version for d in distributions() if d.metadata['Name']},
    }
