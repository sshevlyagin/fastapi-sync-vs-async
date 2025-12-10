"""Locust load testing scenarios for all routes."""
from locust import HttpUser, task, between


class SyncRouteSyncInnerAsyncBgSyncTask(HttpUser):
    """Load test: def/sync/async-bg-reg/sync-bg-task"""
    wait_time = between(0.1, 0.5)
    host = "http://localhost:8000"

    @task
    def test_sync_route_sync_inner_async_bg_sync_task(self):
        self.client.get("/sync-route-sync-inner-async-bg-sync-task")


class SyncRouteSyncInnerAsyncBgAsyncTask(HttpUser):
    """Load test: def/sync/async-bg-reg/async-bg-task"""
    wait_time = between(0.1, 0.5)
    host = "http://localhost:8000"

    @task
    def test_sync_route_sync_inner_async_bg_async_task(self):
        self.client.get("/sync-route-sync-inner-async-bg-async-task")


class SyncRouteSyncInnerSyncBgSyncTask(HttpUser):
    """Load test: def/sync/sync-bg-reg/sync-bg-task"""
    wait_time = between(0.1, 0.5)
    host = "http://localhost:8000"

    @task
    def test_sync_route_sync_inner_sync_bg_sync_task(self):
        self.client.get("/sync-route-sync-inner-sync-bg-sync-task")


class AsyncRouteSyncInnerAsyncBgAsyncTask(HttpUser):
    """Load test: async/sync/async-bg-reg/async-bg-task"""
    wait_time = between(0.1, 0.5)
    host = "http://localhost:8000"

    @task
    def test_async_route_sync_inner_async_bg_async_task(self):
        self.client.get("/async-route-sync-inner-async-bg-async-task")


class AsyncRouteAsyncInnerAsyncBgAsyncTask(HttpUser):
    """Load test: async/async/async-bg-reg/async-bg-task"""
    wait_time = between(0.1, 0.5)
    host = "http://localhost:8000"

    @task
    def test_async_route_async_inner_async_bg_async_task(self):
        self.client.get("/async-route-async-inner-async-bg-async-task")


class AsyncRouteAsyncInnerAsyncBgSyncTask(HttpUser):
    """Load test: async/async/async-bg-reg/sync-bg-task"""
    wait_time = between(0.1, 0.5)
    host = "http://localhost:8000"

    @task
    def test_async_route_async_inner_async_bg_sync_task(self):
        self.client.get("/async-route-async-inner-async-bg-sync-task")


class AsyncRouteAsyncInnerSyncBgSyncTask(HttpUser):
    """Load test: async/async/sync-bg-reg/sync-bg-task"""
    wait_time = between(0.1, 0.5)
    host = "http://localhost:8000"

    @task
    def test_async_route_async_inner_sync_bg_sync_task(self):
        self.client.get("/async-route-async-inner-sync-bg-sync-task")
