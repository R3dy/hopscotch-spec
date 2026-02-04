# Hopscotch v0.5 Specification

This document defines the Hopscotch v0.5 file format.

## 1. Scope

Hopscotch is a Markdown-native, open file format for representing tabletop roleplaying adventures in a uniform, machine-parseable way. A Hopscotch file MUST be deterministically convertible to JSON for import into third-party tools (VTTs, mobile apps, pipelines).

Hopscotch v0.5 is focused on:
- A canonical world model: World → Continent → Region → Destination → Location → Area
- Typed entities for common adventure components (scenes, encounters, NPCs/creatures, secrets, loot, hazards, travel, milestones, clocks)
- Simple, explicit linking via IDs and references
- Optional intent structure for rules pointers, discovery gates, devices, tables, assets, and lightweight scene/clock conditions
- A strict subset of semantics that is practical to implement

Non-goals for v0.5:
- Full rules modeling for every game system
- Legendary/lair actions and full spellcasting blocks (reserved for v0.5+)
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
- `hopscotchVersion` (string, e.g. `0.4.0`)
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

In prose, implementations MAY support inline references of the form `@{some.id}`. Inline reference parsing is OPTIONAL in v0.5.

### 4.4 Reference objects
Some fields take a list of ref objects rather than raw id strings.

A ref object MUST define:
- `ref` (string; an id)

A ref object MAY define:
- `note` (string; short context or label)

### 4.5 Common attachment fields
Several blocks MAY attach optional lists of ref objects to express intent without adding rules simulation:

- `rules` → list of `ruleRef.*` objects (see §10)
- `assets` → list of `asset.*` objects (see §17)
- `gates` → list of `gate.*` objects (see §11)
- `devices` → list of `device.*` objects (see §15)
- `tables` → list of `table.*` objects (see §16)

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
- `rules` (list of refs to `ruleRef.*`)
- `assets` (list of refs to `asset.*`)

### 5.4 Location
A `location` MUST define:
- `parent` (destination id)
- `kind` (enum): `building | dwelling | landmark | camp | district | other`

A `location` MAY define:
- `rules` (list of refs to `ruleRef.*`)
- `assets` (list of refs to `asset.*`)

### 5.5 Area
An `area` MUST define:
- `parent` (destination id OR location id)

An `area` MAY define:
- `key` (string; map key, e.g., `C1`, `S17`)
- `readAloud` (string)
- `features` (list of refs; hazards/rules)
- `exits` (list of refs)
- `rules` (list of refs to `ruleRef.*`)
- `assets` (list of refs to `asset.*`)
- `gates` (list of refs to `gate.*`)
- `devices` (list of refs to `device.*`)

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
- `conditions` (object; see §6.6)
- `outcomes` (object; see §6.7)
- `rules` (list of refs to `ruleRef.*`)
- `gates` (list of refs to `gate.*`)
- `tables` (list of refs to `table.*`)
- `assets` (list of refs to `asset.*`)

### 6.4 Dialogue blocks
Scenes MAY define `dialogue` as a list of dialogue blocks. Each block MUST define:
- `type` (enum): `read_aloud | dm_guidance | conditional | likely_actions | mechanics`

Each block MAY define:
- `speaker` (string or ref to an NPC/creature id)

Additional requirements by type:
- `read_aloud` MUST define `text` (markdown string; spoken aloud)
- `dm_guidance` MUST define `text` (markdown string; DM-facing)
- `dm_guidance` MAY define `subItems` (list of strings; bullet points for guidance)
- `conditional` MUST define `conditions` (list of conditional talking points)
- `likely_actions` MUST define `action` (string; what the party might do) and `response` (string; how to respond)
- `mechanics` MUST define `text` (markdown string; rules or mechanical guidance)

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

### 6.6 Scene conditions (state-based)
Scenes MAY declare optional gating rules under `conditions`:

- `enterIf` (list of simple conditions; all must be satisfied)
- `skipIf` (list of simple conditions; if any is satisfied, skip the scene)

Simple conditions MUST be one of:
- `{ hasSecret: "secret.id" }`
- `{ not: { hasSecret: "secret.id" } }`
- `{ clockAtLeast: { id: "clock.id", track: "subject", days: <number> } }`

