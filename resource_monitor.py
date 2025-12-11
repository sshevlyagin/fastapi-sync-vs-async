#!/usr/bin/env python3
"""
Resource monitor for FastAPI load tests.

Monitors CPU, memory, thread pool stats, and background task queue.
Runs continuously until:
1. The specified test duration has passed
2. All background tasks have completed (pending_count == 0)

Outputs time-series data to CSV.
"""
import argparse
import csv
import sys
import time
from datetime import datetime
from typing import Optional

import psutil
import requests


def find_uvicorn_pid() -> Optional[int]:
    """Find the uvicorn process serving on port 8000."""
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = proc.info.get('cmdline') or []
            cmdline_str = ' '.join(cmdline)
            if 'uvicorn' in cmdline_str and 'app.main:app' in cmdline_str:
                return proc.pid
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return None


def collect_metrics(pid: int, metrics_url: str, process: psutil.Process) -> Optional[dict]:
    """
    Collect all metrics from process and internal endpoint.

    Args:
        pid: Process ID
        metrics_url: URL of the metrics endpoint
        process: Pre-initialized psutil.Process object

    Returns:
        dict with all metrics, or None if process not found
    """
    try:
        # Process-level metrics
        # cpu_percent() returns the CPU usage since the last call
        # Using interval=None makes it non-blocking but requires previous call to initialize
        cpu_percent = process.cpu_percent(interval=None)
        memory_info = process.memory_info()
        num_threads = process.num_threads()

        metrics = {
            'timestamp': datetime.now().isoformat(),
            'cpu_percent': cpu_percent,
            'memory_rss_mb': memory_info.rss / (1024 * 1024),
            'memory_vms_mb': memory_info.vms / (1024 * 1024),
            'process_threads': num_threads,
        }

        # Internal metrics from endpoint
        try:
            response = requests.get(metrics_url, timeout=1)
            if response.status_code == 200:
                internal = response.json()
                metrics.update({
                    'thread_pool_total': internal['thread_pool']['total_tokens'],
                    'thread_pool_borrowed': internal['thread_pool']['borrowed_tokens'],
                    'thread_pool_available': internal['thread_pool']['available_tokens'],
                    'thread_pool_waiting': internal['thread_pool']['tasks_waiting'],
                    'pending_bg_tasks': internal['background_tasks']['pending_count'],
                    'active_threads': internal['threading']['active_thread_count'],
                })
            else:
                metrics.update({
                    'thread_pool_total': None,
                    'thread_pool_borrowed': None,
                    'thread_pool_available': None,
                    'thread_pool_waiting': None,
                    'pending_bg_tasks': None,
                    'active_threads': None,
                })
        except requests.RequestException:
            # Endpoint unavailable
            metrics.update({
                'thread_pool_total': None,
                'thread_pool_borrowed': None,
                'thread_pool_available': None,
                'thread_pool_waiting': None,
                'pending_bg_tasks': None,
                'active_threads': None,
            })

        return metrics
    except psutil.NoSuchProcess:
        return None


