"""Freeze real retrieval contexts; report known-evidence coverage, not complete precision."""
import json,re
from pathlib import Path
from rag_traffic.config import Settings
from rag_traffic.retriever import VectorRetriever
ROOT=Path(__file__).resolve().parent

def norm(s):return re.sub(r'\W+','',s.lower())

def main():
 s=Settings.from_env();retriever=VectorRetriever(s.chunks_file,s.faiss_file,s.manifest_file)
 rows=[json.loads(l) for split in ['dev','test'] for l in (ROOT/'data'/f'{split}.jsonl').read_text().splitlines()]
 out=[];e2e=[]
 for row in rows:
  if not row['sources']:continue # Missing-evidence controls apply only to fixed context.
  results=retriever.search(row['query'],10);spans=[norm(line) for line in row['sources'][0]['content'].splitlines() if line.strip()]
  qrels=[]
  for result in results:
   text=norm(result.content);enough=all(span in text for span in spans)
   qrels.append(dict(chunk_id=result.chunk_id,rank=result.rank,contains_known_evidence=enough))
  first=next((x['rank'] for x in qrels if x['contains_known_evidence']),None)
  out.append(dict(case_id=row['case_id'],topic=row['group'],capability=row['capability'],
    known_evidence_hit_at_k={k:any(x['contains_known_evidence'] for x in qrels[:k]) for k in [1,3,6,10]},
    known_evidence_reciprocal_rank=1/first if first else 0,qrels=qrels,
    limitation='Span matching checks known evidence only. Unmatched sources are unjudged, not irrelevant; Precision@K withheld.'))
  e2e.append({**row,'sources':[x.to_dict() for x in results[:6]],'context_mode':'real_retrieval','reference_sources':row['sources']})
 (ROOT/'data/retrieval-eval.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
 (ROOT/'data/end-to-end.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in e2e))
 print('Frozen',len(e2e),'real retrieval contexts; precision withheld pending complete relevance review.')
if __name__=='__main__':main()