Conditions are intent signals for DMs/tools, not executable rules.

Example scene conditions:

```text
```hopscotch:scene id=scene.salsvault.entry
title: "Enter Salsvault"
summary: The party reaches the submerged ruin.
conditions:
  enterIf:
    - hasSecret: secret.salsvault.location
  skipIf:
    - not:
        hasSecret: secret.salsvault.location
```
```

### 6.7 Scene outcomes
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

### 6.8 DM usability rationale
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

### 8.2 Encounter types (v0.5)
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
- `gates` (list of refs to `gate.*`)
- `devices` (list of refs to `device.*`)
- `tables` (list of refs to `table.*`)
- `choices` (list of decision objects)
- `outcomes` (list of result objects)
- `rewards` (list; refs to `loot.*`, `item.*`, `secret.*`)
- `escalation` (object; see §8.5)
- `notes` (string)
- `rules` (list of refs to `ruleRef.*`)

### 8.5 Escalation semantics
An encounter MAY escalate to:
- another encounter: `toEncounter: <encounter id>`
- a clock advance: `advanceClock: { id: <clock id>, amount: <number> }`

## 9. Checks

A `check` represents a single resolution point. v0.5 adds optional structured resolution while preserving the v0.3 `skill` + `dc` fields.

A `check` MUST define:
- `skill` (string; e.g., `Investigation`, `Persuasion`, `Survival`)
- `dc` (integer)
- `onSuccess` (string or ref)
- `onFail` (string or ref)

A `check` MAY define:
- `scope` (node id; where the check applies)
- `resolution` (object; see §9.1)

### 9.1 Enhanced resolution (optional)
If present, `resolution` MUST define:
- `type` (enum): `dc | opposed`
- `skill` (string; primary skill)

If `type: dc`, `resolution` MUST define:
- `dc` (number)

If `type: opposed`, `resolution` MAY define:
- `opposedBy` (object): `{ ref?, skill? }`

`resolution` MAY also define:
- `alternatives` (list of strings; alternative skills)
- `advantageWhen` (list of simple conditions; see §6.6)
- `disadvantageWhen` (list of simple conditions; see §6.6)

Example check with structured resolution:

```text
```hopscotch:check id=check.thin-ice.crossing
skill: Survival
dc: 13
resolution:
  type: dc
  skill: Survival
  dc: 13
  alternatives: ["Perception", "Investigation"]
  advantageWhen:
    - hasSecret: secret.locals.warned
onSuccess: "You plot a safe route across the ice."
onFail: "The ice cracks beneath you."
```
```

## 10. Rule references (ruleRef)

A `ruleRef` block is a lightweight pointer to external rules text. It is a reference, not embedded rules content.

A `ruleRef` MUST define:
- `id` (prefix `rule.`)
- `source` (enum): `srd | phb | dmg | custom | other`
- `name` (string)

A `ruleRef` MAY define:
- `uri` (string; URL or relative path)
- `section` (string; e.g., `DMG Chapter 5`)
- `notes` (short string; MUST NOT embed long copyrighted text)
- `tags` (list of strings)

The following blocks MAY define `rules` as a list of ref objects to `ruleRef.*`:
- `destination`, `location`, `area`, `scene`, `encounter`, `hazard`, `travel`, `clock`

Example rule reference and usage:

```text
```hopscotch:ruleRef id=rule.dmg.thin-ice
source: dmg
name: "Thin Ice"
section: "DMG Chapter 5"
notes: "Use as a pointer for thin-ice travel checks."
```

```hopscotch:travel id=travel.thin-ice
name: "Thin Ice Crossing"
from: destination.syrinlya
to: destination.thin-sheets
distanceOrDuration: "4 hours"
rules:
  - ref: rule.dmg.thin-ice
```
```

## 11. Gates (Passive/Active discovery)

A `gate` represents a passive or active discovery threshold (e.g., passive Perception or an active check).

A `gate` MUST define:
- `id` (prefix `gate.`)
- `type` (enum): `passive | active`
- `skill` (string)
- `threshold` (number)

A `gate` MAY define:
- `opposedBySkill` (string)
- `onSuccess` (object)
- `onFail` (object)

