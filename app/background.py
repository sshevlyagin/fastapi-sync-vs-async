"""Background task functions for FastAPI."""
import time
import asyncio
import logging
import threading

logger = logging.getLogger(__name__)


def sync_background_task():
    """Synchronous background task - pure blocking sync."""
    thread_id = threading.get_ident()
    logger.info(f"[sync_background_task] Started in thread {thread_id}")
    time.sleep(10)  # Simulate blocking work
    logger.info(f"[sync_background_task] Completed in thread {thread_id}")


async def async_background_task_wrapping_sync():
    """Async background task that wraps a blocking sync operation."""
    thread_id = threading.get_ident()
    logger.info(f"[async_background_task_wrapping_sync] Started in thread {thread_id}")
    # This will block the event loop - BAD practice but demonstrates the issue
    time.sleep(10)  # Blocking call inside async function
    logger.info(f"[async_background_task_wrapping_sync] Completed in thread {thread_id}")


async def async_background_task_wrapping_async():
    """Async background task with pure async operations."""
    thread_id = threading.get_ident()
    logger.info(f"[async_background_task_wrapping_async] Started in thread {thread_id}")
    await asyncio.sleep(10)  # Pure async work
    logger.info(f"[async_background_task_wrapping_async] Completed in thread {thread_id}")
