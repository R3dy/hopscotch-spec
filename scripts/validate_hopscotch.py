#!/usr/bin/env python3
import argparse
import re
import sys
from dataclasses import dataclass
from typing import Dict, List, Set, Tuple


NODE_TYPES = {"world", "continent", "region", "location", "area"}
ENTITY_TYPES = {
    "encounter",
    "check",
    "hazard",
    "secret",
    "loot",
    "creature",
    "clock",
    "travel",
    "milestone",
    "map",
    "npc",
}
ALL_TYPES = NODE_TYPES | ENTITY_TYPES

LOCATION_KINDS = {"settlement", "dungeon", "outpost", "wilderness", "ruin", "ship", "other"}
ENCOUNTER_TYPES = {"combat", "social", "exploration", "puzzle", "mixed"}
CLOCK_UNITS = {"days", "hours", "turns", "milestones"}

ALLOWED_FIELDS: Dict[str, Set[str]] = {
    "world": {"name", "summary", "tags"},
    "continent": {"name", "parent", "summary", "tags"},
    "region": {"name", "parent", "summary", "tags"},
    "location": {"name", "parent", "summary", "tags", "kind"},
    "area": {"name", "parent", "summary", "tags", "key", "readAloud", "features", "exits"},
    "encounter": {
        "name",
        "scope",
        "encounterType",
        "trigger",
        "participants",
        "checks",
        "hazards",
        "choices",
        "outcomes",
        "rewards",
        "escalation",
        "notes",
    },
    "check": {"skill", "dc", "onSuccess", "onFail"},
    "hazard": {"name", "scope", "trigger", "effect", "save", "dc", "damage", "disarm"},
    "secret": {"name", "scope", "text", "reveal", "leadsTo"},
    "loot": {"name", "scope", "items"},
    "creature": {"name", "scope", "baseRef", "overlay", "notes", "tags"},
    "clock": {"name", "scope", "unit", "tracks", "advance"},
    "travel": {
        "name",
        "from",
        "to",
        "distanceOrDuration",
        "paceRules",
        "navCheck",
        "randomEncountersRef",
        "environmentRules",
    },
    "milestone": {"name", "when", "effect"},
    "map": {"name", "scope", "keys"},
    "npc": {
        "name",
        "scope",
        "alignment",
        "ancestry",
        "role",
        "statblock",
        "hooks",
        "notes",
        "knows",
    },
}


@dataclass
class Block:
    block_type: str
    block_id: str
    keys: Set[str]
    values: Dict[str, str]
    line_start: int


