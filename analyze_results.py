"""Analyze Locust test results and generate markdown reports."""
import csv
import glob
from pathlib import Path
from datetime import datetime


def parse_locust_stats(csv_file: str) -> dict:
    """Parse Locust stats CSV file."""
    stats = {
        'total_requests': 0,
        'failures': 0,
        'avg_response_time': 0,
        'min_response_time': 0,
        'max_response_time': 0,
        'rps': 0,
        'percentiles': {}
    }

    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['Type'] == 'GET' and 'Aggregated' not in row['Name']:
                stats['total_requests'] = int(row['Request Count'])
                stats['failures'] = int(row['Failure Count'])
                stats['avg_response_time'] = float(row['Average Response Time'])
                stats['min_response_time'] = float(row['Min Response Time'])
                stats['max_response_time'] = float(row['Max Response Time'])
                stats['rps'] = float(row['Requests/s'])
                stats['percentiles'] = {
                    '50': float(row.get('50%', 0)),
                    '66': float(row.get('66%', 0)),
                    '75': float(row.get('75%', 0)),
                    '80': float(row.get('80%', 0)),
                    '90': float(row.get('90%', 0)),
                    '95': float(row.get('95%', 0)),
                    '98': float(row.get('98%', 0)),
                    '99': float(row.get('99%', 0)),
                    '99.9': float(row.get('99.9%', 0)),
                    '99.99': float(row.get('99.99%', 0)),
                    '100': float(row.get('100%', 0)),
                }

    return stats


