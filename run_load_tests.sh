#!/bin/bash

# Ensure results directory exists
mkdir -p thoughts/sergeis/results

echo "Starting load tests for all routes..."
echo "Make sure the FastAPI app is running on http://localhost:8000"
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

for route_config in "${routes[@]}"
do
    IFS='|' read -r route_name class_name <<< "$route_config"

    echo "====================================="
    echo "Testing ${route_name} with 10 users"
    echo "====================================="
    poetry run locust \
        -f tests/locustfile.py \
        --headless \
        -u 10 \
        -r 5 \
        -t 30s \
        --only-summary \
        --html "thoughts/sergeis/results/${route_name}-10users.html" \
        --csv "thoughts/sergeis/results/${route_name}-10users" \
        ${class_name}

    echo ""
    echo "====================================="
    echo "Testing ${route_name} with 40 users"
    echo "====================================="
    poetry run locust \
        -f tests/locustfile.py \
        --headless \
        -u 40 \
        -r 10 \
        -t 30s \
        --only-summary \
        --html "thoughts/sergeis/results/${route_name}-40users.html" \
        --csv "thoughts/sergeis/results/${route_name}-40users" \
        ${class_name}

    echo ""
    echo "====================================="
    echo "Testing ${route_name} with 100 users"
    echo "====================================="
    poetry run locust \
        -f tests/locustfile.py \
        --headless \
        -u 100 \
        -r 20 \
        -t 30s \
        --only-summary \
        --html "thoughts/sergeis/results/${route_name}-100users.html" \
        --csv "thoughts/sergeis/results/${route_name}-100users" \
        ${class_name}

    echo ""
    echo "Sleeping 5 seconds before next test..."
    sleep 5
done

echo "====================================="
echo "All tests completed!"
echo "Results available in thoughts/sergeis/results/"
echo "====================================="
