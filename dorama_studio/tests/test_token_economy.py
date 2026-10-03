"""
Tests for Token Economy Optimization components.
"""


import pytest

from dorama_studio.core.agent_handoff import (
    AgentHandoffSchema,
    HandoffField,
    HandoffFieldType,
    HandoffRegistry,
    create_handoff,
    handoff_registry,
    validate_handoff,
)
from dorama_studio.core.cache import (
    CacheEntry,
    CacheKey,
    DiskCacheBackend,
    IdempotencyManager,
    MemoryCacheBackend,
    MultiLevelCache,
    create_dynamic_context_hash,
    create_stable_context_hash,
    create_task_hash,
    multi_level_cache,
)
from dorama_studio.core.prompt_context import (
    CompressedContinuity,
    ContextBudget,
    ContextLevel,
    DynamicContext,
    PromptContextBuilder,
    StableContext,
    TaskContext,
    build_minimal_prompt,
)
from dorama_studio.core.token_usage import (
    TokenEstimationMethod,
    TokenTracker,
    TokenUsage,
    TokenUsageReport,
    compare_reports,
    create_baseline_report,
    estimate_tokens,
)


class TestTokenUsage:
    """Tests for TokenUsage tracking."""

    def test_token_usage_creation(self):
        usage = TokenUsage(
            input_tokens=1000,
            output_tokens=500,
            total_tokens=1500,
            estimated=True,
            estimation_method=TokenEstimationMethod.CHAR_BASED,
            model="claude-opus-4-5",
            provider="freellmapi",
            agent="MasterWriterAgent",
            operation="generate_script",
        )
        assert usage.input_tokens == 1000
        assert usage.output_tokens == 500
        assert usage.total_tokens == 1500
        assert usage.estimated is True

    def test_token_usage_to_dict(self):
        usage = TokenUsage(
            input_tokens=1000,
            output_tokens=500,
            total_tokens=1500,
            estimated=True,
            estimation_method=TokenEstimationMethod.CHAR_BASED,
            model="claude-opus-4-5",
            provider="freellmapi",
            agent="MasterWriterAgent",
            operation="generate_script",
        )
        d = usage.to_dict()
        assert d["input_tokens"] == 1000
        assert d["agent"] == "MasterWriterAgent"

    def test_token_usage_report_aggregation(self):
        report = TokenUsageReport(
            period_start="2024-01-01T00:00:00",
            period_end="2024-01-01T01:00:00"
        )

        usage1 = TokenUsage(
            input_tokens=1000, output_tokens=500, total_tokens=1500,
            estimated=True, estimation_method=TokenEstimationMethod.CHAR_BASED,
            model="claude-opus-4-5", provider="freellmapi",
            agent="MasterWriterAgent", operation="generate_script",
        )
        usage2 = TokenUsage(
            input_tokens=2000, output_tokens=1000, total_tokens=3000,
            estimated=False, estimation_method=TokenEstimationMethod.EXACT,
            model="claude-sonnet-4-5", provider="freellmapi",
            agent="HookEngineAgent", operation="generate_hooks",
            cache_hit=True,
        )

        report.add_usage(usage1)
        report.add_usage(usage2)

        assert report.total_calls == 2
        assert report.total_input_tokens == 3000
        assert report.total_output_tokens == 1500
        assert report.total_tokens == 4500
        assert report.cache_hits == 1
        assert report.cache_misses == 1
        assert "MasterWriterAgent" in report.by_agent
        assert "HookEngineAgent" in report.by_agent

    def test_token_usage_report_summary(self):
        report = TokenUsageReport(
            period_start="2024-01-01T00:00:00",
            period_end="2024-01-01T01:00:00"
        )
        usage = TokenUsage(
            input_tokens=1000, output_tokens=500, total_tokens=1500,
            estimated=True, estimation_method=TokenEstimationMethod.CHAR_BASED,
            model="claude-opus-4-5", provider="freellmapi",
            agent="MasterWriterAgent", operation="generate_script",
            latency_ms=1000,
        )
        report.add_usage(usage)

        summary = report.get_summary()
        assert summary["total_calls"] == 1
        assert summary["total_tokens"] == 1500
        assert summary["avg_latency_ms"] == 1000

    def test_estimate_tokens_char_based(self):
        text = "a" * 400  # ~100 tokens
        tokens = estimate_tokens(text, TokenEstimationMethod.CHAR_BASED)
        assert tokens == 100

    def test_estimate_tokens_word_based(self):
        text = " ".join(["word"] * 100)  # 100 words ~ 133 tokens
        tokens = estimate_tokens(text, TokenEstimationMethod.WORD_BASED)
        assert tokens == 133  # 100 / 0.75

    def test_token_tracker_singleton(self):
        tracker1 = TokenTracker()
        tracker2 = TokenTracker()
        assert tracker1 is tracker2

    def test_token_tracker_record_and_get(self):
        tracker = TokenTracker()
        tracker.reset()

        usage = TokenUsage(
            input_tokens=1000, output_tokens=500, total_tokens=1500,
            estimated=True, estimation_method=TokenEstimationMethod.CHAR_BASED,
            model="claude-opus-4-5", provider="freellmapi",
            agent="TestAgent", operation="test_op",
        )
        tracker.record(usage)

        report = tracker.get_report()
        assert report.total_calls == 1
        assert report.total_tokens == 1500

    def test_token_tracker_filter(self):
        tracker = TokenTracker()
        tracker.reset()

        usage1 = TokenUsage(
            input_tokens=1000, output_tokens=500, total_tokens=1500,
            estimated=True, estimation_method=TokenEstimationMethod.CHAR_BASED,
            model="claude-opus-4-5", provider="freellmapi",
            agent="AgentA", operation="op1", episode_id="ep1",
        )
        usage2 = TokenUsage(
            input_tokens=2000, output_tokens=1000, total_tokens=3000,
            estimated=True, estimation_method=TokenEstimationMethod.CHAR_BASED,
            model="claude-opus-4-5", provider="freellmapi",
            agent="AgentB", operation="op2", episode_id="ep2",
        )
        tracker.record(usage1)
        tracker.record(usage2)

        # Filter by agent
        results = tracker.get_usages(agent="AgentA")
        assert len(results) == 1
        assert results[0].agent == "AgentA"

        # Filter by episode
        results = tracker.get_usages(episode_id="ep2")
        assert len(results) == 1
        assert results[0].episode_id == "ep2"

    def test_create_baseline_report(self):
        tracker = TokenTracker()
        tracker.reset()
        usage = TokenUsage(
            input_tokens=1000, output_tokens=500, total_tokens=1500,
            estimated=True, estimation_method=TokenEstimationMethod.CHAR_BASED,
            model="claude-opus-4-5", provider="freellmapi",
            agent="TestAgent", operation="test_op",
        )
        tracker.record(usage)

        baseline = create_baseline_report()
        assert "baseline_timestamp" in baseline
        assert "summary" in baseline
        assert baseline["summary"]["total_tokens"] == 1500

    def test_compare_reports(self):
        baseline = {"summary": {"total_tokens": 10000, "total_calls": 10, "input_tokens": 6000, "output_tokens": 4000, "avg_latency_ms": 1000, "cache_hit_rate_pct": 0}}
        optimized = {"summary": {"total_tokens": 5000, "total_calls": 5, "input_tokens": 3000, "output_tokens": 2000, "avg_latency_ms": 500, "cache_hit_rate_pct": 50}}

        comparison = compare_reports(baseline, optimized)
        assert comparison["total_tokens"]["pct"] == 50.0
        assert comparison["llm_calls"]["pct"] == 50.0
        assert comparison["cache_hit_rate_change"] == 50.0


