#!/usr/bin/env python
"""Export provenance data (Knowledge Ledger + Story Graph) to JSON/CSV for audit."""

import json
import csv
import sys
from datetime import datetime

from dorama_studio.core.knowledge_ledger import knowledge_ledger
from dorama_studio.core.story_graph import story_graph_manager


def export_knowledge_ledger(path: str = "knowledge_events.json", limit: int | None = None):
    """Export knowledge ledger events to JSON."""
    events = knowledge_ledger.get_knowledge_events(limit=limit)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(events, f, ensure_ascii=False, indent=2)
    print(f"Exported {len(events)} knowledge events to {path}")


def export_knowledge_ledger_csv(path: str = "knowledge_events.csv", limit: int | None = None):
    """Export knowledge ledger events to CSV."""
    events = knowledge_ledger.get_knowledge_events(limit=limit)
    if not events:
        print("No events to export.")
        return
    # Collect all possible keys
    all_keys = set()
    for ev in events:
        all_keys.update(ev.keys())
    fieldnames = ["event_id", "timestamp", "character_id", "knowledge_type",
                  "knowledge_state", "source", "source_reference", "confidence", "context"]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for ev in events:
            # Ensure all fields present
            row = {k: ev.get(k, "") for k in fieldnames}
            writer.writerow(row)
    print(f"Exported {len(events)} knowledge events to {path}")


def export_story_graph_json(path: str = "story_graph.json"):
    """Export Story Graph nodes and edges to JSON."""
    # story_graph_manager.graph is a StoryGraph dataclass with .nodes dict and .edges dict
    nodes_dict = story_graph_manager.graph.nodes
    edges_dict = story_graph_manager.graph.edges
    # Convert to plain serializable structures
    nodes = []
    for nid, ndata in nodes_dict.items():
        nodes.append({"id": nid, "type": ndata.node_type if hasattr(ndata, 'node_type') else ndata.get("node_type", ""),
                      "metadata": ndata.metadata if hasattr(ndata, 'metadata') else ndata.get("metadata", {})})
    edges = []
    for ekey, edata in edges_dict.items():
        # ekey could be "source->target" or similar; extract source/target
        # edges stored as dict key -> StoryEdge; StoryEdge has fields source_node_id, target_node_id, relationship_type, strength, metadata
        if hasattr(edata, 'source_node_id'):
            src = edata.source_node_id
            tgt = edata.target_node_id
            rel = edata.relationship_type
            meta = edata.metadata
        else:
            # fallback if edata is dict
            src = edata.get("source_node_id", "")
            tgt = edata.get("target_node_id", "")
            rel = edata.get("relationship_type", "")
            meta = edata.get("metadata", {})
        edges.append({"source": src, "target": tgt, "relationship": rel, "metadata": meta})
    payload = {"nodes": nodes, "edges": edges}
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print(f"Exported story graph: {len(nodes)} nodes, {len(edges)} edges to {path}")


def export_story_graph_csv(path: str = "story_graph.csv"):
    """Export Story Graph to CSV (nodes and edges separate)."""
    nodes = []
    for nid, data in story_graph_manager.graph.nodes(data=True):
        nodes.append({"id": nid, "type": data.get("node_type", ""),
                      "metadata": json.dumps(data.get("metadata", {}))})
    edges = []
    for u, v, data in story_graph_manager.graph.edges(data=True):
        edges.append({"source": u, "target": v,
                      "relationship": data.get("relationship_type", ""),
                      "metadata": json.dumps(data.get("metadata", {}))})
    # Write nodes CSV
    with open(path.replace(".csv", "_nodes.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "type", "metadata"])
        writer.writeheader()
        for n in nodes:
            writer.writerow(n)
    # Write edges CSV
    with open(path.replace(".csv", "_edges.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["source", "target", "relationship", "metadata"])
        writer.writeheader()
        for e in edges:
            writer.writerow(e)
    print(f"Exported story graph nodes/edges to {path}_nodes.csv and {path}_edges.csv")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Export provenance data")
    parser.add_argument("--knowledge", action="store_true", help="Export knowledge ledger JSON")
    parser.add_argument("--knowledge-csv", action="store_true", help="Export knowledge ledger CSV")
    parser.add_argument("--story", action="store_true", help="Export story graph JSON")
    parser.add_argument("--story-csv", action="store_true", help="Export story graph CSV (nodes/edges)")
    parser.add_argument("--limit", type=int, default=None, help="Max events to export")
    args = parser.parse_args()

    if args.knowledge or not any([args.knowledge, args.knowledge_csv, args.story, args.story_csv]):
        export_knowledge_ledger("knowledge_events.json", limit=args.limit)
    if args.knowledge_csv:
        export_knowledge_ledger_csv("knowledge_events.csv", limit=args.limit)
    if args.story or not any([args.knowledge, args.knowledge_csv, args.story, args.story_csv]):
        export_story_graph_json("story_graph.json")
    if args.story_csv:
        export_story_graph_csv("story_graph.csv")


if __name__ == "__main__":
    main()