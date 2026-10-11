from rag_traffic.citations import citation_metadata

def test_citations_distinguish_unused_and_invalid_sources():
    out=citation_metadata('Một [2], hai [2], sai [9].',[{'rank':1,'chunk_id':'a'},{'rank':2,'chunk_id':'b'}])
    assert out['retrieved_chunk_ids']==['a','b']
    assert out['cited_chunk_ids']==['b']
    assert out['invalid_citation_ranks']==[9]
