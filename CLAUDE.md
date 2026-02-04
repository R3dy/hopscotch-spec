# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Hopscotch is an open, Markdown-native file format for representing tabletop roleplaying (TTRPG) adventures. Files use `.hopscotch` extension and contain Markdown with typed blocks that can be deterministically converted to JSON for VTTs and other tools.

**Current Version**: v0.5.0 (pre-1.0)

## Commands

```bash
# Validate a hopscotch file
python scripts/validate_hopscotch.py examples/frozen-sick.hopscotch

# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_validate_hopscotch.py -v
```

## Repository Structure

- `SPEC.md` - Normative specification with RFC-style keywords (MUST/SHOULD/MAY)
- `schemas/` - 27 JSON Schema files for all block types
- `scripts/validate_hopscotch.py` - Python validator (~800 lines)
- `examples/frozen-sick.hopscotch` - Complete v0.5 reference adventure
- `tests/` - Python unittest tests with fixtures in `tests/fixtures/`

## Architecture

### Hopscotch File Format

Files are UTF-8 Markdown with:
1. Optional YAML frontmatter (`hopscotchVersion`, `title`, `system`, etc.)
2. Typed blocks using fenced code syntax: ` ```hopscotch:<type> id=<unique-id> `
3. YAML content inside each block

### World Hierarchy (Nodes)

```
World → Continent → Region → Destination → Location → Area
```

- **Destination**: Travelable places (settlement, dungeon, outpost, wilderness, ruin, ship)
- **Location**: Sub-locations within destinations (building, dwelling, landmark, camp, district)
- **Area**: Smallest tactical unit with `key` (e.g., "C1"), `readAloud`, `features`, `exits`

### Entity Types

Independent blocks with a `scope` linking them to locations:

- **scene** - Narrative scenes with dialogue (read_aloud, dm_guidance, conditional)
- **encounter** - Combat, social, exploration, puzzle, or mixed encounters
- **creature** - Monster stat blocks with optional `baseRef`/`overlay`
- **npc** - Named characters
- **check**, **hazard**, **secret**, **loot** - Encounter components
- **clock** - Progress trackers (disease, time pressure)
- **travel** - Journey segments between destinations
- **link** - Explicit narrative/mechanical connections
- **gate** - Discovery/access gates (v0.5)
- **device** - Multi-stage traps/locks (v0.5)
- **table** - Lightweight encounter tables (v0.5)
- **ruleRef**, **asset** - External references and media (v0.5)

### Validator Key Functions

In `scripts/validate_hopscotch.py`:
- `parse_blocks()` - Extracts hopscotch blocks from file
- `parse_frontmatter_version()` - Gets version tuple from frontmatter
- `validate_block()` - Main validation with field checks and version gating
- `validate_scene_dialogue()` - Validates conditional dialogue structure

### Version Gating

Scene blocks require `hopscotchVersion >= 0.3.0`. The validator rejects scene blocks in older versions.

## Contributing

1. Open an issue describing the change
2. Submit PR updating: `SPEC.md`, `CHANGELOG.md`, relevant `schemas/`, and `examples/`
3. Use RFC keywords (MUST/SHOULD/MAY) in specification text
