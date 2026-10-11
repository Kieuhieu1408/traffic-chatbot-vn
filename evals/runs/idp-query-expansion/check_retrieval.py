import json
from pathlib import Path
import rag_traffic.retriever as mod
from rag_traffic.config import Settings
s=Settings.from_env();r=mod.VectorRetriever(s.chunks_file,s.faiss_file,s.manifest_file);expand=mod.retrieval_query
seed=[json.loads(l) for l in Path('evals/corpus-seed-10.jsonl').read_text().splitlines()]
fresh=[json.loads(l) for l in Path('evals/fresh_runs/20260908-natural10/traces.jsonl').read_text().splitlines()]
out=[]
for i,c in enumerate(seed+fresh):
 q=c.get('query',c.get('question'));mod.retrieval_query=lambda q:q;b=r.search(q);mod.retrieval_query=expand;a=r.search(q)
 out.append(dict(case_id=c.get('case_id',c.get('id')),query=q,before=[x.to_dict() for x in b],after=[x.to_dict() for x in a]))
 print(i+1,[x.article[:35] for x in a[:2]],flush=True)
p=Path('evals/runs/idp-query-expansion');p.mkdir(exist_ok=True);(p/'retrieval-before-after.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
