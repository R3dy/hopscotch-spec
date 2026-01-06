# Hopscotch v0.3 Specification

This document defines the Hopscotch v0.3 file format.

## 1. Scope

Hopscotch is a Markdown-native, open file format for representing tabletop roleplaying adventures in a uniform, machine-parseable way. A Hopscotch file MUST be deterministically convertible to JSON for import into third-party tools (VTTs, mobile apps, pipelines).

Hopscotch v0.3 is focused on:
- A canonical world model: World → Continent → Region → Destination → Location → Area
- Typed entities for common adventure components (scenes, encounters, NPCs/creatures, secrets, loot, hazards, travel, milestones, clocks)
- Simple, explicit linking via IDs and references
- A strict subset of semantics that is practical to implement

Non-goals for v0.3:
- Full rules modeling for every game system
- Legendary/lair actions and full spellcasting blocks (reserved for v0.3+)
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
- `hopscotchVersion` (string, e.g. `0.3.0`)
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
- IDs SHOULD use a stable, dot-scoped naming scheme (e.g., `destination.palebank-village`, `area.croaker-cave.c1`).
- IDs MUST be treated as case-sensitive strings.

### 4.3 References
Hopscotch objects refer to other objects by ID using fields such as `parent`, `scope`, `ref`, `leadsTo`, etc.

In prose, implementations MAY support inline references of the form `@{some.id}`. Inline reference parsing is OPTIONAL in v0.3.

## 5. Node model: World → Continent → Region → Destination → Location → Area

### 5.1 Node types
Hopscotch defines the following node types:
- `world`
- `continent`
- `region`
- `destination`
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

### 5.3 Destination
A `destination` MUST define:
- `parent` (region id)
- `kind` (enum): `settlement | dungeon | outpost | wilderness | ruin | ship | other`

A `destination` MAY define:
- `summary` (string)
- `tags` (list of strings)

### 5.4 Location
A `location` MUST define:
- `parent` (destination id)
- `kind` (enum): `building | dwelling | landmark | camp | district | other`

### 5.5 Area
An `area` MUST define:
- `parent` (destination id OR location id)

An `area` MAY define:
- `key` (string; map key, e.g., `C1`, `S17`)
- `readAloud` (string)
- `features` (list of refs; hazards/rules)
- `exits` (list of refs)

## 6. Scenes (Narrative Moments)

### 6.1 Definition (normative)
A `scene` represents a narrative moment in the adventure. Scenes are not locations; they MAY occur in a location and capture dialog, guidance, and outcomes that affect downstream content.

### 6.2 Required fields
A `scene` MUST define:
- `title` (string)
- `summary` (string or markdown block)

### 6.3 Optional fields
A `scene` MAY define:
- `location` (ref to `location.*` or `area.*`)
- `participants` (list of refs; `npc.*`, `creature.*`, or other entities)
- `tags` (list of strings)
- `timing` (string; recommended: `early | mid | late`)
- `tone` (string; e.g., `tense`, `mysterious`)
- `dialogue` (list of dialogue blocks; see §6.4)
- `outcomes` (object; see §6.6)

### 6.4 Dialogue blocks
Scenes MAY define `dialogue` as a list of dialogue blocks. Each block MUST define:
- `type` (enum): `read_aloud | dm_guidance | conditional`

Each block MAY define:
- `speaker` (string or ref to an NPC/creature id)

Additional requirements by type:
- `read_aloud` MUST define `text` (markdown string; spoken aloud)
- `dm_guidance` MUST define `text` (markdown string; DM-facing)
- `conditional` MUST define `conditions` (list of conditional talking points)

Each `conditions` entry MUST define:
- `if` (string expression; see §6.5)
- `says` (markdown string; what the speaker says when the condition applies)

### 6.5 Condition language (lightweight)
Condition expressions are hints for DMs/tools, not executable rules. They are simple boolean strings:
- Identifiers use dot-scoped names (e.g., `party.press_for_details`)
- Negation uses `!` (e.g., `!party.accuse_elro`)
- Optional `&&` and `||` are supported without parentheses

Examples:
- `party.asks_about_bodies && party.is_polite`
- `party.accuse_elro || party.threaten_elro`

### 6.6 Scene outcomes
Scenes MAY declare outcomes under `outcomes.possible[]`. Each outcome MUST define:
- `id` (string)
- `description` (string)

Each outcome MAY define:
- `unlocks` (list of refs to `scene.*`, `encounter.*`, `location.*`, etc.)
- `blocks` (list of refs to `scene.*`, `encounter.*`, `location.*`, etc.)

Example scene with dialogue, conditions, and outcomes:

```text
```hopscotch:scene id=scene.elro-first-contact
title: "Meeting Elro"
summary: The party meets Elro and can learn about the stolen vials.
location: location.pelcs-curiosities
participants:
  - npc.elro-aldataur
dialogue:
  - speaker: npc.elro-aldataur
    type: read_aloud
    text: |
      “I wish I had better news for you,” Elro says...
  - speaker: npc.elro-aldataur
    type: conditional
    conditions:
      - if: party.press_for_details
        says: |
          “I’ve seen frost in places frost should never be.”
      - if: party.accuse_elro
        says: |
          Elro bristles. “You think I’d endanger my own town?”
outcomes:
  possible:
    - id: outcome.elro-trust
      description: Elro trusts the party and shares rumors.
      unlocks:
        - scene.elro-rumors
```
```