`onSuccess` and `onFail` MUST allow at least:
- `reveal` (list of ids: secrets, devices, or other entities)
- `notes` (string)

The following blocks MAY define `gates` as a list of ref objects to `gate.*`:
- `area`, `scene`, `encounter`

Example passive gate:

```text
```hopscotch:gate id=gate.ice-frog.glimmer
type: passive
skill: Perception
threshold: 13
onSuccess:
  reveal:
    - creature.croaker.ice-frog
  notes: "A faint movement under the ice draws your attention."
```
```

## 12. Hazards

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
- `rules` (list of refs to `ruleRef.*`)

## 13. Secrets (Clues)

A `secret` represents discoverable information.

A `secret` MUST define:
- `name` (string)
- `scope` (node id)
- `text` (string)

A `secret` MAY define:
- `reveal` (list of reveal objects: `{by, method, checkRef?, dc?, when?}`)
- `leadsTo` (list of refs)

## 14. Loot and items

A `loot` block represents a reward package or discovery.

A `loot` MUST define:
- `name` (string)
- `scope` (node id)

A `loot` MUST define at least one of:
- `items` (list of item objects)
- `text` (string; description of the loot)

A `loot` MAY define:
- `tags` (list of strings)

Item objects SHOULD include:
- `name` (string)
- `kind` (string; e.g., `treasure`, `clue`, `gear`)
- `value` (number; gp equivalent if desired)
- `text` (string; optional)

### 14.1 NPCs

An `npc` block represents a notable non-player character.

An `npc` MUST define:
- `name` (string)
- `scope` (node id)

An `npc` MAY define:
- `alignment` (string; e.g., `LE`, `CG`, `N`)
- `ancestry` (string; e.g., `human`, `elf`, `dwarf`)
- `disposition` (enum): `enemy | neutral | ally`
- `faction` (string)
- `description` (string; character description and background)
- `voice` (string; how the NPC speaks)
- `mannerisms` (string; behavioral quirks)
- `emotionalBaseline` (string; default emotional state)
- `breakingPoint` (string; what makes the NPC snap or change behavior)
- `personality` (list of strings; personality traits)
- `motivations` (list of strings; what drives the NPC)
- `role` (string)
- `statblock` (string; external reference)
- `hooks` (list of strings)
- `notes` (string)
- `knows` (list; strings or refs to `secret.*`)
- `hides` (list; strings or refs to secrets the NPC conceals)
- `tags` (list of strings)
- `assets` (list of refs to `asset.*`)

## 15. Devices

A `device` represents a multi-step interactive object (trap, lock, chest) without simulating full rules.

A `device` MUST define:
- `id` (prefix `device.`)
- `name` (string)

A `device` MAY define:
- `scope` (string; area/location/destination id)
- `stages` (list of stage objects)

Each stage object MUST allow:
- `id` (string)
- `gateRef` (ref to `gate.*`)
- `checkRef` (ref to `check.*`)
- `hazardRef` (ref to `hazard.*`)
- `onSuccess` (object)
- `onFail` (object)

The following blocks MAY define `devices` as a list of ref objects to `device.*`:
- `area`, `encounter`

Example device with stages:

```text
```hopscotch:device id=device.tulgi-chest
name: "Tulgi's Ironbound Chest"
scope: area.tulgi-cabin.interior
stages:
  - id: notice
    gateRef: gate.tulgi-chest.glint
  - id: disarm
    checkRef: check.tulgi-chest.tools
    onSuccess:
      notes: "The poison needle is disabled."
    onFail:
      notes: "The needle triggers as the lock opens."
      reveal:
        - hazard.tulgi-chest.needle
```
```

## 16. Tables

A `table` is a lightweight tabular data block.

A `table` MUST define:
- `id` (prefix `table.`)
- `headers` (list of strings)
- `rows` (list of list of strings)

A `table` MAY define:
- `title` (string)
- `notes` (string)

The following blocks MAY define `tables` as a list of ref objects to `table.*`:
- `travel`, `scene`, `encounter`

Example table:

```text
```hopscotch:table id=table.reduced-travel-speeds
title: "Reduced Travel Speeds"
headers: ["Pace", "Miles/Day", "Notes"]
rows:
  - ["Slow", "18", "Disadvantage on navigation checks"]
  - ["Normal", "24", "No modifier"]
  - ["Fast", "30", "Disadvantage on Perception checks"]
