# Hopscotch v0.1 Specification

This document defines the Hopscotch v0.1 file format.

## 1. Scope

Hopscotch is a Markdown-native, open file format for representing tabletop roleplaying adventures in a uniform, machine-parseable way. A Hopscotch file MUST be deterministically convertible to JSON for import into third-party tools (VTTs, mobile apps, pipelines).

Hopscotch v0.1 is focused on:
- A canonical world model: World → Continent → Region → Location → Area
- Typed entities for common adventure components (encounters, NPCs/creatures, secrets, loot, hazards, travel, milestones, clocks)
- Simple, explicit linking via IDs and references
- A strict subset of semantics that is practical to implement

Non-goals for v0.1:
- Full rules modeling for every game system
- Legendary/lair actions and full spellcasting blocks (reserved for v0.2+)
- Automatic extraction of structure from arbitrary prose without explicit blocks

## 2. Normative language

The key words MUST, MUST NOT, REQUIRED, SHOULD, SHOULD NOT, and MAY are to be interpreted as described in RFC 2119.

## 3. File format

### 3.1 Encoding
- Files MUST be UTF-8.
- Files SHOULD use LF line endings, but parsers MUST accept LF or CRLF.

### 3.2 Structure
A `.hopscotch` file is Markdown text that MAY include YAML frontmatter. Structure is defined by Hopscotch typed blocks (see §4). Unstructured Markdown outside blocks MAY be ignored by strict parsers.

### 3.3 YAML frontmatter (recommended)
If present, frontmatter MUST be the first content in the file and delimited by `---` lines.

Recommended fields:
- `hopscotchVersion` (string, e.g. `0.1.0`)
- `title` (string)
- `license` (string)
- `system` (string)
- `levels` (string)
- `tags` (list of strings)

## 4. Typed blocks

### 4.1 Syntax
Typed blocks MUST use fenced code blocks with an info string of the form:

```text
```hopscotch:<type> id=<id>
<YAML content>
```
```

Where:
- `<type>` is a Hopscotch type identifier (see §5)
- `id=<id>` declares the block’s globally unique identifier

### 4.2 IDs
- Every block MUST declare an `id`.
- IDs MUST be unique within a file.
- IDs SHOULD use a stable, dot-scoped naming scheme (e.g., `location.palebank-village`, `area.croaker-cave.c1`).
- IDs MUST be treated as case-sensitive strings.

### 4.3 References
Hopscotch objects refer to other objects by ID using fields such as `parent`, `scope`, `ref`, `leadsTo`, etc.

In prose, implementations MAY support inline references of the form `@{some.id}`. Inline reference parsing is OPTIONAL in v0.1.

## 5. Node model: World → Continent → Region → Location → Area

### 5.1 Node types
Hopscotch defines the following node types:
- `world`
- `continent`
- `region`
- `location`
- `area`

### 5.2 Common node fields
All node blocks MUST define:
- `name` (string)

All nodes except `world` MUST define:
- `parent` (id)

Nodes MAY define:
- `summary` (string)
- `tags` (list of strings)

### 5.3 Location
A `location` MUST define:
- `kind` (enum): `settlement | dungeon | outpost | wilderness | ruin | ship | other`

### 5.4 Area
An `area` MUST define:
- `parent` (location id)

An `area` MAY define:
- `key` (string; map key, e.g., `C1`, `S17`)
- `readAloud` (string)
- `features` (list of refs; hazards/rules)
- `exits` (list of refs)

## 6. Encounters (FINAL)

### 6.1 Definition (normative)
An Encounter is a bounded unit of play that presents player choice and resolves through interaction with the game world.

Encounters are not limited to combat. An encounter MUST declare an `encounterType`.

### 6.2 Encounter types (v0.1)
`encounterType` MUST be one of:
- `combat`
- `social`
- `exploration`
- `puzzle`
- `mixed`

### 6.3 Required fields
An `encounter` MUST define:
- `name` (string)
- `scope` (node id)
- `encounterType` (enum)
- `trigger` (string)

### 6.4 Optional fields
An `encounter` MAY define:
- `participants` (list of refs; `npc.*`, `creature.*`, or external `baseRef`s)
- `checks` (list; inline checks or refs to `check.*`)
- `hazards` (list; refs to `hazard.*`)
- `choices` (list of decision objects)
- `outcomes` (list of result objects)
- `rewards` (list; refs to `loot.*`, `item.*`, `secret.*`)
- `escalation` (object; see §6.5)
- `notes` (string)

