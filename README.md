# FastAPI Sync/Async Demonstration

## Intro

Demonstrates the interaction patterns between FastAPI sync/async routes, inner functions, and background tasks. FastAPI (via Starlette) uses a default thread pool of 40 workers for executing sync functions called from async contexts. This demonstration shows what happens when concurrent requests exceed this limit.

This project has 7 routes that mix sync and async routes and background tasks.

**Route matrix**

| Endpoint | Pattern (handler / inner / bg-task) |
| --- | --- |
| `/sync-route-sync-inner-async-bg-sync-task` | `def` / sync / sync-bg-task |
| `/sync-route-sync-inner-async-bg-async-task` | `def` / sync / async-bg-task |
| `/sync-route-sync-inner-sync-bg-sync-task` | `def` / sync / sync-bg-task |
| `/async-route-sync-inner-async-bg-async-task` | `async` / **sync (blocking call)** / async-bg-task |
| `/async-route-async-inner-async-bg-async-task` | `async` / async / async-bg-task |
| `/async-route-async-inner-async-bg-sync-task` | `async` / async / **async-bg-task that blocks** |
| `/async-route-async-inner-sync-bg-sync-task` | `async` / async / sync-bg-task |

**What each request does (so you can reason about timings)**
  - **Inner work**:
    - `sync_inner_function()` blocks for ~200ms (`time.sleep(0.2)`)
    - `async_inner_function()` yields for ~200ms (`await asyncio.sleep(0.2)`)
  - **Background work** (scheduled via FastAPI/Starlette `BackgroundTasks`):
    - `sync_background_task()` blocks for ~10s (`time.sleep(10)`)
    - `async_background_task_wrapping_async()` yields for ~10s (`await asyncio.sleep(10)`)
    - `async_background_task_wrapping_sync()` **blocks the event loop for ~10s** (`time.sleep(10)` inside `async def`) — intentionally “bad” to demonstrate failure mode

## What did we learn

- **“Sync vs async route” isn’t the whole story**
  - With **non-blocking inner + non-blocking background work**, sync and async routes look similar at 100 users:
    - `async-route-async-inner-async-bg-async-task`: ~**184 req/s**, ~**206ms** avg
    - `sync-route-sync-inner-async-bg-async-task`: ~**178 req/s**, ~**221ms** avg
    - `async-route-async-inner-sync-bg-sync-task`: ~**184 req/s**, ~**206ms** avg
  - However, the sync route leads to much higher CPU utilization 22.4% vs 16.4% from the fast thread switching between requests.
  - And the sync background task lead to slightly higher CPU utilization 19.2% vs 16.4%  and more memory usage 90.2MB vs 70MB because of the backlog of slow background tasks that got queued up.

- **Calling blocking code from an `async def` handler can halt the whole server**
  - `async-route-sync-inner-async-bg-async-task` calls `sync_inner_function()` directly (which does `time.sleep(0.2)`), so it **blocks the event loop**.
  - Result: throughput collapses to ~**5 req/s** and median latency jumps to ~**3.3s** even at high concurrency.

- **Background tasks can starve the thread pool**
  - **Sync endpoints + sync background tasks** share the same AnyIO thread pool (default capacity **40**).
  - With `sync-route-*-sync-task`, the 10s background work ties up the pool, so requests wait a long time just to start:
    - Example (`sync-route-sync-inner-async-bg-sync-task`, 100 users): ~**8.5 req/s**, median ~**8.8s**

- **Fast responses can hide a massive background-work backlog**
  - `async-route-async-inner-sync-bg-sync-task` keeps request latency low (~**206ms** avg at 100 users), but it queues **thousands** of 10s sync background tasks onto the 40-thread pool.
  - In the 100-user run it finished the 30s test with **~5.4k pending** background tasks; after waiting 60s it still had **~5.2k pending** (roughly **~22 minutes** to drain at 40 threads × 10s/task).

- **“Async” background tasks that do blocking work are catastrophic**
  - `async-route-async-inner-async-bg-sync-task` uses an `async def` background task that calls `time.sleep(10)`, which **blocks the event loop**.
  - In practice the app becomes largely unresponsive (even `/metrics` times out), and the Locust run produced no meaningful request stats.

## Prereqs
  - **Python**: 3.12 (see `pyproject.toml`)
  - **Dependency manager**: Poetry

## Setup

```bash
poetry install
```

## Running the App

```bash
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Running Load Tests

  - **Main runner**: `run_load_tests.sh` (starts a fresh uvicorn for every route + concurrency level)
  - **Concurrencies**: 10, 40, 100 users
  - **Ramp rates**: 5/s, 10/s, 20/s respectively
  - **Duration**: 30s per run
  - **Think time** (per Locust user): random 0.1–0.5s
  - **Artifacts**: `docs/*.{html,csv}` (Locust reports + time-series resource CSV from `resource_monitor.py`)

```bash
chmod +x run_load_tests.sh
./run_load_tests.sh
```

- **View results**
  - Open the per-run Locust HTML reports in `docs/`
  - Or use the dashboard:

```bash
poetry run python embed_data.py
open docs/index.html
```


## Further reading

- [Starlette thread pool behavior](https://www.starlette.dev/threadpool/)
- [Starlette background tasks](https://www.starlette.dev/background/)
- [Behind the scenes: FastAPI concurrency](https://viktor-bubanja.github.io/behind-the-scenes-fastapi-concurrency/)