class TestPromptContextBuilder:
    """Tests for PromptContextBuilder."""

    def test_context_budget_defaults(self):
        budget = ContextBudget()
        assert budget.max_global_tokens == 2000
        assert budget.max_season_tokens == 1500
        assert budget.max_episode_tokens == 2000
        assert budget.max_scene_tokens == 1500
        assert budget.max_task_tokens == 1000
        assert budget.max_total_tokens == 7000

    def test_context_budget_validation(self):
        budget = ContextBudget()
        level_tokens = {
            ContextLevel.GLOBAL: 1000,
            ContextLevel.SEASON: 1000,
            ContextLevel.EPISODE: 1000,
            ContextLevel.SCENE: 1000,
            ContextLevel.TASK: 500,
        }
        assert budget.validate_total(level_tokens) is True

        level_tokens[ContextLevel.GLOBAL] = 5000
        assert budget.validate_total(level_tokens) is False

    def test_stable_context_hash(self):
        stable = StableContext(
            system_rules="Rule 1",
            architecture_docs="Arch 1",
            global_style="Style 1",
            contracts="Contract 1",
            permanent_instructions="Instr 1",
        )
        hash1 = stable.compute_hash()
        hash2 = stable.compute_hash()
        assert hash1 == hash2
        assert len(hash1) == 16

    def test_stable_context_cache_key(self):
        stable = StableContext(system_rules="Rule 1")
        stable.compute_hash()
        key = stable.get_cache_key()
        assert key.startswith("stable_ctx_")

    def test_dynamic_context_to_prompt(self):
        dyn = DynamicContext(
            season_arc="Revenge arc",
            main_characters=[{"id": "CHAR_001", "name": "Kira", "role": "protagonist"}],
            episode_objective="Discover betrayal",
            episode_beats=[{"beat_name": "Hook", "action": "Finds letter"}],
        )
        prompt = dyn.to_prompt_block(include_season=True, include_episode=True)
        assert "SEASON ARC" in prompt
        assert "EPISODE OBJECTIVE" in prompt
        assert "Kira" in prompt

    def test_task_context_to_prompt(self):
        task = TaskContext(
            agent_name="TestAgent",
            task_description="Generate something",
            constraints=["Constraint 1", "Constraint 2"],
            output_schema='{"type": "object"}',
            required_fields=["field1", "field2"],
        )
        prompt = task.to_prompt_block()
        assert "TASK" in prompt
        assert "CONSTRAINTS" in prompt
        assert "Constraint 1" in prompt
        assert "OUTPUT SCHEMA" in prompt

    def test_compressed_continuity(self):
        cc = CompressedContinuity(
            facts=["Fact 1", "Fact 2"],
            unresolved_threads=["Thread 1"],
            character_changes={"CHAR_001": "Now angry"},
        )
        prompt = cc.to_prompt_block()
        assert "KEY FACTS" in prompt
        assert "UNRESOLVED THREADS" in prompt
        assert "CHARACTER CHANGES" in prompt
        assert "CHAR_001" in prompt

    def test_compressed_continuity_from_episode(self):
        episode_data = {
            "beats": [
                {"beat_name": "Hook", "action": "Finds letter"},
                {"beat_name": "Context", "action": "Reads letter"},
            ],
        }
        previous = [
            {"episode_number": 1, "cliffhanger": "Letter arrives"},
        ]
        cc = CompressedContinuity.from_episode_state(episode_data, previous)
        assert len(cc.recent_events) > 0
        assert len(cc.unresolved_threads) > 0

    def test_prompt_context_builder_build(self):
        builder = PromptContextBuilder()
        builder.load_stable_context_from_files(".")

        episode_data = {
            "objective": "Test objective",
            "beats": [{"beat_name": "Hook", "action": "Action"}],
            "characters_present": ["CHAR_001"],
            "season_arc": "Test arc",
        }

        prompt = builder.build(
            task="Generate beats",
            agent="TestAgent",
            episode=episode_data,
        )

        assert "TASK" in prompt
        assert "Generate beats" in prompt

    def test_prompt_context_builder_budget(self):
        builder = PromptContextBuilder(ContextBudget(max_total_tokens=100))
        # Don't load from files to keep stable context small
        builder.set_stable_context(StableContext(
            system_rules="Rule 1",
            architecture_docs="Arch 1",
        ))

        # Use small episode data
        episode_data = {"objective": "Small test objective"}

        prompt = builder.build(
            task="Test",
            agent="TestAgent",
            episode=episode_data,
        )

        stats = builder.get_context_stats(prompt)
        # Should be within budget (approximately)
        assert stats["estimated_tokens"] <= 200  # Some tolerance

    def test_build_minimal_prompt(self):
        prompt = build_minimal_prompt(
            agent="TestAgent",
            task="Generate something",
            schema='{"type": "object"}',
            budget_override=500,
        )
        assert "Generate something" in prompt
        assert "OUTPUT SCHEMA" in prompt


