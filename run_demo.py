#!/usr/bin/env python
"""Demo script to run agents and populate Knowledge Ledger + Story Graph."""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from dorama_studio.agents.narrative.story_architect import StoryArchitectAgent
from dorama_studio.agents.narrative.master_writer import MasterWriterAgent
from dorama_studio.agents.narrative.hook_engine import HookEngineAgent
from dorama_studio.agents.narrative.episode_scorer import EpisodeScorerAgent
from dorama_studio.core.knowledge_ledger import knowledge_ledger
from dorama_studio.core.story_graph import story_graph_manager


def run_demo():
    print("[DEMO] Running DORAMA STUDIO demo pipeline...")

    # 1. Story Architect - creates season architecture
    print("\n1. Story Architect...")
    architect = StoryArchitectAgent()
    arch_result = architect.run({
        "concept_seed": "Una heredera descubre que su familia oculta una tecnologia de energia limpia",
        "genre": "romance_traicion",
        "num_episodes": 2,
        "episode_duration": 90,
        "seed_identifier": "demo_s01"
    })
    print(f"   Architecture created: {len(arch_result.get('episodes', []))} episodes")

    # 2. Hook Engine for Episode 1
    print("\n2. Hook Engine (Ep 1)...")
    hook_engine = HookEngineAgent()
    ep1_blueprint = arch_result.get('episodes', [])[0] if arch_result.get('episodes') else {}
    hook_result = hook_engine.run({
        "episode_num": 1,
        "episode_blueprint": ep1_blueprint,
        "characters": arch_result.get('character_bible', []),
        "genome_context": {},
        "viral_ruleset": ["hook < 3s", "visual first", "zero dialogue"]
    })
    print(f"   Top 5 hooks generated: {hook_result.get('all_candidates_count', 0)} candidates")

    # 3. Master Writer for Episode 1
    print("\n3. Master Writer (Ep 1)...")
    master_writer = MasterWriterAgent()
    writer_result = master_writer.run({
        "blueprint": ep1_blueprint,
        "characters": arch_result.get('character_bible', []),
        "ep": 1,
        "total_episodes": 2,
        "viral_ruleset": [],
        "originality_memo": "",
        "genome_context": {},
        "emerging_tropes": [],
        "episode_id": "e01",
        "episode_title": "El despertar"
    })
    print(f"   Beats written: {len(writer_result.get('beats', []))}")

    # 4. Episode Scorer
    print("\n4. Episode Scorer (Ep 1)...")
    scorer = EpisodeScorerAgent()
    beats = writer_result.get('beats', [])
    score_result = scorer.run({
        "beats": beats,
        "episode_id": "e01"
    })
    print(f"   Score: {score_result.get('total_score', 0)}/100, Verdict: {score_result.get('verdict', 'N/A')}")

    # 5. Repeat for Episode 2
    print("\n5. Episode 2...")
    ep2_blueprint = arch_result.get('episodes', [{}])[1] if len(arch_result.get('episodes', [])) > 1 else {}
    hook_result2 = hook_engine.run({
        "episode_num": 2,
        "episode_blueprint": ep2_blueprint,
        "characters": arch_result.get('character_bible', []),
        "genome_context": {},
        "viral_ruleset": []
    })
    writer_result2 = master_writer.run({
        "blueprint": ep2_blueprint,
        "characters": arch_result.get('character_bible', []),
        "ep": 2,
        "total_episodes": 2,
        "viral_ruleset": [],
        "originality_memo": "",
        "genome_context": {},
        "emerging_tropes": [],
        "episode_id": "e02",
        "episode_title": "La revelacion"
    })
    score_result2 = scorer.run({
        "beats": writer_result2.get('beats', []),
        "episode_id": "e02"
    })
    print(f"   Score Ep 2: {score_result2.get('total_score', 0)}/100")

    # Summary
    print("\n" + "="*50)
    print("[OK] Demo pipeline completed!")
    print("="*50)

    # Print knowledge ledger summary
    events = knowledge_ledger.get_knowledge_events()
    print(f"\n[DATA] Knowledge Ledger: {len(events)} events recorded")
    for ev in events[-5:]:  # last 5
        print(f"   - {ev.get('knowledge_type')} by {ev.get('character_id')} [{ev.get('knowledge_state')}]")

    # Print story graph summary
    nodes = story_graph_manager.graph.nodes
    edges = story_graph_manager.graph.edges
    print(f"\n[GRAPH] Story Graph: {len(nodes)} nodes, {len(edges)} edges")
    for nid, ndata in list(nodes.items())[:10]:
        print(f"   Node: {nid} ({ndata.node_type}) - {ndata.description[:50]}")
    for eid, edata in list(edges.items())[:10]:
        print(f"   Edge: {edata.source_node_id} -> {edata.target_node_id} [{edata.relationship_type}]")

    return True


if __name__ == "__main__":
    run_demo()