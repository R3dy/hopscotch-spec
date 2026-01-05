# Changelog

All notable changes to this project will be documented in this file.

This project aims to follow Semantic Versioning: https://semver.org/

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
