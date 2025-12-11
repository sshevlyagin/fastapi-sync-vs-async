"""Route definitions demonstrating sync/async combinations."""
import logging
import threading
from fastapi import APIRouter, BackgroundTasks

from app.functions import sync_inner_function, async_inner_function
from app.background import (
    sync_background_task,
    async_background_task_wrapping_sync,
    async_background_task_wrapping_async
)
from app.metrics import increment_pending_bg_tasks

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/sync-route-sync-inner-async-bg-sync-task")
def sync_route_sync_inner_async_bg_sync_task(background_tasks: BackgroundTasks):
    """def route -> sync inner -> async background registration -> sync bg task"""
    thread_id = threading.get_ident()
    logger.info(f"[sync-route-sync-inner-async-bg-sync-task] Handler executing in thread {thread_id}")

    result = sync_inner_function()
    increment_pending_bg_tasks()
    background_tasks.add_task(sync_background_task)  # async registration of sync task

    return {
        "route": "sync-route-sync-inner-async-bg-sync-task",
        "pattern": "def/sync/async-bg-reg/sync-bg-task",
        "handler_thread": thread_id,
        "inner_result": result
    }


@router.get("/sync-route-sync-inner-async-bg-async-task")
def sync_route_sync_inner_async_bg_async_task(background_tasks: BackgroundTasks):
    """def route -> sync inner -> async background registration -> async bg task wrapping async"""
    thread_id = threading.get_ident()
    logger.info(f"[sync-route-sync-inner-async-bg-async-task] Handler executing in thread {thread_id}")

    result = sync_inner_function()
    increment_pending_bg_tasks()
    background_tasks.add_task(async_background_task_wrapping_async)  # async wrapping async

    return {
        "route": "sync-route-sync-inner-async-bg-async-task",
        "pattern": "def/sync/async-bg-reg/async-bg-task-wrapping-async",
        "handler_thread": thread_id,
        "inner_result": result
    }


@router.get("/sync-route-sync-inner-sync-bg-sync-task")
def sync_route_sync_inner_sync_bg_sync_task(background_tasks: BackgroundTasks):
    """def route -> sync inner -> sync background registration -> sync bg task"""
    thread_id = threading.get_ident()
    logger.info(f"[sync-route-sync-inner-sync-bg-sync-task] Handler executing in thread {thread_id}")

    result = sync_inner_function()
    increment_pending_bg_tasks()
    background_tasks.add_task(sync_background_task)  # sync registration of sync task

    return {
        "route": "sync-route-sync-inner-sync-bg-sync-task",
        "pattern": "def/sync/sync-bg-reg/sync-bg-task",
        "handler_thread": thread_id,
        "inner_result": result
    }


@router.get("/async-route-sync-inner-async-bg-async-task")
async def async_route_sync_inner_async_bg_async_task(background_tasks: BackgroundTasks):
    """async route -> sync inner -> async background registration -> async bg task wrapping async"""
    thread_id = threading.get_ident()
    logger.info(f"[async-route-sync-inner-async-bg-async-task] Handler executing in thread {thread_id}")

    # Calling sync function from async context - will use thread pool
    result = sync_inner_function()
    increment_pending_bg_tasks()
    background_tasks.add_task(async_background_task_wrapping_async)

    return {
        "route": "async-route-sync-inner-async-bg-async-task",
        "pattern": "async/sync/async-bg-reg/async-bg-task-wrapping-async",
        "handler_thread": thread_id,
        "inner_result": result
    }


@router.get("/async-route-async-inner-async-bg-async-task")
async def async_route_async_inner_async_bg_async_task(background_tasks: BackgroundTasks):
    """async route -> async inner -> async background registration -> async bg task wrapping async"""
    thread_id = threading.get_ident()
    logger.info(f"[async-route-async-inner-async-bg-async-task] Handler executing in thread {thread_id}")

    result = await async_inner_function()
    increment_pending_bg_tasks()
    background_tasks.add_task(async_background_task_wrapping_async)

    return {
        "route": "async-route-async-inner-async-bg-async-task",
        "pattern": "async/async/async-bg-reg/async-bg-task-wrapping-async",
        "handler_thread": thread_id,
        "inner_result": result
    }


@router.get("/async-route-async-inner-async-bg-sync-task")
async def async_route_async_inner_async_bg_sync_task(background_tasks: BackgroundTasks):
    """async route -> async inner -> async background registration -> async bg task wrapping sync"""
    thread_id = threading.get_ident()
    logger.info(f"[async-route-async-inner-async-bg-sync-task] Handler executing in thread {thread_id}")

    result = await async_inner_function()
    increment_pending_bg_tasks()
    background_tasks.add_task(async_background_task_wrapping_sync)  # async wrapping blocking sync

    return {
        "route": "async-route-async-inner-async-bg-sync-task",
        "pattern": "async/async/async-bg-reg/async-bg-task-wrapping-sync",
        "handler_thread": thread_id,
        "inner_result": result
    }


@router.get("/async-route-async-inner-sync-bg-sync-task")
async def async_route_async_inner_sync_bg_sync_task(background_tasks: BackgroundTasks):
    """async route -> async inner -> sync background registration -> sync bg task"""
    thread_id = threading.get_ident()
    logger.info(f"[async-route-async-inner-sync-bg-sync-task] Handler executing in thread {thread_id}")

    result = await async_inner_function()
    increment_pending_bg_tasks()
    background_tasks.add_task(sync_background_task)

    return {
        "route": "async-route-async-inner-sync-bg-sync-task",
        "pattern": "async/async/sync-bg-reg/sync-bg-task",
        "handler_thread": thread_id,
        "inner_result": result
    }
