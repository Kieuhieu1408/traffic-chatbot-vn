"""Run the seed through retrieval and configured OpenAI generation.
Run: .venv/bin/python -m evals.run_seed_answers
Makes one paid API request per case with retrieved evidence; writes no API keys.
"""
import json
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter
from rag_traffic.config import Settings
from rag_traffic.generation import SYSTEM_PROMPT, generate_answer
from rag_traffic.indexing import sha256_file
from rag_traffic.retriever import VectorRetriever


def main():
    base = Path(__file__).resolve().parent
    settings = Settings.from_env()
    if not settings.openai_api_key:
        raise SystemExit('Chưa cấu hình OPENAI_API_KEY')
    dataset = base / 'corpus-seed-10.jsonl'
    cases = [json.loads(line) for line in dataset.read_text().splitlines() if line.strip()]
    retriever = VectorRetriever(settings.chunks_file, settings.faiss_file, settings.manifest_file)
    dest = base / 'runs' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    dest.mkdir(parents=True)
    metadata = {'created_at': datetime.now(timezone.utc).isoformat(), 'model': settings.openai_model,
                'top_k': settings.top_k, 'min_score': settings.min_score, 'system_prompt': SYSTEM_PROMPT,
                'dataset_sha256': sha256_file(dataset), 'corpus_sha256': sha256_file(settings.chunks_file),
                'generation_code_sha256': sha256_file(base.parent / 'rag_traffic/generation.py'),
                'retriever_code_sha256': sha256_file(base.parent / 'rag_traffic/retriever.py'),
                'index_manifest': retriever.manifest, 'case_count': len(cases)}
    (dest / 'manifest.json').write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + '\n')
    print('Output:', dest, flush=True)
    with (dest / 'answers.jsonl').open('w') as output:
        for case in cases:
            start = perf_counter()
            results = retriever.search(case['query'], settings.top_k, settings.min_score)
            retrieval_seconds = perf_counter() - start
            start = perf_counter()
            answer, mode = generate_answer(case['query'], results, settings.openai_api_key,
                                           settings.openai_model, case.get('history', ()))
            # Defensive redaction before persisting any returned diagnostic text.
            answer = answer.replace(settings.openai_api_key, '[REDACTED]')
            row = {'case_id': case['case_id'], 'query': case['query'], 'history': case.get('history', []),
                   'answer': answer, 'mode': mode, 'results': [x.to_dict() for x in results],
                   'retrieval_seconds': round(retrieval_seconds, 3),
                   'generation_seconds': round(perf_counter() - start, 3)}
            output.write(json.dumps(row, ensure_ascii=False) + '\n'); output.flush()
            print(case['case_id'], mode, row['generation_seconds'], 's', flush=True)
            if mode != 'rag':
                print('Stopped after fallback; inspect saved trace before further API calls.', flush=True)
                break


if __name__ == '__main__':
    main()
