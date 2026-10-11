"""Read an existing trace through SmithDB APIs; does not call the model."""
import argparse
import asyncio
import json

from langsmith import Client
from rag_traffic.config import Settings


async def verify(project_id: str, run_id: str) -> dict:
    settings = Settings.from_env()
    if not settings.langsmith_api_key:
        raise ValueError('Missing LANGSMITH_API_KEY')
    client = Client(api_key=settings.langsmith_api_key,
                    api_url=settings.langsmith_endpoint,
                    workspace_id=settings.langsmith_workspace_id)
    run = await client.runs.retrieve(
        run_id, project_id=project_id,
        selects=['ID', 'NAME', 'STATUS', 'END_TIME', 'TRACE_ID', 'OUTPUTS'],
    )
    link = await client.runs.get_url(
        run_id, project_id=project_id, trace_id=str(run.trace_id or run.id),
    )
    return {'run_id': str(run.id), 'name': run.name, 'status': run.status,
            'finished': run.end_time is not None,
            'link': link.model_dump(mode='json')}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project-id', required=True)
    parser.add_argument('--run-id', required=True)
    args = parser.parse_args()
    print(json.dumps(asyncio.run(verify(args.project_id, args.run_id)), ensure_ascii=False, indent=2))