### 6.5 Escalation semantics
An encounter MAY escalate to:
- another encounter: `toEncounter: <encounter id>`
- a clock advance: `advanceClock: { id: <clock id>, amount: <number> }`

## 7. Checks

A `check` represents a single DC gate.

A `check` MUST define:
- `skill` (string; e.g., `Investigation`, `Persuasion`, `Survival`)
- `dc` (integer)
- `onSuccess` (string or ref)
- `onFail` (string or ref)

## 8. Hazards

A `hazard` represents an environmental or mechanical danger.

A `hazard` MUST define:
- `name` (string)
- `scope` (area id)
- `trigger` (string)
- `effect` (string)

A `hazard` MAY define:
- `save` (string)
- `dc` (integer)
- `damage` (string, e.g., `1d6 fire`)
- `disarm` (ref to `check.*`)

## 9. Secrets (Clues)

A `secret` represents discoverable information.

A `secret` MUST define:
- `name` (string)
- `scope` (node id)
- `text` (string)

A `secret` MAY define:
- `reveal` (list of reveal objects: `{by, method, checkRef?, dc?, when?}`)
- `leadsTo` (list of refs)

## 10. Loot and items

A `loot` block represents a reward package or discovery.

A `loot` MUST define:
- `name` (string)
- `scope` (node id)
- `items` (list of item objects)

Item objects SHOULD include:
- `name` (string)
- `kind` (string; e.g., `treasure`, `clue`, `gear`)
- `value` (number; gp equivalent if desired)
- `text` (string; optional)

## 11. Creatures: SRD references + overlays (FINAL)

### 11.1 Purpose
Hopscotch supports referencing canonical stat blocks (e.g., SRD) while allowing adventure-specific modifications via overlays (deltas).

### 11.2 Required fields
A `creature` MUST define:
- `name` (string)
- `scope` (node id)
- `baseRef` (string; e.g., `srd:bandit_captain`)

### 11.3 Overlay model
Overlays MUST be structured patches. Implementations MUST apply overlays in this order:
1) scalar stats (hp/ac/speed/abilities)
2) lists (resistances/immunities/vulnerabilities)
3) traits/actions (action/bonus/reaction)
4) notes

Supported v0.1 overlay sections:
- `hp` (mode add|set)
- `ac` (set)
- `speed.walk` (set|add)
- `abilities` (set|add)
- `resistances`/`immunities`/`vulnerabilities` (add/remove)
- `traits` (add/remove)
- `actions.action` (add/remove)
- `actions.bonus` (add/remove)
- `actions.reaction` (add/remove)

Unknown overlay keys MUST fail validation in strict mode.

## 12. Clocks (Time pressure)

### 12.1 Definition
A `clock` models time pressure (e.g., disease progression, deadlines). Advancing a clock is a first-class event.

### 12.2 Required fields
A `clock` MUST define:
- `name` (string)
- `scope` (node id)
- `unit` (enum): `days | hours | turns | milestones`

### 12.3 Tracks
A clock MAY define `tracks`, each with:
- `subject` (string)
- `max` (number)
- `milestones` (list of `{at, effect}` objects)

Implementations MAY visualize tracks as countdowns or progress bars.

### 12.4 Advancing clocks
Clocks MAY define an `advance` section describing automatic advancement events. Encounters MAY advance clocks via `escalation.advanceClock`.

## 13. Travel

A `travel` block models a bounded travel segment.

A `travel` MUST define:
- `name` (string)
- `from` (node id)
- `to` (node id)
- `distanceOrDuration` (string)

A `travel` MAY define:
- `paceRules` (string)
- `navCheck` (ref to `check.*`)
- `randomEncountersRef` (string or ref)
- `environmentRules` (string)

## 14. Milestones (Advancement)

A `milestone` block represents an explicit adventure milestone.

A `milestone` MUST define:
- `name` (string)
- `when` (string or ref)
- `effect` (string; e.g., `Advance to level 2`)

## 15. JSON projection (normative)

A Hopscotch file MUST be convertible into a JSON document with, at minimum:
- `metadata`
- `nodes` (all node blocks keyed by id)
- `entities` (all non-node blocks keyed by id)
- `edges` (optional; derived from explicit refs)

Implementations MUST preserve all IDs and references.
