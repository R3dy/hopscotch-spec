#!/usr/bin/env python3
import argparse
import re
import sys
from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple


NODE_TYPES = {"world", "continent", "region", "destination", "location", "area"}
ENTITY_TYPES = {
    "scene",
    "link",
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

DESTINATION_KINDS = {"settlement", "dungeon", "outpost", "wilderness", "ruin", "ship", "other"}
LOCATION_KINDS = {"building", "dwelling", "landmark", "camp", "district", "other"}
ENCOUNTER_TYPES = {"combat", "social", "exploration", "puzzle", "mixed"}
CLOCK_UNITS = {"days", "hours", "turns", "milestones"}
LINK_TYPES = {"narrative_branch", "narrative_linear", "mechanical"}

ALLOWED_FIELDS: Dict[str, Set[str]] = {
    "world": {"name", "summary", "tags"},
    "continent": {"name", "parent", "summary", "tags"},
    "region": {"name", "parent", "summary", "tags"},
    "destination": {"name", "parent", "summary", "tags", "kind"},
    "location": {"name", "parent", "summary", "tags", "kind"},
    "area": {"name", "parent", "summary", "tags", "key", "readAloud", "features", "exits"},
    "scene": {
        "title",
        "summary",
        "location",
        "participants",
        "tags",
        "timing",
        "tone",
        "dialogue",
        "outcomes",
    },
    "link": {"from", "to", "linkType", "notes", "tags"},
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
    content_lines: List[str]


def parse_blocks(lines: List[str]) -> Tuple[List[Block], List[str]]:
    blocks: List[Block] = []
    errors: List[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("```hopscotch:"):
            block_start_line = i + 1
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
            blocks.append(Block(block_type, block_id, keys, values, block_start_line, content_lines))
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


def parse_frontmatter_version(lines: List[str]) -> Optional[Tuple[int, int, int]]:
    if not lines or not lines[0].startswith("---"):
        return None
    for i in range(1, len(lines)):
        line = lines[i].rstrip("\n")
        if line.startswith("---"):
            break
        if not line.strip() or line.startswith(" "):
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        if key.strip() != "hopscotchVersion":
            continue
        raw = value.strip().strip("'\"")
        match = re.match(r"^(\d+)\.(\d+)\.(\d+)", raw)
        if not match:
            return None
        return (int(match.group(1)), int(match.group(2)), int(match.group(3)))
    return None


def validate_scene_dialogue(block: Block) -> List[str]:
    errors: List[str] = []
    dialogue_indent = None
    start_idx = 0
    for idx, raw in enumerate(block.content_lines):
        line = raw.rstrip("\n")
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip(" "))
        if line.strip() == "dialogue:":
            dialogue_indent = indent
            start_idx = idx + 1
            break

    if dialogue_indent is None:
        return errors

    item_indent = None
    item_type = None
    conditions_seen = False
    conditions_indent = None
    has_if = False
    has_says = False

    def finalize_item() -> None:
        nonlocal item_type, conditions_seen, conditions_indent, has_if, has_says
        if item_type == "conditional":
            if not conditions_seen:
                errors.append(
                    f"Line {block.line_start}: conditional dialogue missing conditions."
                )
            elif not (has_if and has_says):
                errors.append(
                    f"Line {block.line_start}: conditional dialogue missing if/says."
                )
        item_type = None
        conditions_seen = False
        conditions_indent = None
        has_if = False
        has_says = False

    for idx in range(start_idx, len(block.content_lines)):
        raw = block.content_lines[idx]
        line = raw.rstrip("\n")
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip(" "))
        stripped = line.strip()

        if indent <= dialogue_indent:
            finalize_item()
            break

        if stripped.startswith("- "):
            if item_indent is None or indent == item_indent:
                finalize_item()
                item_indent = indent
                item_type = None
                conditions_seen = False
                conditions_indent = None
                has_if = False
                has_says = False
            after_dash = stripped[2:].strip()
            if after_dash.startswith("type:"):
                value = after_dash[len("type:") :].strip()
                if value == "conditional":
                    item_type = "conditional"
            continue

        if item_indent is None:
            continue

        if stripped.startswith("type:"):
            value = stripped[len("type:") :].strip()
            if value == "conditional":
                item_type = "conditional"
            continue

        if item_type == "conditional":
            if stripped == "conditions:":
                conditions_seen = True
                conditions_indent = indent
                continue
            if conditions_seen and conditions_indent is not None and indent > conditions_indent:
                if stripped.startswith("- if:") or stripped.startswith("if:"):
                    has_if = True
                if stripped.startswith("says:"):
                    has_says = True

    finalize_item()
    return errors


def validate_block(
    block: Block, hopscotch_version: Optional[Tuple[int, int, int]]
) -> Tuple[List[str], List[str]]:
    errors: List[str] = []
    warnings: List[str] = []
    if block.block_type not in ALL_TYPES:
        errors.append(f"Line {block.line_start}: Unknown block type '{block.block_type}'.")
        return errors, warnings
    if hopscotch_version and hopscotch_version < (0, 3, 0):
        if block.block_type in {"scene", "link"}:
            errors.append(
                f"Line {block.line_start}: {block.block_type} blocks require hopscotchVersion >= 0.3.0."
            )
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
        if block.block_type == "destination":
            kind = block.values.get("kind", "")
            if not kind:
                errors.append(f"Line {block.line_start}: destination missing required field 'kind'.")
            elif kind not in DESTINATION_KINDS:
                errors.append(
                    f"Line {block.line_start}: destination kind '{kind}' is not valid."
                )
        if block.block_type == "location":
            kind = block.values.get("kind", "")
            if not kind:
                errors.append(f"Line {block.line_start}: location missing required field 'kind'.")
            elif kind not in LOCATION_KINDS:
                errors.append(
                    f"Line {block.line_start}: location kind '{kind}' is not valid."
                )
        if block.block_type == "area":
            parent = block.values.get("parent", "")
            if not parent:
                errors.append(f"Line {block.line_start}: area missing required field 'parent'.")
            elif not (parent.startswith("destination.") or parent.startswith("location.")):
                errors.append(
                    f"Line {block.line_start}: area parent '{parent}' must be a destination.* or location.* id."
                )
        parent_prefixes = {
            "continent": "world",
            "region": "continent",
            "destination": "region",
            "location": "destination",
        }
        expected_parent_prefix = parent_prefixes.get(block.block_type)
        if expected_parent_prefix:
            parent = block.values.get("parent", "")
            if parent and not parent.startswith(f"{expected_parent_prefix}."):
                errors.append(
                    f"Line {block.line_start}: {block.block_type} parent '{parent}' must start with "
                    f"{expected_parent_prefix}."
                )
    if block.block_type == "scene":
        for field in ("title", "summary"):
            if field not in block.keys:
                errors.append(
                    f"Line {block.line_start}: scene missing required field '{field}'."
                )
        location = block.values.get("location", "")
        if location and not (location.startswith("location.") or location.startswith("area.")):
            errors.append(
                f"Line {block.line_start}: scene location '{location}' must be a location.* or area.* id."
            )
        errors.extend(validate_scene_dialogue(block))
    if block.block_type == "link":
        for field in ("from", "to", "linkType"):
            if field not in block.keys:
                errors.append(
                    f"Line {block.line_start}: link missing required field '{field}'."
                )
        link_type = block.values.get("linkType", "")
        if link_type and link_type not in LINK_TYPES:
            errors.append(
                f"Line {block.line_start}: linkType '{link_type}' is not valid."
            )
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
                print_level(child.block_id, "destination", indent + 1)
            elif expected_type == "destination":
                print_level(child.block_id, "location", indent + 1)
                print_level(child.block_id, "area", indent + 1)
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

    hopscotch_version = parse_frontmatter_version(lines)
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
        block_errors, block_warnings = validate_block(block, hopscotch_version)
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
