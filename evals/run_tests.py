"""Run offline tests and preserve version, output, per-test results and exit code."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from evals.tracking import ROOT, version_metadata


def main() -> int:
    dest = ROOT / 'evals' / 'runs' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ-tests')
    dest.mkdir(parents=True)
    command = [sys.executable, '-m', 'pytest', 'tests', f'--junitxml={dest / "junit.xml"}']
    report = {'created_at': datetime.now(timezone.utc).isoformat(),
              'scope': 'Offline automated tests; not answer-quality evaluation.',
              'command': command, 'version': version_metadata(), 'status': 'running'}
    manifest = dest / 'tests.json'
    manifest.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    env = {**os.environ, 'HF_HUB_OFFLINE': '1', 'TRANSFORMERS_OFFLINE': '1',
           'LANGSMITH_TRACING': 'false'}
    for key in ('OPENAI_API_KEY', 'OPENROUTER_API_KEY'):
        env.pop(key, None)
    with (dest / 'pytest.txt').open('w') as log:
        result = subprocess.run(command, cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT)
    print((dest / 'pytest.txt').read_text(), end='')
    report.update(status='passed' if result.returncode == 0 else 'failed',
                  exit_code=result.returncode, finished_at=datetime.now(timezone.utc).isoformat())
    manifest.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(f'Report: {manifest}')
    return result.returncode


if __name__ == '__main__':
    raise SystemExit(main())