def generate_markdown_report(results_dir: str = "thoughts/sergeis/results"):
    """Generate comprehensive markdown report from all test results."""

    routes = [
        ("sync-route-sync-inner-async-bg-sync-task", "`def` / sync inner / async bg reg / sync bg task"),
        ("sync-route-sync-inner-async-bg-async-task", "`def` / sync inner / async bg reg / async bg task"),
        ("sync-route-sync-inner-sync-bg-sync-task", "`def` / sync inner / sync bg reg / sync bg task"),
        ("async-route-sync-inner-async-bg-async-task", "`async` / sync inner / async bg reg / async bg task"),
        ("async-route-async-inner-async-bg-async-task", "`async` / async inner / async bg reg / async bg task"),
        ("async-route-async-inner-async-bg-sync-task", "`async` / async inner / async bg reg / sync bg task"),
        ("async-route-async-inner-sync-bg-sync-task", "`async` / async inner / sync bg reg / sync bg task"),
    ]

    report = [
        "# FastAPI Sync/Async Load Test Results",
        "",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## Test Configuration",
        "",
        "- **Duration**: 30 seconds per test",
        "- **Spawn Rates**: 5 users/sec (10 users), 10 users/sec (40 users), 20 users/sec (100 users)",
        "- **Sleep Times**: 0.2s (inner functions), 0.3s (background tasks)",
        "- **Thread Pool**: Default (40 workers)",
        "",
        "## Route Patterns",
        "",
        "| Route | Pattern |",
        "|-------|---------|",
    ]

    for route_name, pattern in routes:
        report.append(f"| {route_name} | {pattern} |")

    report.extend([
        "",
        "## Results Summary",
        ""
    ])

    # Process each route
    for route_name, pattern in routes:
        report.append(f"### {route_name}")
        report.append("")

        # 10 users
        csv_10 = f"{results_dir}/{route_name}-10users_stats.csv"
        if Path(csv_10).exists():
            stats_10 = parse_locust_stats(csv_10)
            report.extend([
                "#### 10 Concurrent Users (Well Below Thread Pool Limit)",
                "",
                f"- **Total Requests**: {stats_10['total_requests']:,}",
                f"- **Failures**: {stats_10['failures']}",
                f"- **RPS**: {stats_10['rps']:.2f}",
                f"- **Avg Response Time**: {stats_10['avg_response_time']:.0f}ms",
                f"- **Min/Max**: {stats_10['min_response_time']:.0f}ms / {stats_10['max_response_time']:.0f}ms",
                "",
                "**Percentiles:**",
                f"- 50th: {stats_10['percentiles']['50']:.0f}ms",
                f"- 95th: {stats_10['percentiles']['95']:.0f}ms",
                f"- 99th: {stats_10['percentiles']['99']:.0f}ms",
                "",
            ])

        # 40 users
        csv_40 = f"{results_dir}/{route_name}-40users_stats.csv"
        if Path(csv_40).exists():
            stats_40 = parse_locust_stats(csv_40)
            report.extend([
                "#### 40 Concurrent Users (At Thread Pool Limit)",
                "",
                f"- **Total Requests**: {stats_40['total_requests']:,}",
                f"- **Failures**: {stats_40['failures']}",
                f"- **RPS**: {stats_40['rps']:.2f}",
                f"- **Avg Response Time**: {stats_40['avg_response_time']:.0f}ms",
                f"- **Min/Max**: {stats_40['min_response_time']:.0f}ms / {stats_40['max_response_time']:.0f}ms",
                "",
                "**Percentiles:**",
                f"- 50th: {stats_40['percentiles']['50']:.0f}ms",
                f"- 95th: {stats_40['percentiles']['95']:.0f}ms",
                f"- 99th: {stats_40['percentiles']['99']:.0f}ms",
                "",
            ])

            # Calculate degradation from 10 users
            if Path(csv_10).exists():
                degradation_10_40 = ((stats_40['avg_response_time'] - stats_10['avg_response_time'])
                              / stats_10['avg_response_time'] * 100)
                report.extend([
                    f"**Performance Change (10→40 users)**: {degradation_10_40:+.1f}%",
                    ""
                ])

        # 100 users
        csv_100 = f"{results_dir}/{route_name}-100users_stats.csv"
        if Path(csv_100).exists():
            stats_100 = parse_locust_stats(csv_100)
            report.extend([
                "#### 100 Concurrent Users (Exceeds Thread Pool Limit)",
                "",
                f"- **Total Requests**: {stats_100['total_requests']:,}",
                f"- **Failures**: {stats_100['failures']}",
                f"- **RPS**: {stats_100['rps']:.2f}",
                f"- **Avg Response Time**: {stats_100['avg_response_time']:.0f}ms",
                f"- **Min/Max**: {stats_100['min_response_time']:.0f}ms / {stats_100['max_response_time']:.0f}ms",
                "",
                "**Percentiles:**",
                f"- 50th: {stats_100['percentiles']['50']:.0f}ms",
                f"- 95th: {stats_100['percentiles']['95']:.0f}ms",
                f"- 99th: {stats_100['percentiles']['99']:.0f}ms",
                "",
            ])

            # Calculate degradation from 10 and 40 users
            if Path(csv_10).exists():
                degradation_10_100 = ((stats_100['avg_response_time'] - stats_10['avg_response_time'])
                              / stats_10['avg_response_time'] * 100)
                report.extend([
                    f"**Performance Change (10→100 users)**: {degradation_10_100:+.1f}%",
                    ""
                ])
            if Path(csv_40).exists():
                degradation_40_100 = ((stats_100['avg_response_time'] - stats_40['avg_response_time'])
                              / stats_40['avg_response_time'] * 100)
                report.extend([
                    f"**Performance Change (40→100 users)**: {degradation_40_100:+.1f}%",
                    ""
                ])

        report.append("---")
        report.append("")

    # Add observations section
    report.extend([
        "## Key Observations",
        "",
        "### Thread Pool Saturation Effects",
        "",
        "- Routes with sync inner functions called from async contexts use the thread pool",
        "- At 40 concurrent users, performance should be stable (within thread pool limit)",
        "- At 100 concurrent users, routes depending on thread pool will show degradation",
        "",
        "### Expected Behaviors",
        "",
        "**Sync routes (def) with sync inner functions**:",
        "- All sync operations run in thread pool",
        "- Significant degradation expected at 100 users",
        "",
        "**Async routes calling sync inner functions**:",
        "- Sync function executed in thread pool via `run_in_executor`",
        "- Moderate degradation at 100 users",
        "",
        "**Async routes with async inner functions**:",
        "- Minimal thread pool usage",
        "- Better performance scaling under high concurrency",
        "- Background task type affects background processing but not request handling",
        "",
        "### HTML Reports",
        "",
        "Detailed HTML reports with charts available at:",
        ""
    ])

    for route_name, _ in routes:
        report.append(f"- {route_name}:")
        report.append(f"  - [10 users](./{route_name}-10users.html)")
        report.append(f"  - [40 users](./{route_name}-40users.html)")
        report.append(f"  - [100 users](./{route_name}-100users.html)")

    # Write report
    output_file = f"{results_dir}/RESULTS.md"
    with open(output_file, 'w') as f:
        f.write('\n'.join(report))

    print(f"Report generated: {output_file}")


if __name__ == "__main__":
    generate_markdown_report()
