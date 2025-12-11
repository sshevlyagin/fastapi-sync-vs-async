"""Internal metrics endpoint for monitoring thread pool and background task state."""
import threading
import anyio
from fastapi import APIRouter

router = APIRouter()

# Global counter for tracking pending background tasks
_pending_bg_tasks = 0
_bg_tasks_lock = threading.Lock()


def increment_pending_bg_tasks():
    """Increment the pending background task counter (thread-safe)."""
    global _pending_bg_tasks
    with _bg_tasks_lock:
        _pending_bg_tasks += 1


def decrement_pending_bg_tasks():
    """Decrement the pending background task counter (thread-safe)."""
    global _pending_bg_tasks
    with _bg_tasks_lock:
        _pending_bg_tasks -= 1


def get_pending_bg_tasks():
    """Get the current count of pending background tasks."""
    with _bg_tasks_lock:
        return _pending_bg_tasks


@router.get("/metrics")
async def get_metrics():
    """
    Return internal runtime metrics for monitoring.

    Returns:
        dict: Metrics including thread pool stats and background task count
    """
    # Get AnyIO thread pool limiter stats
    # This is the limiter used by Starlette/FastAPI for running sync functions in async contexts
    limiter = anyio.to_thread.current_default_thread_limiter()
    stats = limiter.statistics()

    return {
        "thread_pool": {
            "total_tokens": stats.total_tokens,           # Total thread pool capacity (default: 40)
            "borrowed_tokens": stats.borrowed_tokens,     # Currently active threads
            "available_tokens": stats.total_tokens - stats.borrowed_tokens,
            "tasks_waiting": stats.tasks_waiting,         # Tasks queued for thread pool
        },
        "background_tasks": {
            "pending_count": get_pending_bg_tasks(),      # Background tasks not yet completed
        },
        "threading": {
            "active_thread_count": threading.active_count(),  # Total active threads in process
        }
    }
