# Changelog

All notable changes to this project will be documented in this file.

This project aims to follow Semantic Versioning: https://semver.org/

## [0.5.0] - 2026-02-03

### Added
- Added extended NPC characterization fields: `disposition` (enemy/neutral/ally), `faction`, `description`, `voice`, `mannerisms`, `emotionalBaseline`, `breakingPoint`, `personality` (array), `motivations` (array), `hides` (array), and `tags`.
- Added new scene dialogue types: `likely_actions` (with `action`/`response` fields) and `mechanics` (for rules guidance).
- Added `subItems` support for `dm_guidance` dialogue blocks.
- Added optional `scope` field to `check` blocks for location context.
- Added optional `description` field to `clock` blocks.
- Added optional `text` field to `loot` blocks as alternative to `items` array.
- Added optional `tags` field to `loot` and `secret` blocks.
- Added support for mixed string/ref entries in NPC `knows` and `hides` fields.

### Changed
- Bumped Hopscotch version references to v0.5.0 across docs and schemas.
- Made `items` field optional in `loot` blocks (either `items` or `text` must be present).

## [0.4.0] - TBD

### Added
- Added optional rule references (`ruleRef`) and `rules` attachments for destinations, locations, areas, scenes, encounters, hazards, travel, and clocks.
- Added enhanced check resolution metadata with multi-skill, opposed checks, and advantage/disadvantage hints.
- Added passive/active discovery `gate` blocks with optional attachments to areas, scenes, and encounters.
- Added multi-stage `device` blocks for traps/locks with gate/check/hazard references.
- Added lightweight `table` blocks for travel/scene/encounter attachments.
- Added `asset` blocks with optional attachments to destinations, locations, areas, scenes, NPCs, and creatures.
- Added clock triggers (`onMilestone`, `onExpire`) and scene entry conditions.
- Added v0.4 schemas for new block types and a block/Entity union schema.

### Changed
- Bumped Hopscotch version references to v0.4.0 across docs and schemas.
- Updated `examples/frozen-sick.hopscotch` to v0.4 and expanded it to demonstrate all v0.4 features (v0.2 example retained).
- Extended the validator to recognize v0.4 block types and fields.

## [0.3.0] - TBD

### Added
- Added `scene` blocks with dialogue, conditional talking points, and outcomes.
- Added `link` blocks for explicit narrative/mechanical edges.
- Added v0.3 JSON Schemas for scenes and links.
- Added v0.3 validation rules and tests for scene version gating.

### Changed
- Bumped Hopscotch version references to v0.3.0 across docs and schemas.

## [0.2.0] - TBD

### Added
- Added the `destination` node type between `region` and `location` in the world model.
- Added v0.2 node schemas for core world model nodes.

### Changed
- Updated v0.2 node hierarchy to World → Continent → Region → Destination → Location → Area (breaking change).

## [0.1.0] - 2026-01-03

### Added
- Initial Hopscotch v0.1 normative specification (`SPEC.md`)
- JSON Schemas for v0.1 entities: encounter, creature (with overlays), and clock
- Permissively licensed reference adventure example: `examples/frostbound-blight.hopscotch`
