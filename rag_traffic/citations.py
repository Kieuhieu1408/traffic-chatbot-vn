"""Extract citation references, not judgments of citation correctness."""
import re

def citation_metadata(answer, sources):
    cited=sorted({int(x) for x in re.findall(r'\[(\d+)\]',answer)})
    by_rank={s['rank']:s for s in sources}
    return dict(retrieved_chunk_ids=[s['chunk_id'] for s in sources],
                cited_source_ranks=[r for r in cited if r in by_rank],
                cited_chunk_ids=[by_rank[r]['chunk_id'] for r in cited if r in by_rank],
                invalid_citation_ranks=[r for r in cited if r not in by_rank])
