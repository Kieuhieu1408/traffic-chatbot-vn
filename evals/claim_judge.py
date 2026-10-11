"""Experimental claim audit; does not replace the default judge."""
import json
from typing import Literal

import httpx
from pydantic import BaseModel, ConfigDict

from evals.judge import PROMPT, judge_input, validate_judgment

AUDIT_PROMPT = PROMPT + '''
Instead of an overall verdict, return an evidence audit. Cover every material factual or
normative claim, including extra paragraphs and limitations, in answer order. Split compound
sentences when clauses make different assertions. Quote each claim exactly from the answer.
For each claim, list the source ranks checked and a short public evidence assessment.
Use supported, unsupported, contradicted, or unresolved. Unsupported means the supplied
sources do not establish this assertion, not that it is false in the real world. Evaluate
exclusivity independently from a neighboring valid claim. Consider whole-answer context.
Also list any material answer-level problems (wrong request or missing necessary information)
in answer_issues; leave empty if none. Do not reveal private chain-of-thought.
'''


class Claim(BaseModel):
    model_config = ConfigDict(extra='forbid')
    quote: str
    source_ranks: list[int]
    status: Literal['supported', 'unsupported', 'contradicted', 'unresolved']
    evidence_assessment: str


class Audit(BaseModel):
    model_config = ConfigDict(extra='forbid')
    claims: list[Claim]
    answer_issues: list[str]


def aggregate(raw, data):
    audit = Audit.model_validate(raw)
    if not audit.claims:
        raise ValueError('Empty claim audit')
    for c in audit.claims:
        # Reuse source/quotation checks even for supported claims.
        checked = validate_judgment(dict(verdict='fail', needs_human_review=False,
            reason='Validate evidence reference', issues=[dict(claim=c.quote,
            category='unsupported', source_ranks=c.source_ranks,
            explanation=c.evidence_assessment)]), data)
        c.quote = checked['issues'][0]['claim']
    if any(not x.strip() for x in audit.answer_issues):
        raise ValueError('Empty answer issue')
    failed = any(c.status in ('unsupported', 'contradicted') for c in audit.claims)
    unresolved = any(c.status == 'unresolved' for c in audit.claims)
    verdict = 'fail' if failed or audit.answer_issues else None if unresolved else 'pass'
    return {'verdict': verdict, 'needs_human_review': verdict is None, **audit.model_dump()}


def evaluate_claims(row, rubric, api_key, model):
    data = judge_input(row)
    response = httpx.post('https://api.openai.com/v1/chat/completions',
        headers={'Authorization': f'Bearer {api_key}'},
        json={'model': model, 'reasoning_effort': 'medium', 'max_completion_tokens': 6000,
              'messages': [{'role': 'system', 'content': AUDIT_PROMPT+'\nRUBRIC:\n'+rubric},
                           {'role': 'user', 'content': json.dumps(data, ensure_ascii=False)}],
              'response_format': {'type': 'json_schema', 'json_schema': {
                  'name': 'claim_audit', 'strict': True, 'schema': Audit.model_json_schema()}}},
        timeout=120)
    response.raise_for_status()
    payload=response.json(); choice=payload['choices'][0]
    if choice.get('finish_reason') != 'stop' or choice['message'].get('refusal'):
        raise ValueError('Incomplete claim audit')
    return {'audit': aggregate(json.loads(choice['message']['content']), data),
            'usage':payload.get('usage', {}), 'response_id':payload.get('id')}
