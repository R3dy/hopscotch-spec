# Migration guide: v0.1 -> v0.2

Hopscotch v0.2 introduces a new `destination` node between `region` and `location`. This is a breaking change for any files that model region-level locations.

## Summary of breaking changes
- World hierarchy is now World -> Continent -> Region -> Destination -> Location -> Area.
- `destination.kind` uses the old location-kind enum: `settlement | dungeon | outpost | wilderness | ruin | ship | other`.
- `location.kind` is now for inside-destination structures: `building | dwelling | landmark | camp | district | other`.
- `area.parent` may be `destination.*` or `location.*`.

## Migration steps
1) Add destination nodes for any region-level places.
   - Rename block type `location` -> `destination` when its parent is a `region.*`.
   - Change the id prefix to `destination.*`.
2) Update references to renamed ids.
   - Replace `location.*` ids with `destination.*` in `parent`, `scope`, `from`, `to`, `leadsTo`, `exits`, and any other refs.
3) Adjust kinds.
   - Move old `location.kind` values (settlement/dungeon/etc.) to `destination.kind`.
   - For actual sub-places, set `location.kind` to one of `building | dwelling | landmark | camp | district | other`.
4) Update area parents.
   - Areas that belonged to region-level locations should now point to the destination.
   - Areas under a true sub-location can keep `parent: location.*`.
5) Bump version strings.
   - Update `hopscotchVersion` to `0.2.0`.
   - If you validate against JSON schemas, use the v0.2 schema ids under `schemas/`.

## Example rename

```text
```hopscotch:location id=location.croaker-cave
name: Croaker Cave
kind: dungeon
parent: region.biting-north
```
```

becomes:

```text
```hopscotch:destination id=destination.croaker-cave
name: Croaker Cave
kind: dungeon
parent: region.biting-north
```
```

# Migration guide: v0.2 -> v0.3

Hopscotch v0.3 introduces narrative scenes and explicit links between blocks.

## Summary of changes
- Added a `scene` block type with dialogue, conditions, and outcomes.
- Added a `link` block type for explicit narrative/mechanical edges.
- Updated schemas and recommendations to `hopscotchVersion: 0.3.0`.

## Migration steps
1) Add scenes where you want structured read-aloud or branching dialogue.
2) Add link blocks to connect scenes to locations, encounters, or other scenes.
3) Bump version strings.
   - Update `hopscotchVersion` to `0.3.0`.
   - If you validate against JSON schemas, use the v0.3 schema ids under `schemas/`.