def parse_blocks(lines: List[str]) -> Tuple[List[Block], List[str]]:
    blocks: List[Block] = []
    errors: List[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("```hopscotch:"):
            info = line.strip()[len("```hopscotch:") :]
            info_parts = info.split()
            if not info_parts:
                errors.append(f"Line {i+1}: Missing type in hopscotch block info string.")
                i += 1
                continue
            block_type = info_parts[0]
            match = re.search(r"\bid=([^\s]+)", info)
            if not match:
                errors.append(f"Line {i+1}: Missing id in hopscotch block info string.")
                block_id = ""
            else:
                block_id = match.group(1)
            i += 1
            content_lines = []
            while i < len(lines) and not lines[i].startswith("```"):
                content_lines.append(lines[i])
                i += 1
            if i >= len(lines):
                errors.append(f"Line {i+1}: Unterminated hopscotch block for id {block_id}.")
                break
            keys, values = parse_top_level_keys(content_lines)
            blocks.append(Block(block_type, block_id, keys, values, i + 1))
        i += 1
    return blocks, errors


def parse_top_level_keys(lines: List[str]) -> Tuple[Set[str], Dict[str, str]]:
    keys: Set[str] = set()
    values: Dict[str, str] = {}
    for line in lines:
        if not line.strip():
            continue
        if line.startswith(" ") or line.startswith("\t"):
            continue
        if ":" not in line:
            continue
        key, rest = line.split(":", 1)
        key = key.strip()
        if not key:
            continue
        keys.add(key)
        value = rest.strip()
        if value.startswith(("'", '"')) and value.endswith(("'", '"')) and len(value) >= 2:
            value = value[1:-1]
        values[key] = value
    return keys, values


def validate_block(block: Block) -> Tuple[List[str], List[str]]:
    errors: List[str] = []
    warnings: List[str] = []
    if block.block_type not in ALL_TYPES:
        errors.append(f"Line {block.line_start}: Unknown block type '{block.block_type}'.")
        return errors, warnings
    if not block.block_id:
        errors.append(f"Line {block.line_start}: Block missing id.")

    allowed_fields = ALLOWED_FIELDS.get(block.block_type)
    if allowed_fields is None:
        warnings.append(
            f"Line {block.line_start}: No SPEC field list for type '{block.block_type}'."
        )
    else:
        unknown_keys = sorted(block.keys - allowed_fields)
        for key in unknown_keys:
            warnings.append(
                f"Line {block.line_start}: Field '{key}' is not defined in SPEC for "
                f"type '{block.block_type}'."
            )

    if block.block_type in NODE_TYPES:
        if "name" not in block.keys:
            errors.append(f"Line {block.line_start}: {block.block_type} missing required field 'name'.")
        if block.block_type != "world" and "parent" not in block.keys:
            errors.append(
                f"Line {block.line_start}: {block.block_type} missing required field 'parent'."
            )
        if block.block_type == "location":
            kind = block.values.get("kind", "")
            if not kind:
                errors.append(f"Line {block.line_start}: location missing required field 'kind'.")
            elif kind not in LOCATION_KINDS:
                errors.append(
                    f"Line {block.line_start}: location kind '{kind}' is not valid."
                )
        if block.block_type == "area" and "parent" not in block.keys:
            errors.append(f"Line {block.line_start}: area missing required field 'parent'.")
    if block.block_type == "encounter":
        for field in ("name", "scope", "encounterType", "trigger"):
            if field not in block.keys:
                errors.append(
                    f"Line {block.line_start}: encounter missing required field '{field}'."
                )
        enc_type = block.values.get("encounterType", "")
        if enc_type and enc_type not in ENCOUNTER_TYPES:
            errors.append(
                f"Line {block.line_start}: encounterType '{enc_type}' is not valid."
            )
    if block.block_type == "check":
        for field in ("skill", "dc", "onSuccess", "onFail"):
            if field not in block.keys:
                errors.append(
                    f"Line {block.line_start}: check missing required field '{field}'."
                )
    if block.block_type == "hazard":
        for field in ("name", "scope", "trigger", "effect"):
            if field not in block.keys:
                errors.append(
                    f"Line {block.line_start}: hazard missing required field '{field}'."
                )
    if block.block_type == "secret":
        for field in ("name", "scope", "text"):
            if field not in block.keys:
                errors.append(
                    f"Line {block.line_start}: secret missing required field '{field}'."
                )
    if block.block_type == "loot":
        for field in ("name", "scope", "items"):
            if field not in block.keys:
                errors.append(
                    f"Line {block.line_start}: loot missing required field '{field}'."
                )
    if block.block_type == "creature":
        for field in ("name", "scope", "baseRef"):
            if field not in block.keys:
                errors.append(
                    f"Line {block.line_start}: creature missing required field '{field}'."
                )
    if block.block_type == "clock":
        for field in ("name", "scope", "unit"):
            if field not in block.keys:
                errors.append(
                    f"Line {block.line_start}: clock missing required field '{field}'."
                )
        unit = block.values.get("unit", "")
        if unit and unit not in CLOCK_UNITS:
            errors.append(f"Line {block.line_start}: clock unit '{unit}' is not valid.")
    if block.block_type == "travel":
        for field in ("name", "from", "to", "distanceOrDuration"):
            if field not in block.keys:
                errors.append(
                    f"Line {block.line_start}: travel missing required field '{field}'."
                )
    if block.block_type == "milestone":
        for field in ("name", "when", "effect"):
            if field not in block.keys:
                errors.append(
                    f"Line {block.line_start}: milestone missing required field '{field}'."
                )
    if block.block_type == "npc":
        for field in ("name", "scope"):
            if field not in block.keys:
                errors.append(
                    f"Line {block.line_start}: npc missing required field '{field}'."
                )
    if block.block_type == "map":
        for field in ("name", "scope", "keys"):
            if field not in block.keys:
                errors.append(
                    f"Line {block.line_start}: map missing required field '{field}'."
                )
    return errors, warnings


def summarize_blocks(blocks: List[Block]) -> Dict[str, int]:
    counts = {block_type: 0 for block_type in ALL_TYPES}
    for block in blocks:
        if block.block_type in counts:
            counts[block.block_type] += 1
    return counts


def format_block_label(block: Block) -> str:
    name = block.values.get("name", "")
    if name:
        return f"{block.block_type}: {block.block_id} ({name})"
    return f"{block.block_type}: {block.block_id}"


def build_node_index(blocks: List[Block]) -> Tuple[List[Block], Dict[str, Block], Dict[str, List[Block]]]:
    nodes = [block for block in blocks if block.block_type in NODE_TYPES and block.block_id]
    by_id = {block.block_id: block for block in nodes}
    children: Dict[str, List[Block]] = {}
    for block in nodes:
        parent_id = block.values.get("parent", "")
        if parent_id:
            children.setdefault(parent_id, []).append(block)
    return nodes, by_id, children


def print_node_hierarchy(blocks: List[Block]) -> Set[str]:
    nodes, _, children = build_node_index(blocks)
    printed_ids: Set[str] = set()

    def print_level(parent_id: str, expected_type: str, indent: int) -> None:
        for child in children.get(parent_id, []):
            if child.block_type != expected_type:
                continue
            print("\t" * indent + format_block_label(child))
            printed_ids.add(child.block_id)
            if expected_type == "continent":
                print_level(child.block_id, "region", indent + 1)
            elif expected_type == "region":
                print_level(child.block_id, "location", indent + 1)
            elif expected_type == "location":
                print_level(child.block_id, "area", indent + 1)

    worlds = [block for block in nodes if block.block_type == "world"]
    for world in worlds:
        print(format_block_label(world))
        printed_ids.add(world.block_id)
        print_level(world.block_id, "continent", 1)

    return printed_ids


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate a Hopscotch file against core SPEC requirements."
    )
    parser.add_argument("path", help="Path to .hopscotch file")
    args = parser.parse_args()

    try:
        with open(args.path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except OSError as exc:
        print(f"ERROR: Could not read {args.path}: {exc}", file=sys.stderr)
        return 2

    blocks, parse_errors = parse_blocks(lines)
    errors = list(parse_errors)
    warnings: List[str] = []

    seen_ids: Set[str] = set()
    for block in blocks:
        if block.block_id:
            if block.block_id in seen_ids:
                errors.append(
                    f"Line {block.line_start}: Duplicate id '{block.block_id}'."
                )
            seen_ids.add(block.block_id)
        block_errors, block_warnings = validate_block(block)
        errors.extend(block_errors)
        warnings.extend(block_warnings)

    print("Summary:")
    printed_ids = print_node_hierarchy(blocks)
    counts = summarize_blocks(blocks)
    print("\tentities:")
    for block_type in sorted(ENTITY_TYPES):
        print(f"\t\t{block_type}: {counts[block_type]}")

    orphaned = [
        block
        for block in blocks
        if block.block_type in NODE_TYPES
        and block.block_id
        and block.block_id not in printed_ids
    ]
    if orphaned:
        print("\torphaned nodes:")
        for block in orphaned:
            print("\t\t" + format_block_label(block))

    if errors:
        print("\nValidation errors:", file=sys.stderr)
        for err in errors:
            print(f"- {err}", file=sys.stderr)
        if warnings:
            print("\nSPEC warnings:", file=sys.stderr)
            for warning in warnings:
                print(f"- {warning}", file=sys.stderr)
        return 1

    if warnings:
        print("\nSPEC warnings:", file=sys.stderr)
        for warning in warnings:
            print(f"- {warning}", file=sys.stderr)

    print("\nValidation OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
