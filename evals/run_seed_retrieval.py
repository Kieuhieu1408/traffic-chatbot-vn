"""Run the reviewed-source seed against configured retrieval, without an LLM call.

Run from repository root: .venv/bin/python -m evals.run_seed_retrieval
Metrics match exact gold IDs; inspect other copies before interpreting misses.
"""
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter
from rag_traffic.config import Settings
from rag_traffic.indexing import sha256_file
from rag_traffic.retriever import VectorRetriever
from evals.tracking import version_metadata


def main() -> None:
    base = Path(__file__).resolve().parent
    dataset = base / 'corpus-seed-10.jsonl'
    cases = [json.loads(line) for line in dataset.read_text().splitlines() if line.strip()]
    settings = Settings.from_env()
    version = version_metadata()
    retriever = VectorRetriever(settings.chunks_file, settings.faiss_file, settings.manifest_file)
    outputs = []
    for case in cases:
        start = perf_counter()
        results = retriever.search(case['query'], settings.top_k, settings.min_score)
        gold = {item['chunk_id'] for item in case['gold_evidence']}
        found = gold & {item.chunk_id for item in results}
        ranks = [item.rank for item in results if item.chunk_id in gold]
        row = {'case_id': case['case_id'], 'query': case['query'],
               'gold_chunk_ids': sorted(gold), 'found_gold_ids': sorted(found),
               'missing_gold_ids': sorted(gold - found),
               'exact_gold_recall': len(found) / len(gold),
               'exact_gold_rr': 1 / min(ranks) if ranks else 0,
               'elapsed_seconds': round(perf_counter() - start, 3),
               'results': [item.to_dict() for item in results]}
        outputs.append(row)
        print(case['case_id'], f'gold={len(found)}/{len(gold)}', f'ranks={ranks}', flush=True)
    report = {'created_at': datetime.now(timezone.utc).isoformat(),
              'version': version,
              'config': {'top_k': settings.top_k, 'min_score': settings.min_score},
              'dataset_sha256': sha256_file(dataset),
              'corpus_sha256': sha256_file(settings.chunks_file),
              'index_manifest': retriever.manifest,
              'scope': 'Retrieval only; exact seed gold IDs, not exhaustive relevance labels; no generation evaluation.',
              'summary': {'cases': len(outputs),
                          'all_gold_found': sum(not r['missing_gold_ids'] for r in outputs),
                          'any_gold_found': sum(bool(r['found_gold_ids']) for r in outputs),
                          'mean_exact_gold_recall': sum(r['exact_gold_recall'] for r in outputs) / len(outputs),
                          'mrr_exact_gold': sum(r['exact_gold_rr'] for r in outputs) / len(outputs)},
              'cases': outputs}
    dest = base / 'runs' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    dest.mkdir(parents=True)
    (dest / 'retrieval.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print('Report:', dest / 'retrieval.json', flush=True)
    print(json.dumps(report['summary'], ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
