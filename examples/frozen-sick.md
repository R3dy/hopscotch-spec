# Frozen Sick (Canonical Hopscotch Companion)

This document is a canonical companion to `examples/frozen-sick.hopscotch`.
It intentionally avoids non-structural/adapted prose and mirrors the Hopscotch v0.5 data model.

## Metadata

- `hopscotchVersion`: `0.5.0`
- `title`: `Frozen Sick`
- `system`: `D&D 5E`
- `levels`: `1-3`
- `tags`: `adventure`, `arctic`, `mystery`, `dungeon`

## Canonical Structure

- World graph: `world → continent → region → destination → location → area`
- Core destinations:
  - `destination.palebank-village`
  - `destination.croaker-cave`
  - `destination.syrinlya`
  - `destination.salsvault`
  - `destination.eiselcross-wilds`

## Canonical Adventure Flow

1. **Palebank investigation (early)**
   - Scenes:
     - `scene.palebank.funeral`
     - `scene.palebank.urgon-cabin`
     - `scene.palebank.tulgi-cabin`
     - `scene.palebank.pelc-curiosities`
   - Primary discoveries:
     - `secret.pelc-receipt`
     - `secret.frigid-woe-vials`
     - `secret.tulgi-uttolot`
     - `secret.hulil-croaker`

2. **Croaker Cave escalation (mid)**
   - Scenes:
     - `scene.croaker.approach`
     - `scene.croaker.hideout`
     - `scene.palebank.irven-infected`
   - Key outcome:
     - recover vials and identify urgent need for cure (`secret.irven-infected`)

3. **Eiselcross expedition (mid → late)**
   - Scenes:
     - `scene.travel.to-syrinlya`
     - `scene.syrinlya.arrival`
     - `scene.travel.to-salsvault`
     - `scene.salsvault.entry`
     - `scene.salsvault.ferol`
     - `scene.salsvault.curative-lab`
     - `scene.return.to-syrinlya`
     - `scene.conclusion`
   - Key discoveries:
     - `secret.salsvault-location`
     - `secret.antidote-cache`

## Canonical Entity Coverage

- Scenes: narrative framing with `dialogue`, `conditions`, and `outcomes`
- Links: explicit `narrative_linear`, `narrative_branch`, and `mechanical` edges
- Encounters: social/exploration/combat/mixed encounters with typed triggers
- Hazards: environmental/mechanical dangers with optional saves and disarm refs
- Secrets: discoverable clues with structured reveal metadata
- Loot: scoped rewards and item bundles
- NPCs and creatures:
  - NPC roleplay profile blocks (`npc.*`)
  - SRD-based creature references plus overlays (`creature.*`)
- Clock: milestone-based pressure model (`clock.frigid-woe`)
- Travel: bounded legs between nodes (`travel.*`)
- Milestone: explicit advancement trigger (`milestone.level-3`)
- Rule references: external rules pointer (`rule.*`)

## Canonical Usage Notes

- Use `examples/frozen-sick.hopscotch` as the source of truth for parsers and tools.
- Treat this Markdown file as a human-oriented index only.
- IDs, refs, and typed blocks in the `.hopscotch` file are the canonical format representation.
