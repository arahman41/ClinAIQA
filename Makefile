.PHONY: up down test test-harness metrics loadtest dev-frontend

# Start FastAPI plus PostgreSQL with pgvector locally
up:
	docker compose up --build

# Stop and remove containers (data volume is preserved)
down:
	docker compose down

# Run the full harness test suite
test:
	pytest

# Run only the core evaluation-logic tests (the CI gate)
test-harness:
	pytest -m harness

# Compute precision and recall on the held-out set (run once at end of build)
metrics:
	python -m clinaiqa.eval.report_metrics

# Run the load test
loadtest:
	locust -f loadtest/locustfile.py

# Start the React dashboard dev server
dev-frontend:
	cd frontend && npm run dev
