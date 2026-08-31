from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from iosislib.core.graph import Graph, GraphValidationError, ValidationReport
from iosislib.core.node import Node
from iosislib.strategy.ir import Strategy
from iosislib.strategy.lowering import LoweredStrategy, OperationRegistry, builtin_registry, lower
from iosislib.strategy.parser import load as load_strategy


def parse_and_lower(yaml_path: str | Path) -> LoweredStrategy:
    """Parse a strategy YAML and lower it to core nodes."""
    strategy = load_strategy(yaml_path)
    registry = builtin_registry()
    return lower(strategy, registry)


def validate_strategy(yaml_path: str | Path) -> bool:
    """Parse, lower, and validate a strategy. Print report. Return True if valid."""
    try:
        lowered = parse_and_lower(yaml_path)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return False

    output_name = next(iter(lowered.outputs))
    graph = lowered.graph(output_name)

    report = Graph.validate(graph.root_node)
    if report.is_valid:
        print("Valid.")
        return True

    print(f"Invalid ({len(report.issues)} issue(s)):", file=sys.stderr)
    for i, issue in enumerate(report.issues, 1):
        parts = [f"  {i}. [{issue.code}] {issue.message}"]
        print("\n".join(parts), file=sys.stderr)
    return False


def print_table(rows: list[list[str]], headers: list[str]) -> None:
    """Print a simple ASCII table."""
    if not rows:
        print("(empty)")
        return

    all_rows = [headers] + rows
    widths = [max(len(row[i]) for row in all_rows) for i in range(len(headers))]

    def fmt_row(row: list[str]) -> str:
        parts = []
        for i, cell in enumerate(row):
            parts.append(cell.ljust(widths[i]))
        return "  ".join(parts)

    print(fmt_row(headers))
    print("  ".join("-" * w for w in widths))
    for row in rows:
        print(fmt_row(row))
