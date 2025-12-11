#!/bin/bash

# Ensure results directory exists
mkdir -p thoughts/sergeis/results

echo "Starting load tests for all routes..."
echo "Each test will start a fresh uvicorn instance"
echo ""

# Array of route configurations: "route_name|class_name"
declare -a routes=(
    "sync-route-sync-inner-async-bg-sync-task|SyncRouteSyncInnerAsyncBgSyncTask"
    "sync-route-sync-inner-async-bg-async-task|SyncRouteSyncInnerAsyncBgAsyncTask"
    "sync-route-sync-inner-sync-bg-sync-task|SyncRouteSyncInnerSyncBgSyncTask"
    "async-route-sync-inner-async-bg-async-task|AsyncRouteSyncInnerAsyncBgAsyncTask"
    "async-route-async-inner-async-bg-async-task|AsyncRouteAsyncInnerAsyncBgAsyncTask"
    "async-route-async-inner-async-bg-sync-task|AsyncRouteAsyncInnerAsyncBgSyncTask"
    "async-route-async-inner-sync-bg-sync-task|AsyncRouteAsyncInnerSyncBgSyncTask"
)

# Function to start uvicorn and wait for it to be ready
start_uvicorn() {
    echo "Starting uvicorn..."
    poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 > /tmp/uvicorn.log 2>&1 &
    UVICORN_PID=$!

    # Wait for uvicorn to be ready (max 10 seconds)
    for i in {1..20}; do
        if curl -s http://localhost:8000/ > /dev/null 2>&1; then
            echo "Uvicorn ready (PID: $UVICORN_PID)"
            return 0
        fi
        sleep 0.5
    done

    echo "ERROR: Uvicorn failed to start"
    return 1
}

# Function to stop uvicorn
stop_uvicorn() {
    echo "Stopping uvicorn..."
    if [ ! -z "$UVICORN_PID" ]; then
        kill $UVICORN_PID 2>/dev/null
        wait $UVICORN_PID 2>/dev/null
        echo "Uvicorn stopped"
    fi
}

# Run tests for each route at different concurrency levels
for route_config in "${routes[@]}"
do
    IFS='|' read -r route_name class_name <<< "$route_config"

    # Test with 10 users
    echo ""
    echo "=========================================="
    echo "Testing ${route_name} with 10 users"
    echo "=========================================="

    start_uvicorn
    if [ $? -ne 0 ]; then
        echo "Skipping test due to uvicorn startup failure"
        continue
    fi

    # Start resource monitor in background with the correct PID
    poetry run python resource_monitor.py \
        --output "results/${route_name}-10users_resources.csv" \
        --test-duration 30 \
        --interval 1 \
        --pid $UVICORN_PID &
    MONITOR_PID=$!

    # Run locust test
    poetry run locust \
        -f tests/locustfile.py \
        --headless \
        -u 10 \
        -r 5 \
        -t 30s \
        --only-summary \
        --html "results/${route_name}-10users.html" \
        --csv "results/${route_name}-10users" \
        ${class_name}

    # Wait for resource monitor to finish (it waits for bg tasks)
    echo "Waiting for resource monitor to complete..."
    wait $MONITOR_PID

    stop_uvicorn
    sleep 2

    # Test with 40 users
    echo ""
    echo "=========================================="
    echo "Testing ${route_name} with 40 users"
    echo "=========================================="

    start_uvicorn
    if [ $? -ne 0 ]; then
        echo "Skipping test due to uvicorn startup failure"
        continue
    fi

    # Start resource monitor in background with the correct PID
    poetry run python resource_monitor.py \
        --output "results/${route_name}-40users_resources.csv" \
        --test-duration 30 \
        --interval 1 \
        --pid $UVICORN_PID &
    MONITOR_PID=$!

    # Run locust test
    poetry run locust \
        -f tests/locustfile.py \
        --headless \
        -u 40 \
        -r 10 \
        -t 30s \
        --only-summary \
        --html "results/${route_name}-40users.html" \
        --csv "results/${route_name}-40users" \
        ${class_name}

    # Wait for resource monitor to finish (it waits for bg tasks)
    echo "Waiting for resource monitor to complete..."
    wait $MONITOR_PID

    stop_uvicorn
    sleep 2

    # Test with 100 users
    echo ""
    echo "=========================================="
    echo "Testing ${route_name} with 100 users"
    echo "=========================================="

    start_uvicorn
    if [ $? -ne 0 ]; then
        echo "Skipping test due to uvicorn startup failure"
        continue
    fi

    # Start resource monitor in background with the correct PID
    poetry run python resource_monitor.py \
        --output "results/${route_name}-100users_resources.csv" \
        --test-duration 30 \
        --interval 1 \
        --pid $UVICORN_PID &
    MONITOR_PID=$!

    # Run locust test
    poetry run locust \
        -f tests/locustfile.py \
        --headless \
        -u 100 \
        -r 20 \
        -t 30s \
        --only-summary \
        --html "results/${route_name}-100users.html" \
        --csv "results/${route_name}-100users" \
        ${class_name}

    # Wait for resource monitor to finish (it waits for bg tasks)
    echo "Waiting for resource monitor to complete..."
    wait $MONITOR_PID

    stop_uvicorn
    sleep 2
done

echo ""
echo "=========================================="
echo "All tests completed!"
echo "Results available in results/"
echo "=========================================="
