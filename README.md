# Hopscotch Specification (v0.2)

Hopscotch is an open, Markdown-native file format for representing tabletop roleplaying adventures in a uniform, machine-parseable way.

Design goals for v0.2:
- Human-readable Markdown with strict, typed blocks for structure
- Deterministic 1:1 projection to JSON for importing into third-party apps (VTTs, mobile, tooling)
- Full support for typical published-adventure components:
  - World → Continent → Region → Destination → Location → Area hierarchy
  - Encounters (combat, social, exploration, puzzle, mixed)
  - NPCs/creatures, secrets/clues, loot/items, hazards, checks, maps, travel segments, milestones
  - Time pressure via clocks (e.g., disease progression)

Repository contents:
- `SPEC.md` — Normative Hopscotch v0.2 specification
- `schemas/` — JSON Schemas for key entities (v0.2)
- `examples/` — A permissively licensed reference adventure in `.hopscotch`
- `CHANGELOG.md` — Version history

## License

This repository is licensed under the Apache License 2.0. See `LICENSE`.

## Status

Hopscotch v0.2 is a draft specification intended to be practical and implementable. Backwards-incompatible changes may occur until v1.0.0.

## Quick start

Hopscotch files are UTF-8 Markdown with:
- YAML frontmatter (optional but recommended)
- Typed Hopscotch blocks, using fenced code blocks:

```text
```hopscotch:destination id=destination.example
name: Example Destination
kind: settlement
parent: region.example
summary: A travelable destination represented in Hopscotch.
```
```

See `examples/frostbound-blight.hopscotch` for an end-to-end sample that exercises most v0.2 features.