def monitor(output_file: str, test_duration: int, interval: float = 1.0,
            max_wait_for_bg_tasks: int = 60, pid: Optional[int] = None):
    """
    Main monitoring loop.

    Args:
        output_file: Path to output CSV file
        test_duration: Expected duration of the load test in seconds
        interval: Sample interval in seconds
        max_wait_for_bg_tasks: Maximum time to wait for background tasks after test ends
        pid: Process ID to monitor (if None, will search for uvicorn process)
    """
    # Find uvicorn process if PID not provided
    if pid is None:
        pid = find_uvicorn_pid()
        if not pid:
            print("ERROR: Could not find uvicorn process", file=sys.stderr)
            sys.exit(1)

    print(f"Monitoring uvicorn process PID {pid}")
    print(f"Test duration: {test_duration}s, Sample interval: {interval}s")

    # Initialize process object and CPU monitoring
    process = psutil.Process(pid)
    # First call to cpu_percent() initializes the measurement
    # It will return 0.0, but subsequent calls will return actual values
    process.cpu_percent(interval=None)

    fieldnames = [
        'timestamp', 'cpu_percent', 'memory_rss_mb', 'memory_vms_mb',
        'process_threads', 'thread_pool_total', 'thread_pool_borrowed',
        'thread_pool_available', 'thread_pool_waiting', 'pending_bg_tasks',
        'active_threads', 'phase'
    ]

    metrics_url = 'http://localhost:8000/metrics'
    start_time = time.time()
    test_end_time = start_time + test_duration

    with open(output_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        print("\n=== Monitoring Phase 1: During Load Test ===")

        # Phase 1: Monitor during the test
        while time.time() < test_end_time:
            metrics = collect_metrics(pid, metrics_url, process)
            if metrics:
                metrics['phase'] = 'test'
                writer.writerow(metrics)
                f.flush()

                # Print status
                elapsed = time.time() - start_time
                pending = metrics.get('pending_bg_tasks', '?')
                cpu = metrics.get('cpu_percent', '?')
                if cpu != '?':
                    cpu = f"{cpu:.1f}"
                borrowed = metrics.get('thread_pool_borrowed', '?')
                print(f"[{elapsed:.0f}s] CPU: {cpu}%, Threads: {borrowed}/40, Pending BG: {pending}")

            time.sleep(interval)

        print("\n=== Monitoring Phase 2: Waiting for Background Tasks ===")

        # Phase 2: Wait for background tasks to complete
        bg_wait_start = time.time()
        all_tasks_complete = False

        while time.time() - bg_wait_start < max_wait_for_bg_tasks:
            metrics = collect_metrics(pid, metrics_url, process)
            if not metrics:
                print("Process no longer exists")
                break

            metrics['phase'] = 'bg_completion'
            writer.writerow(metrics)
            f.flush()

            pending = metrics.get('pending_bg_tasks')
            if pending is None:
                print("Metrics endpoint not available")
                break

            elapsed_total = time.time() - start_time
            elapsed_bg = time.time() - bg_wait_start
            cpu = metrics.get('cpu_percent', '?')
            if cpu != '?':
                cpu = f"{cpu:.1f}"
            borrowed = metrics.get('thread_pool_borrowed', '?')
            print(f"[{elapsed_total:.0f}s / +{elapsed_bg:.0f}s bg] "
                  f"CPU: {cpu}%, Threads: {borrowed}/40, Pending BG: {pending}")

            if pending == 0:
                all_tasks_complete = True
                total_duration = time.time() - start_time
                bg_completion_time = time.time() - bg_wait_start
                print(f"\n✓ All background tasks completed!")
                print(f"  Test duration: {test_duration}s")
                print(f"  BG completion time: {bg_completion_time:.1f}s")
                print(f"  Total monitoring time: {total_duration:.1f}s")
                break

            time.sleep(interval)

        if not all_tasks_complete:
            print(f"\n⚠ WARNING: Background tasks did not complete within {max_wait_for_bg_tasks}s")
            final_metrics = collect_metrics(pid, metrics_url, process)
            if final_metrics:
                print(f"  Final pending count: {final_metrics.get('pending_bg_tasks', '?')}")

    print(f"\nMonitoring complete. Results written to {output_file}")

    # Return exit code based on whether all tasks completed
    sys.exit(0 if all_tasks_complete else 1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Monitor uvicorn process resources during and after load test'
    )
    parser.add_argument('--output', '-o', required=True,
                        help='Output CSV file path')
    parser.add_argument('--test-duration', '-d', type=int, default=30,
                        help='Expected test duration in seconds (default: 30)')
    parser.add_argument('--interval', '-i', type=float, default=1.0,
                        help='Sample interval in seconds (default: 1.0)')
    parser.add_argument('--max-bg-wait', type=int, default=60,
                        help='Maximum time to wait for background tasks (default: 60)')
    parser.add_argument('--pid', '-p', type=int, default=None,
                        help='Process ID to monitor (if not provided, will search for uvicorn)')

    args = parser.parse_args()

    monitor(
        output_file=args.output,
        test_duration=args.test_duration,
        interval=args.interval,
        max_wait_for_bg_tasks=args.max_bg_wait,
        pid=args.pid
    )
