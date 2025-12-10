"""Inner functions called by route handlers."""
import time
import asyncio
import logging
import threading

logger = logging.getLogger(__name__)


def sync_inner_function():
    """Synchronous inner function that simulates I/O work."""
    thread_id = threading.get_ident()
    logger.info(f"[sync_inner_function] Executing in thread {thread_id}")
    time.sleep(0.2)  # Simulate I/O work
    logger.info(f"[sync_inner_function] Completed in thread {thread_id}")
    return {"type": "sync", "thread_id": thread_id}


async def async_inner_function():
    """Asynchronous inner function that simulates I/O work."""
    thread_id = threading.get_ident()
    logger.info(f"[async_inner_function] Executing in thread {thread_id}")
    await asyncio.sleep(0.2)  # Simulate async I/O work
    logger.info(f"[async_inner_function] Completed in thread {thread_id}")
    return {"type": "async", "thread_id": thread_id}
