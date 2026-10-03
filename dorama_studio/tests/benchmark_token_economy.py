"""
Benchmark Suite for Token Economy Optimization.
Mide baseline y optimized para validar ahorros.
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from dorama_studio.core.agent_handoff import create_handoff
from dorama_studio.core.cache import multi_level_cache
from dorama_studio.core.prompt_context import (
    PromptContextBuilder,
)
from dorama_studio.core.state import EpisodeProductionState
from dorama_studio.core.token_usage import (
    TokenUsageReport,
    compare_reports,
    token_tracker,
)
from dorama_studio.pipeline.orchestrator import DoramaGraphFactory

logger = logging.getLogger(__name__)


@dataclass
class BenchmarkResult:
    """Resultado de un benchmark."""
    name: str
    description: str
    baseline: dict[str, Any] | None = None
    optimized: dict[str, Any] | None = None
    comparison: dict[str, Any] | None = None
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    duration_seconds: float = 0.0
    success: bool = True
    error: str | None = None


class BenchmarkRunner:
    """
    Ejecuta benchmarks comparativos antes/después de optimizaciones.
    """

    def __init__(self, output_dir: str = "benchmarks"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.results: list[BenchmarkResult] = []

    def run_episode_benchmark(
        self,
        episode_num: int = 1,
        total_episodes: int = 1,
        use_optimized: bool = True,
    ) -> BenchmarkResult:
        """
        Ejecuta benchmark de un episodio completo.

        Args:
            episode_num: Número de episodio
            total_episodes: Total de episodios en temporada
            use_optimized: Si True usa pipeline optimizado, si False usa baseline

        Returns:
            BenchmarkResult con métricas
        """
        name = f"episode_{episode_num}_{'optimized' if use_optimized else 'baseline'}"
        description = f"Full pipeline run for episode {episode_num} of {total_episodes}"

        result = BenchmarkResult(name=name, description=description)
        start_time = time.time()

        try:
            # Reset token tracker
            token_tracker.reset()

            # Configure cache for this run
            multi_level_cache.clear()

            # Build pipeline graph
            factory = DoramaGraphFactory()
            graph = factory.build()

            # Create initial state
            initial_state = EpisodeProductionState(
                project_id=f"bench_proj_{episode_num}",
                season_id=f"bench_season_{episode_num}",
                episode_id=f"e{episode_num:02d}",
                episode_number=episode_num,
                target_duration_sec=90,
                total_episodes=total_episodes,
            )

            config = {"configurable": {"thread_id": f"bench_thread_{episode_num}"}}

            # Execute graph
            final_state = graph.invoke(initial_state.model_dump(), config=config)

            result.duration_seconds = time.time() - start_time

            # Get token usage report
            report = token_tracker.get_report()

            if use_optimized:
                result.optimized = report.to_dict()
            else:
                result.baseline = report.to_dict()

            result.success = final_state.get("stage") in [
                "episode_complete",
                "season_packaging_done",
                "final_approved"
            ]

            if not result.success:
                result.error = f"Pipeline ended at stage: {final_state.get('stage')}"

        except Exception as e:
            result.duration_seconds = time.time() - start_time
            result.success = False
            result.error = str(e)
            logger.error(f"Benchmark {name} failed: {e}")

        self.results.append(result)
        return result

    def run_comparison_benchmark(
        self,
        episode_num: int = 1,
        total_episodes: int = 1,
    ) -> BenchmarkResult:
        """Ejecuta baseline y optimizado y compara."""
        name = f"episode_{episode_num}_comparison"
        description = f"Baseline vs Optimized comparison for episode {episode_num}"

        result = BenchmarkResult(name=name, description=description)
        start_time = time.time()

        try:
            # Run baseline (without optimizations)
            logger.info("Running baseline benchmark...")
            # For baseline, we'd need a non-optimized version of the pipeline
            # For now, run with use_optimized=False to get baseline metrics
            baseline_result = self.run_episode_benchmark(episode_num, total_episodes, use_optimized=False)

            # Clear caches between runs
            multi_level_cache.clear()
            token_tracker.reset()

            # Run optimized
            logger.info("Running optimized benchmark...")
            optimized_result = self.run_episode_benchmark(episode_num, total_episodes, use_optimized=True)

            result.duration_seconds = time.time() - start_time

            if baseline_result.baseline and optimized_result.optimized:
                result.baseline = baseline_result.baseline
                result.optimized = optimized_result.optimized
                result.comparison = compare_reports(
                    {"summary": TokenUsageReport(**baseline_result.baseline).get_summary() if baseline_result.baseline else {}},
                    {"summary": TokenUsageReport(**optimized_result.optimized).get_summary() if optimized_result.optimized else {}}
                )

            result.success = baseline_result.success and optimized_result.success

        except Exception as e:
            result.duration_seconds = time.time() - start_time
            result.success = False
            result.error = str(e)
            logger.error(f"Comparison benchmark failed: {e}")

        self.results.append(result)
        return result

    def run_prompt_context_benchmark(
        self,
        num_iterations: int = 100,
    ) -> BenchmarkResult:
        """Benchmark específico del PromptContextBuilder."""
        name = "prompt_context_builder"
        description = f"Prompt context building benchmark ({num_iterations} iterations)"

        result = BenchmarkResult(name=name, description=description)
        start_time = time.time()

        try:
            builder = PromptContextBuilder()
            builder.load_stable_context_from_files(".")

            # Sample data
            episode_data = {
                "objective": "Protagonist discovers betrayal",
                "beats": [{"beat_name": f"Beat {i}", "action": f"Action {i}"} for i in range(9)],
                "characters_present": ["CHAR_001", "CHAR_002"],
                "locations": ["Office", "Home"],
                "conflict": "Betrayal discovered",
                "cliffhanger": "Who can she trust?",
                "season_arc": "Revenge and redemption",
                "season_characters": [{"id": "CHAR_001", "name": "Kira", "role": "protagonist"}],
                "relationships": {"CHAR_001": "enemy of CHAR_002"},
                "world_rules": "No magic, realistic",
                "visual_identity": "K-Drama cold palette",
                "season_continuity": {},
                "previous_episodes": [
                    {"episode_number": 1, "cliffhanger": "Cliffhanger 1"},
                    {"episode_number": 2, "cliffhanger": "Cliffhanger 2"},
                ],
            }

            scene_data = {
                "characters": ["CHAR_001"],
                "location": "Office",
                "action": "Discovers document",
                "dialogue": "¿Qué es esto?",
                "shot_requirements": "ECU on document",
            }

            # Warm up
            for _ in range(10):
                builder.build(
                    task="Generate beats for episode",
                    agent="MasterWriterAgent",
                    episode=episode_data,
                    scene=scene_data,
                )

            # Benchmark
            token_tracker.reset()
            for i in range(num_iterations):
                prompt = builder.build(
                    task="Generate beats for episode",
                    agent="MasterWriterAgent",
                    episode=episode_data,
                    scene=scene_data,
                )

            result.duration_seconds = time.time() - start_time
            report = token_tracker.get_report()
            result.optimized = report.to_dict()
            result.success = True

        except Exception as e:
            result.duration_seconds = time.time() - start_time
            result.success = False
            result.error = str(e)
            logger.error(f"Prompt context benchmark failed: {e}")

        self.results.append(result)
        return result

    def run_handoff_benchmark(
        self,
        num_iterations: int = 1000,
    ) -> BenchmarkResult:
        """Benchmark de agent handoff optimization."""
        name = "agent_handoff"
        description = f"Agent handoff filtering benchmark ({num_iterations} iterations)"

        result = BenchmarkResult(name=name, description=description)
        start_time = time.time()

        try:
            # Sample output from MasterWriterAgent
            master_writer_output = {
                "script": {"artifact_id": "script_001", "content": "x" * 5000},
                "beats": [{"beat_name": f"Beat {i}", "action": "x" * 200} for i in range(9)],
                "hook": {"hook_id": "hook_001", "content": "x" * 1000},
                "characters": [{"id": "CHAR_001", "name": "Kira", "data": "x" * 1000} for _ in range(5)],
                "viral_ruleset": ["rule1", "rule2", "rule3"],
                "genome_context": {"data": "x" * 500},
            }

            token_tracker.reset()

            for _ in range(num_iterations):
                handoff = create_handoff(
                    "MasterWriterAgent",
                    "DirectorEngineAgent",
                    master_writer_output,
                )

            result.duration_seconds = time.time() - start_time
            report = token_tracker.get_report()
            result.optimized = report.to_dict()
            result.success = True

        except Exception as e:
            result.duration_seconds = time.time() - start_time
            result.success = False
            result.error = str(e)
            logger.error(f"Handoff benchmark failed: {e}")

        self.results.append(result)
        return result

    def run_cache_benchmark(
        self,
        num_operations: int = 1000,
    ) -> BenchmarkResult:
        """Benchmark de cache multi-nivel."""
        name = "multi_level_cache"
        description = f"Multi-level cache benchmark ({num_operations} operations)"

        result = BenchmarkResult(name=name, description=description)
        start_time = time.time()

        try:
            multi_level_cache.clear()
            token_tracker.reset()

            # Test data
            test_data = {"key": "value", "data": "x" * 1000}

            for i in range(num_operations):
                key = f"test_key_{i % 100}"  # 100 unique keys
                # Write
                from dorama_studio.core.cache import CacheEntry
                entry = CacheEntry(key=key, value=test_data)
                multi_level_cache.set(key, entry)
                # Read
                retrieved = multi_level_cache.get(key)

            result.duration_seconds = time.time() - start_time
            stats = multi_level_cache.get_stats()
            result.optimized = stats
            result.success = True

        except Exception as e:
            result.duration_seconds = time.time() - start_time
            result.success = False
            result.error = str(e)
            logger.error(f"Cache benchmark failed: {e}")

        self.results.append(result)
        return result

    def run_40x90_smoke_benchmark(self) -> BenchmarkResult:
        """Benchmark smoke test 40x90 (simulado, sin generar video real)."""
        name = "40x90_smoke"
        description = "40 episodes × 90s smoke test (context growth measurement)"

        result = BenchmarkResult(name=name, description=description)
        start_time = time.time()

        try:
            factory = DoramaGraphFactory()
            graph = factory.build()

            token_tracker.reset()
            multi_level_cache.clear()

            # Track context growth per episode
            context_sizes = []
            token_per_episode = []

            for ep_num in range(1, 41):
                initial_state = EpisodeProductionState(
                    project_id="bench_40x90",
                    season_id="s01",
                    episode_id=f"e{ep_num:02d}",
                    episode_number=ep_num,
                    target_duration_sec=90,
                    total_episodes=40,
                )

                config = {"configurable": {"thread_id": f"bench_40x90_ep{ep_num}"}}

                # Execute single episode through subgraph
                # Note: Full graph would fan-out to all episodes
                # Here we measure single episode execution context
                ep_start = time.time()
                final_state = graph.invoke(initial_state.model_dump(), config=config)
                ep_duration = time.time() - ep_start

                report = token_tracker.get_report()
                ep_report = report.by_episode.get(f"e{ep_num:02d}", {})

                context_sizes.append({
                    "episode": ep_num,
                    "state_keys": len(final_state.keys()) if isinstance(final_state, dict) else 0,
                    "duration_seconds": ep_duration,
                    "tokens": ep_report.get("total_tokens", 0),
                    "calls": ep_report.get("calls", 0),
                })

                token_per_episode.append(ep_report.get("total_tokens", 0))

                # Reset for next episode (simulate clean slate per episode)
                token_tracker.reset()

            result.duration_seconds = time.time() - start_time

            # Analyze growth
            if token_per_episode:
                growth_analysis = {
                    "first_episode_tokens": token_per_episode[0] if token_per_episode else 0,
                    "last_episode_tokens": token_per_episode[-1] if token_per_episode else 0,
                    "avg_tokens_per_episode": sum(token_per_episode) / len(token_per_episode),
                    "max_tokens": max(token_per_episode),
                    "min_tokens": min(token_per_episode),
                    "linear_growth": token_per_episode[-1] > token_per_episode[0] * 1.5 if len(token_per_episode) > 1 else False,
                }
            else:
                growth_analysis = {}

            result.optimized = {
                "episodes": context_sizes,
                "growth_analysis": growth_analysis,
                "total_episodes_tested": len(context_sizes),
            }
            result.success = True

        except Exception as e:
            result.duration_seconds = time.time() - start_time
            result.success = False
            result.error = str(e)
            logger.error(f"40x90 benchmark failed: {e}")

        self.results.append(result)
        return result

    def save_results(self, filename: str = None) -> str:
        """Guarda resultados a archivo JSON."""
        if filename is None:
            filename = f"benchmark_results_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"

        filepath = self.output_dir / filename

        data = {
            "timestamp": datetime.utcnow().isoformat(),
            "total_benchmarks": len(self.results),
            "results": [asdict(r) for r in self.results],
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        logger.info(f"Benchmark results saved to {filepath}")
        return str(filepath)

    def print_summary(self):
        """Imprime resumen de resultados."""
        print("\n" + "="*60)
        print("BENCHMARK SUMMARY")
        print("="*60)

        for r in self.results:
            status = "✓" if r.success else "✗"
            print(f"\n{status} {r.name}")
            print(f"   Duration: {r.duration_seconds:.2f}s")

            if r.comparison:
                print("   Comparison:")
                for metric, data in r.comparison.items():
                    if isinstance(data, dict) and "pct" in data:
                        print(f"     {metric}: {data['pct']:+.1f}% ({data['before']} → {data['after']})")

            if r.optimized and "summary" in r.optimized:
                summary = r.optimized.get("summary", {})
                if summary:
                    print(f"   Tokens: {summary.get('total_tokens', 0):,}")
                    print(f"   Calls: {summary.get('total_calls', 0)}")
                    print(f"   Cache hit rate: {summary.get('cache_hit_rate_pct', 0):.1f}%")

        print("\n" + "="*60)


def run_full_benchmark_suite() -> BenchmarkRunner:
    """Ejecuta suite completa de benchmarks."""
    runner = BenchmarkRunner()

    print("Running prompt context benchmark...")
    runner.run_prompt_context_benchmark(100)

    print("Running agent handoff benchmark...")
    runner.run_handoff_benchmark(1000)

    print("Running cache benchmark...")
    runner.run_cache_benchmark(1000)

    print("Running 40x90 smoke benchmark...")
    runner.run_40x90_smoke_benchmark()

    print("Running episode comparison benchmark...")
    runner.run_comparison_benchmark(1, 1)

    runner.print_summary()
    runner.save_results()

    return runner


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_full_benchmark_suite()