```
```

## 17. Assets

An `asset` block represents media attached to adventure content.

An `asset` MUST define:
- `id` (prefix `asset.`)
- `kind` (enum): `image`
- `uri` (string; URL or relative path)

An `asset` MAY define:
- `title` (string)
- `roles` (list of strings; e.g., `portrait`, `token`, `map-dm`, `map-player`, `handout`)
- `visibility` (enum): `player | dm | both` (default `both`)
- `alt` (string)
- `credit` (object): `{ author?, license?, source? }`

The following blocks MAY define `assets` as a list of ref objects to `asset.*`:
- `destination`, `location`, `area`, `scene`, `npc`, `creature`

Example asset usage:

```text
```hopscotch:asset id=asset.map.croaker
kind: image
uri: "assets/maps/croaker-cave.png"
title: "Croaker Cave (DM)"
roles: ["map-dm"]
visibility: dm
```
```

## 18. Creatures: SRD references + overlays (FINAL)

### 18.1 Purpose
Hopscotch supports referencing canonical stat blocks (e.g., SRD) while allowing adventure-specific modifications via overlays (deltas).

### 18.2 Required fields
A `creature` MUST define:
- `name` (string)
- `scope` (node id)
- `baseRef` (string; e.g., `srd:bandit_captain`)

A `creature` MAY define:
- `overlay` (object; see §18.3)
- `notes` (string)
- `tags` (list of strings)
- `assets` (list of refs to `asset.*`)

### 18.3 Overlay model
Overlays MUST be structured patches. Implementations MUST apply overlays in this order:
1) scalar stats (hp/ac/speed/abilities)
2) lists (resistances/immunities/vulnerabilities)
3) traits/actions (action/bonus/reaction)
4) notes

Supported v0.5 overlay sections:
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
Trait and action changes MUST be expressed under `overlay` in v0.5 (no top-level `traits`/`actions`).

## 19. Clocks (Time pressure)

### 19.1 Definition
A `clock` models time pressure (e.g., disease progression, deadlines). Advancing a clock is a first-class event.

### 19.2 Required fields
A `clock` MUST define:
- `name` (string)
- `scope` (node id)
- `unit` (enum): `days | hours | turns | milestones`

A `clock` MAY define:
- `description` (string; explains the clock's purpose)
- `rules` (list of refs to `ruleRef.*`)

### 19.3 Tracks
A clock MAY define `tracks`, each with:
- `subject` (string)
- `max` (number)
- `milestones` (list of `{at, effect}` objects)

Implementations MAY visualize tracks as countdowns or progress bars.

### 19.4 Triggers (optional)
A clock MAY define:
- `onExpire` (list of refs to `scene.*`, `encounter.*`, or `milestone.*`)
- `onMilestone` (list of `{ at, trigger }` objects, where `trigger` is a ref)

Example clock triggers:

```text
```hopscotch:clock id=clock.frostbite
name: "Frostbite Escalation"
scope: region.biting-north
unit: days
tracks:
  - subject: "Expedition"
    max: 10
onMilestone:
  - at: 5
    trigger: scene.expedition.warned
onExpire:
  - milestone.expedition.failed
```
```

### 19.5 Advancing clocks
Clocks MAY define an `advance` section describing automatic advancement events. Encounters MAY advance clocks via `escalation.advanceClock`.

## 20. Travel

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
- `tables` (list of refs to `table.*`)
- `rules` (list of refs to `ruleRef.*`)

## 21. Milestones (Advancement)

A `milestone` block represents an explicit adventure milestone.

A `milestone` MUST define:
- `name` (string)
- `when` (string or ref)
- `effect` (string; e.g., `Advance to level 2`)

## 22. JSON projection (normative)

A Hopscotch file MUST be convertible into a JSON document with, at minimum:
- `metadata`
- `nodes` (all node blocks keyed by id)
- `entities` (all non-node blocks keyed by id, including scenes and links)
- `edges` (optional; derived from explicit refs and `link` blocks)

Implementations MUST preserve all IDs and references.