class TestAgentHandoff:
    """Tests for Agent Handoff Optimization."""

    def test_handoff_field_creation(self):
        field = HandoffField(
            name="test_field",
            field_type=HandoffFieldType.REQUIRED,
            description="Test field",
            source_agent="AgentA",
            target_agents=["AgentB", "AgentC"],
            schema_type="dict",
            compression_hint="ids_only",
        )
        assert field.name == "test_field"
        assert field.field_type == HandoffFieldType.REQUIRED
        assert "AgentB" in field.target_agents

    def test_agent_handoff_schema(self):
        schema = AgentHandoffSchema(
            agent_name="TestAgent",
            inputs=[
                HandoffField("input1", HandoffFieldType.REQUIRED, source_agent="OtherAgent", target_agents=["TestAgent"]),
                HandoffField("input2", HandoffFieldType.OPTIONAL, source_agent="OtherAgent", target_agents=["TestAgent"]),
            ],
            outputs=[
                HandoffField("output1", HandoffFieldType.REQUIRED, source_agent="TestAgent", target_agents=["NextAgent"]),
            ]
        )

        assert schema.get_required_input_names() == ["input1"]
        assert schema.get_optional_input_names() == ["input2"]
        assert schema.get_output_names() == ["output1"]
        next_agent_fields = schema.get_fields_for_target("NextAgent")
        assert len(next_agent_fields) == 1
        assert next_agent_fields[0].name == "output1"

    def test_agent_handoff_schema_validate_input(self):
        schema = AgentHandoffSchema(
            agent_name="TestAgent",
            inputs=[
                HandoffField("required_field", HandoffFieldType.REQUIRED, source_agent="A", target_agents=["TestAgent"]),
                HandoffField("optional_field", HandoffFieldType.OPTIONAL, source_agent="A", target_agents=["TestAgent"]),
            ],
        )

        # Missing required
        missing = schema.validate_input({"optional_field": "value"})
        assert "required_field" in missing

        # All present
        missing = schema.validate_input({"required_field": "value", "optional_field": "value"})
        assert len(missing) == 0

    def test_agent_handoff_schema_filter_output(self):
        schema = AgentHandoffSchema(
            agent_name="SourceAgent",
            outputs=[
                HandoffField("field_for_target", HandoffFieldType.REQUIRED, source_agent="SourceAgent", target_agents=["TargetAgent"]),
                HandoffField("field_for_other", HandoffFieldType.REQUIRED, source_agent="SourceAgent", target_agents=["OtherAgent"]),
                HandoffField("field_no_target", HandoffFieldType.REQUIRED, source_agent="SourceAgent", target_agents=[]),
            ]
        )

        output_data = {
            "field_for_target": "value1",
            "field_for_other": "value2",
            "field_no_target": "value3",
        }

        filtered = schema.filter_output_for_target(output_data, "TargetAgent")
        assert "field_for_target" in filtered
        assert "field_for_other" not in filtered
        assert "field_no_target" not in filtered

    def test_compression_hints(self):
        schema = AgentHandoffSchema(
            agent_name="SourceAgent",
            outputs=[
                HandoffField("list_of_objects", HandoffFieldType.REQUIRED, source_agent="SourceAgent", target_agents=["TargetAgent"], compression_hint="ids_only"),
                HandoffField("long_string", HandoffFieldType.REQUIRED, source_agent="SourceAgent", target_agents=["TargetAgent"], compression_hint="summary", max_size_chars=10),
                HandoffField("dict_data", HandoffFieldType.REQUIRED, source_agent="SourceAgent", target_agents=["TargetAgent"], compression_hint="keys_only"),
            ]
        )

        output_data = {
            "list_of_objects": [{"id": "1", "data": "x"}, {"id": "2", "data": "y"}],
            "long_string": "This is a very long string that should be truncated",
            "dict_data": {"key1": "val1", "key2": "val2"},
        }

        filtered = schema.filter_output_for_target(output_data, "TargetAgent")
        assert filtered["list_of_objects"] == ["1", "2"]
        assert filtered["long_string"].endswith("[truncated]")
        assert filtered["dict_data"] == ["key1", "key2"]

    def test_handoff_registry(self):
        registry = HandoffRegistry()
        schema = registry.get_schema("MasterWriterAgent")
        assert schema is not None
        assert schema.agent_name == "MasterWriterAgent"
        assert len(schema.inputs) > 0
        assert len(schema.outputs) > 0

    def test_handoff_registry_filter(self):
        output = {
            "script": {"artifact_id": "script_001", "content": "x" * 1000},
            "beats": [{"beat_name": f"Beat {i}"} for i in range(9)],
            "hook": {"hook_id": "hook_001"},
            "characters": [{"id": "CHAR_001"}] * 5,
        }

        filtered = handoff_registry.filter_output_for_next_agent(
            "MasterWriterAgent", "DirectorEngineAgent", output
        )

        # Should only contain fields DirectorEngineAgent needs
        assert "script" in filtered or "beats" in filtered
        assert "hook" not in filtered  # Not needed by DirectorEngineAgent

    def test_handoff_registry_validate(self):
        missing = handoff_registry.validate_agent_input("MasterWriterAgent", {
            "blueprint": {},
            "hook": {},
            "characters": [],
        })
        # viral_ruleset is optional, genome_context is optional
        assert len(missing) == 0

        missing = handoff_registry.validate_agent_input("MasterWriterAgent", {})
        assert "blueprint" in missing
        assert "hook" in missing
        assert "characters" in missing

    def test_create_handoff_function(self):
        output = {
            "script": {"artifact_id": "script_001"},
            "beats": [{"beat_name": "Hook"}],
        }

        handoff = create_handoff("MasterWriterAgent", "DirectorEngineAgent", output)
        assert isinstance(handoff, dict)

    def test_validate_handoff_function(self):
        missing = validate_handoff("MasterWriterAgent", {"blueprint": {}, "hook": {}, "characters": []})
        assert len(missing) == 0


