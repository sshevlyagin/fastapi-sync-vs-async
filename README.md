# FastAPI Sync/Async Demonstration

Demonstrates the interaction patterns between FastAPI sync/async routes, inner functions, and background tasks.

## Thread Pool Behavior

FastAPI (via Starlette) uses a default thread pool of 40 workers for executing sync functions called from async contexts. This demonstration shows what happens when concurrent requests exceed this limit.

## Setup

```bash
poetry install
```

## Running the App

```bash
poetry run uvicorn app.main:app --reload
```

## Running Load Tests

Test with 40 concurrent users (within thread pool limit):
```bash
poetry run locust -f tests/locustfile.py --headless -u 40 -r 10 -t 30s --html docs/route-X-40users.html
```

Test with 100 concurrent users (exceeds thread pool limit):
```bash
poetry run locust -f tests/locustfile.py --headless -u 100 -r 20 -t 30s --html docs/route-X-100users.html
```

## Routes

See `app/routes.py` for all 7 route combinations demonstrating different sync/async patterns.
