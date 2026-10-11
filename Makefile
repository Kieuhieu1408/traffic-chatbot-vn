.PHONY: install ingest index test serve

install:
	uv venv --python 3.14 .venv
	uv pip install --python .venv/bin/python torch --index-url https://download.pytorch.org/whl/cpu
	uv pip install --python .venv/bin/python -r requirements.txt

ingest:
	.venv/bin/python metadata.py

index:
	.venv/bin/python embeddings.py --batch-size 32

test:
	.venv/bin/python -m pytest

.PHONY: check eval-retrieval
check:
	.venv/bin/python -m evals.run_tests

eval-retrieval:
	HF_HUB_OFFLINE=1 .venv/bin/python -m evals.run_seed_retrieval

serve:
	.venv/bin/python app.py

.PHONY: review-install review
review-install:
	uv pip install --python .venv/bin/python -r requirements-review.txt

review:
	.venv/bin/python -m shiny run --host 127.0.0.1 --port 8001 review/app.py

.PHONY: judge
# Paid OpenAI calls; only runs when explicitly invoked.
judge:
	.venv/bin/python -m evals.run_judge --limit 10