class TestCache:
    """Tests for Caching and Idempotency."""

    def test_cache_entry(self):
        entry = CacheEntry(key="test_key", value="test_value")
        assert entry.key == "test_key"
        assert entry.value == "test_value"
        assert entry.access_count == 0

        entry.touch()
        assert entry.access_count == 1

    def test_cache_entry_expiry(self):
        entry = CacheEntry(key="test_key", value="test_value", created_at=time.time() - 100)
        assert entry.is_expired(50) is True
        assert entry.is_expired(200) is False

    def test_cache_key_creation(self):
        key = CacheKey.from_components(
            stable_context={"rules": "rule1"},
            dynamic_context={"episode": "ep1"},
            task={"task": "generate"},
            prompt_version="1.0",
            model="claude-opus-4-5",
            provider="freellmapi",
            agent="TestAgent",
            operation="test_op",
        )

        key_str = key.to_string()
        assert "claude-opus-4-5" in key_str
        assert "freellmapi" in key_str
        assert "TestAgent" in key_str
        assert "test_op" in key_str

    def test_memory_cache_backend(self):
        cache = MemoryCacheBackend(max_entries=100)

        entry = CacheEntry(key="key1", value="value1")
        cache.set("key1", entry)

        retrieved = cache.get("key1")
        assert retrieved is not None
        assert retrieved.value == "value1"
        assert retrieved.access_count == 1

        # Miss
        retrieved = cache.get("nonexistent")
        assert retrieved is None

        stats = cache.get_stats()
        assert stats["hits"] == 1
        assert stats["misses"] == 1
        assert stats["entries"] == 1

    def test_memory_cache_eviction(self):
        cache = MemoryCacheBackend(max_entries=2)

        cache.set("key1", CacheEntry(key="key1", value="value1"))
        cache.set("key2", CacheEntry(key="key2", value="value2"))
        cache.set("key3", CacheEntry(key="key3", value="value3"))  # Should evict key1

        assert cache.get("key1") is None  # Evicted
        assert cache.get("key2") is not None
        assert cache.get("key3") is not None

    def test_disk_cache_backend(self, tmp_path):
        cache = DiskCacheBackend(cache_dir=str(tmp_path / "cache"), max_entries=100)

        entry = CacheEntry(key="key1", value="value1")
        cache.set("key1", entry)

        retrieved = cache.get("key1")
        assert retrieved is not None
        assert retrieved.value == "value1"

        stats = cache.get_stats()
        assert stats["entries"] == 1

    def test_multi_level_cache(self):
        cache = MultiLevelCache()

        entry = CacheEntry(key="key1", value="value1")
        cache.set("key1", entry)

        # Should be in L1
        retrieved = cache.get("key1")
        assert retrieved is not None
        assert retrieved.value == "value1"

        # Clear L1, should still be in L2
        cache.l1.clear()
        retrieved = cache.get("key1")
        assert retrieved is not None
        assert retrieved.value == "value1"

    def test_multi_level_cache_invalidate_dependencies(self):
        cache = MultiLevelCache()

        entry1 = CacheEntry(key="key1", value="value1", dependencies=["dep1"])
        entry2 = CacheEntry(key="key2", value="value2", dependencies=["dep2"])
        entry3 = CacheEntry(key="key3", value="value3", dependencies=["dep1"])

        cache.set("key1", entry1)
        cache.set("key2", entry2)
        cache.set("key3", entry3)

        count = cache.invalidate_dependencies("dep1")
        # Each entry exists in both L1 and L2, so count is 4 (2 entries × 2 levels)
        assert count == 4

        assert cache.get("key1") is None
        assert cache.get("key3") is None
        assert cache.get("key2") is not None

    def test_idempotency_manager(self):
        multi_level_cache.clear()
        manager = IdempotencyManager()

        call_count = 0

        def compute():
            nonlocal call_count
            call_count += 1
            return f"result_{call_count}"

        key = "test_key_123"

        # First call - should compute
        result1, hit1 = manager.check_and_store(key, compute)
        assert hit1 is False
        assert result1 == "result_1"
        assert call_count == 1

        # Second call - should hit cache
        result2, hit2 = manager.check_and_store(key, compute)
        assert hit2 is True
        assert result2 == "result_1"
        assert call_count == 1  # Not incremented

    def test_idempotency_manager_generate_key(self):
        manager = IdempotencyManager()

        key = manager.generate_key(
            agent="TestAgent",
            operation="test_op",
            stable_context={"rules": "r1"},
            dynamic_context={"ep": "ep1"},
            task_input={"task": "generate"},
            model="claude-opus-4-5",
            provider="freellmapi",
            prompt_version="1.0",
        )

        assert "TestAgent" in key
        assert "test_op" in key
        assert "claude-opus-4-5" in key
        assert "freellmapi" in key

    def test_idempotency_invalidate(self):
        manager = IdempotencyManager()

        def compute():
            return "result"

        key = "test_key_456"
        manager.check_and_store(key, compute)

        assert manager.cache.get(key) is not None
        assert manager.invalidate(key) is True
        assert manager.cache.get(key) is None

    def test_stable_context_hash(self):
        hash1 = create_stable_context_hash(
            system_rules="Rule 1",
            architecture="Arch 1",
            style="Style 1",
            contracts="Contract 1",
            instructions="Instr 1",
            prompt_version="1.0",
        )
        hash2 = create_stable_context_hash(
            system_rules="Rule 1",
            architecture="Arch 1",
            style="Style 1",
            contracts="Contract 1",
            instructions="Instr 1",
            prompt_version="1.0",
        )
        assert hash1 == hash2
        assert len(hash1) == 16

        # Different version should produce different hash
        hash3 = create_stable_context_hash(
            system_rules="Rule 1",
            prompt_version="2.0",
        )
        assert hash3 != hash1

    def test_dynamic_context_hash(self):
        hash1 = create_dynamic_context_hash(
            season_arc="Arc 1",
            episode_objective="Objective 1",
        )
        hash2 = create_dynamic_context_hash(
            season_arc="Arc 1",
            episode_objective="Objective 1",
        )
        assert hash1 == hash2

    def test_task_hash(self):
        hash1 = create_task_hash(
            agent="TestAgent",
            operation="test_op",
            task_description="Generate something",
        )
        hash2 = create_task_hash(
            agent="TestAgent",
            operation="test_op",
            task_description="Generate something",
        )
        assert hash1 == hash2


import time

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
