#!/usr/bin/env python
"""
Dorama Studio - Triple Agent Orchestration CLI
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from dorama_studio.orchestration.orchestrator import TripleOrchestrator


def main():
    parser = argparse.ArgumentParser(
        description="Dorama Studio - Triple Agent Orchestration System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m dorama_studio.orchestration.cli "Improve the prompt compiler"
  python -m dorama_studio.orchestration.cli "Analyze and fix the video animator agent" --verbose
  python -m dorama_studio.orchestration.cli "Run benchmark on prompt compiler" --benchmark
        """,
    )

    parser.add_argument("task", nargs="*", help="Task description")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument(
        "--benchmark", action="store_true", help="Run benchmarks after execution"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Show plan without executing"
    )
    parser.add_argument("--config", help="Path to orchestration config")
    parser.add_argument("--output", "-o", help="Output file for results")

    args = parser.parse_args()

    if not args.task:
        parser.print_help()
        return 1

    task = " ".join(args.task)

    async def run():

        orchestrator = TripleOrchestrator()

        print("🚀 Starting Triple Agent Orchestration")
        print(f"Task: {task}")
        print("=" * 50)

        try:
            result = await orchestrator.run_task({"description": task})

            print("\n" + "=" * 50)
            print("📊 EXECUTION RESULTS")
            print("=" * 50)
            print(json.dumps(result, indent=2, ensure_ascii=False))

            return 0 if result.get("status") == "completed" else 1

        except Exception as e:
            print(f"❌ Error: {e}")
            return 1

    return asyncio.run(run())


if __name__ == "__main__":
    sys.exit(main())
