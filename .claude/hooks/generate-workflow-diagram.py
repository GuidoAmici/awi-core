#!/usr/bin/env python3
"""
generate-workflow-diagram.py
Regenerates workflow-diagram.md from skill frontmatter + _workflow-config.json.

Usage: python3 generate-workflow-diagram.py <skills_dir>

Each skill .md file may have YAML frontmatter:
  ---
  group: DAY          # must match a group id in _workflow-config.json
  description: ...    # short label shown in diagram node
  order: 2            # position within group (lower = first)
  hidden: true        # omit from diagram (optional)
  ---
"""
import os
import sys
import json
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skills" / "shared" / "scripts"))
from paths import SYSTEM_AWI_RELDIR

SKIP_FILES = {
    "workflow-diagram.md",
    "_legend.md",
    ".abstract.md",
    ".overview.md",
}


def parse_frontmatter(path):
    """Extract simple key: value YAML frontmatter. Returns {} if none present."""
    try:
        with open(path, encoding="utf-8") as f:
            content = f.read()
    except OSError:
        return {}
    if not content.startswith("---\n"):
        return {}
    end = content.find("\n---", 4)
    if end == -1:
        return {}
    fm_text = content[4:end].strip()
    result = {}
    for line in fm_text.splitlines():
        if ":" not in line:
            continue
        k, _, v = line.partition(":")
        v = v.strip().strip('"').strip("'")
        if v.lower() == "true":
            v = True
        elif v.lower() == "false":
            v = False
        else:
            try:
                v = int(v)
            except ValueError:
                pass
        result[k.strip()] = v
    return result


def node_id(skill_name):
    """Convert skill name to a valid mermaid node identifier."""
    return skill_name.replace("-", "_").replace(" ", "_")


def main():
    skills_dir = sys.argv[1] if len(sys.argv) > 1 else f"{SYSTEM_AWI_RELDIR}/skills"
    output_file = os.path.join(skills_dir, "workflow-diagram.md")
    config_file = os.path.join(skills_dir, "_workflow-config.json")

    if not os.path.isfile(config_file):
        print(f"[workflow-diagram] ERROR: config not found: {config_file}", file=sys.stderr)
        sys.exit(1)

    with open(config_file, encoding="utf-8") as f:
        config = json.load(f)

    groups_config = {g["id"]: g for g in config["groups"]}
    group_order = [g["id"] for g in config["groups"]]
    cross_flows = config.get("cross_group_flows", [])
    special_edges = config.get("special_edges", [])

    # Collect all skill files with frontmatter
    skills_by_group = defaultdict(list)
    for fname in sorted(os.listdir(skills_dir)):
        if fname.startswith(".") or fname in SKIP_FILES:
            continue
        if not fname.endswith(".md"):
            continue
        path = os.path.join(skills_dir, fname)
        fm = parse_frontmatter(path)
        if not fm or "group" not in fm:
            continue
        if fm.get("hidden"):
            continue
        if fm["group"] not in groups_config:
            print(f"[workflow-diagram] WARNING: unknown group '{fm['group']}' in {fname}", file=sys.stderr)
            continue
        skill_name = fname[:-3]
        skills_by_group[fm["group"]].append({
            "name": skill_name,
            "description": str(fm.get("description", "")),
            "order": fm.get("order", 99),
        })

    for group in skills_by_group.values():
        group.sort(key=lambda s: s["order"])

    # --- Build mermaid ---
    lines = ["flowchart TD"]

    for gid in group_order:
        gcfg = groups_config[gid]
        skills = skills_by_group.get(gid, [])
        if not skills:
            continue

        lines.append(f'    subgraph {gid}["{gcfg["label"]}"]')

        # Node definitions
        for skill in skills:
            nid = node_id(skill["name"])
            desc = skill["description"]
            label = f'{skill["name"]}<br/>{desc}' if desc else skill["name"]
            lines.append(f'        {nid}["{label}"]')

        # Sequential edges within group
        if gcfg.get("auto_connect", True) and len(skills) > 1:
            for i in range(len(skills) - 1):
                a = node_id(skills[i]["name"])
                b = node_id(skills[i + 1]["name"])
                lines.append(f"        {a} --> {b}")

        # Special edges that belong to this group
        group_skill_names = {s["name"] for s in skills}
        for edge in special_edges:
            if edge["from"] in group_skill_names and edge["to"] in group_skill_names:
                a = node_id(edge["from"])
                b = node_id(edge["to"])
                label = edge.get("label", "")
                arrow = f'-->|{label}|' if label else "-->"
                lines.append(f"        {a} {arrow} {b}")

        lines.append("    end")
        lines.append("")

    # Cross-group flows
    lines.append("    %% Cross-group flows")
    for flow in cross_flows:
        src = flow["from"]
        label = flow.get("label", "")
        dotted = flow.get("dotted", False)
        if dotted and label:
            arrow = f'-.->|{label}|'
        elif dotted:
            arrow = "-.->"
        elif label:
            arrow = f'-->|{label}|'
        else:
            arrow = "-->"

        dst = flow.get("to_node") or flow.get("to")
        lines.append(f"    {src} {arrow} {dst}")

    mermaid = "\n".join(lines)

    # --- Build summary table ---
    table_rows = []
    for gid in group_order:
        gcfg = groups_config[gid]
        skills = skills_by_group.get(gid, [])
        if not skills:
            continue
        sep = " → " if gcfg.get("auto_connect", True) else ", "
        skills_str = sep.join(s["name"] for s in skills)
        cadence = gcfg.get("cadence", "")
        table_rows.append(f'| {gcfg["summary_label"]} | {skills_str} | {cadence} |')

    summary_table = "\n".join([
        "| Phase | Skills | Cadence |",
        "|---|---|---|",
    ] + table_rows)

    # --- Write output ---
    output = (
        "# AWI Skills — Workflow Diagram\n\n"
        "<!-- AUTO-GENERATED — edit `_workflow-config.json` and skill frontmatter, not this file -->\n\n"
        f"```mermaid\n{mermaid}\n```\n\n"
        f"## Summary\n\n{summary_table}\n"
    )

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(output)

    total = sum(len(v) for v in skills_by_group.values())
    print(f"[workflow-diagram] regenerated ({total} skills across {len(skills_by_group)} groups)")


if __name__ == "__main__":
    main()