### 6.7 DM usability rationale
Scenes keep read-aloud text, DM guidance, and branching dialogue in one place without requiring a full quest engine. The outcomes and conditions are lightweight hints that help DMs and tooling understand narrative flow while preserving table flexibility.

## 7. Links

### 7.1 Definition
A `link` block is an explicit, graph-friendly edge between two or more Hopscotch blocks. Links MAY connect scenes to locations, encounters, or other scenes to represent narrative or mechanical flow.

### 7.2 Required fields
A `link` MUST define:
- `from` (id of the source block)
- `to` (list of target ids)
- `linkType` (enum): `narrative_linear | narrative_branch | mechanical`

### 7.3 Optional fields
A `link` MAY define:
- `tags` (list of strings)
- `notes` (string)

Example links connecting scenes to encounters and locations:

```text
```hopscotch:link id=link.elro-to-bandits
from: scene.elro-first-contact
to:
  - encounter.pelcs.bandits
linkType: mechanical
```

```hopscotch:link id=link.elro-to-shop
from: scene.elro-first-contact
to:
  - location.pelcs-curiosities
linkType: narrative_linear
```
```

## 8. Encounters (FINAL)

### 8.1 Definition (normative)
An Encounter is a bounded unit of play that presents player choice and resolves through interaction with the game world.

Encounters are not limited to combat. An encounter MUST declare an `encounterType`.

### 8.2 Encounter types (v0.3)
`encounterType` MUST be one of:
- `combat`
- `social`
- `exploration`
- `puzzle`
- `mixed`

### 8.3 Required fields
An `encounter` MUST define:
- `name` (string)
- `scope` (node id)
- `encounterType` (enum)
- `trigger` (string)

### 8.4 Optional fields
An `encounter` MAY define:
- `participants` (list of refs; `npc.*`, `creature.*`, or external `baseRef`s)
- `checks` (list; inline checks or refs to `check.*`)
- `hazards` (list; refs to `hazard.*`)
- `choices` (list of decision objects)
- `outcomes` (list of result objects)
- `rewards` (list; refs to `loot.*`, `item.*`, `secret.*`)
- `escalation` (object; see §8.5)
- `notes` (string)

### 8.5 Escalation semantics
An encounter MAY escalate to:
- another encounter: `toEncounter: <encounter id>`
- a clock advance: `advanceClock: { id: <clock id>, amount: <number> }`

## 9. Checks

A `check` represents a single DC gate.

A `check` MUST define:
- `skill` (string; e.g., `Investigation`, `Persuasion`, `Survival`)
- `dc` (integer)
- `onSuccess` (string or ref)
- `onFail` (string or ref)

## 10. Hazards

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

## 11. Secrets (Clues)

A `secret` represents discoverable information.

A `secret` MUST define:
- `name` (string)
- `scope` (node id)
- `text` (string)

A `secret` MAY define:
- `reveal` (list of reveal objects: `{by, method, checkRef?, dc?, when?}`)
- `leadsTo` (list of refs)

## 12. Loot and items

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

### 12.1 NPCs

An `npc` block represents a notable non-player character.

An `npc` MUST define:
- `name` (string)
- `scope` (node id)

An `npc` MAY define:
- `alignment` (string)
- `ancestry` (string)
- `role` (string)
- `statblock` (string; external reference)
- `hooks` (list of strings)
- `notes` (string)
- `knows` (list of refs; `secret.*`)

## 13. Creatures: SRD references + overlays (FINAL)

### 13.1 Purpose
Hopscotch supports referencing canonical stat blocks (e.g., SRD) while allowing adventure-specific modifications via overlays (deltas).

### 13.2 Required fields
A `creature` MUST define:
- `name` (string)
- `scope` (node id)
- `baseRef` (string; e.g., `srd:bandit_captain`)

A `creature` MAY define:
- `overlay` (object; see §13.3)
- `notes` (string)
- `tags` (list of strings)

### 13.3 Overlay model
Overlays MUST be structured patches. Implementations MUST apply overlays in this order:
1) scalar stats (hp/ac/speed/abilities)
2) lists (resistances/immunities/vulnerabilities)
3) traits/actions (action/bonus/reaction)
4) notes

Supported v0.3 overlay sections:
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
Trait and action changes MUST be expressed under `overlay` in v0.3 (no top-level `traits`/`actions`).

## 14. Clocks (Time pressure)

### 14.1 Definition
A `clock` models time pressure (e.g., disease progression, deadlines). Advancing a clock is a first-class event.

### 14.2 Required fields
A `clock` MUST define:
- `name` (string)
- `scope` (node id)
- `unit` (enum): `days | hours | turns | milestones`

### 14.3 Tracks
A clock MAY define `tracks`, each with:
- `subject` (string)
- `max` (number)
- `milestones` (list of `{at, effect}` objects)

Implementations MAY visualize tracks as countdowns or progress bars.

### 14.4 Advancing clocks
Clocks MAY define an `advance` section describing automatic advancement events. Encounters MAY advance clocks via `escalation.advanceClock`.

## 15. Travel

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

## 16. Milestones (Advancement)

A `milestone` block represents an explicit adventure milestone.

A `milestone` MUST define:
- `name` (string)
- `when` (string or ref)
- `effect` (string; e.g., `Advance to level 2`)

## 17. JSON projection (normative)

A Hopscotch file MUST be convertible into a JSON document with, at minimum:
- `metadata`
- `nodes` (all node blocks keyed by id)
- `entities` (all non-node blocks keyed by id, including scenes and links)
- `edges` (optional; derived from explicit refs and `link` blocks)

Implementations MUST preserve all IDs and references.
