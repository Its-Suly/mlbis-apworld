# Archipelago APWorld for Mario & Luigi: Bowser's Inside Story

An [Archipelago](https://archipelago.gg) world for *Mario & Luigi:
Bowser's Inside Story* (Nintendo DS, 2009). None existed before this
one.

*[Version française](README.fr.md)*

## Status: it works, and it has been played

The full loop runs, verified in game rather than argued from code:
checks are detected and sent, items come back and are written into the
running game, and a second player's item crossed from another world into
this one and back out again.

- **728 locations** — 647 treasure entries and 81 attack-piece blocks
- **Nine abilities as items**, the hammer among them, shuffled into the
  multiworld pool
- **The ROM is never modified.** Everything happens in memory while you
  play, so there is no patching step and no patched copy to keep
- Packaged as `dist/mlbis.apworld`, which generates a seed on its own
- Passes Archipelago's own 206 general tests, plus two suites of ours

What is *not* settled is the access logic, and the section on limits
below says exactly how far to trust it.

## Playing it

You need BizHawk **2.10 exactly** and your own copy of the game. Only
the machine that generates the seed needs the apworld; players of other
games need nothing from here.

Full instructions live in
[`mlbis/docs/setup_en.md`](mlbis/docs/setup_en.md). The short version:
drop `mlbis.apworld` into your Archipelago `custom_worlds`, generate,
open `connector_bizhawk_generic.lua` **from its own folder** in
BizHawk's Lua console, then start the BizHawk client.

### Options

| Option | What it decides |
|---|---|
| `shuffle_abilities` | the nine abilities become items to find |
| `safe_ability_placement` | keeps them where the logic is trustworthy |
| `goal` | `abilities` ends the run by itself, `manual` hands you `/bis_goal` |
| `filler_variety` | thins out the beans, which are 27% of the vanilla pool |

## How it works

Three measured facts carry the whole world.

**A treasure's identifier is its bit rank.** Collected treasures are
tracked in the `Exxx` global script-variable bitfield at `020560C8`:

```
treasure with identifier N  ->  byte 020560C8 + N/8, bit N%8   (LSB first)
```

That identifier lives in bytes 4-5 of each `Treasure/TreasureInfo.dat`
entry, so an Archipelago location id is `BASE_ID + bit rank` with **no
lookup table at all**. Attack pieces use the same array at higher
indices and need no special case. The bit is set on a block's *first*
hit, not when it is exhausted, so a location fires as soon as the player
sees anything.

**Items are delivered by writing memory.** Coins at `02056400`,
consumables at `02056406 + index`, gear at `02056427 + id - 1`, all
verified in game. A value written is adopted, displayed, saved, and the
game recomputes its own checksum.

**An ability can be taken away.** Clearing its bit in the `2xxx` field
removes it: the hammer vanishes from the battle command and comes back
when the bit returns. That is what makes abilities tradeable without
patching the ROM — the game still hands you the hammer on schedule, and
the client takes it straight back until the multiworld sends it.

Every structure, with the measurement that established it, is in
[`formats-bis.md`](formats-bis.md).

## Limits, stated plainly

**The access logic works at the granularity of a named area, and the
order of those areas comes from a walkthrough, not from the game.** Four
separate attempts to derive it from the ROM failed, each killed by a
measurement and each written up so nobody repeats them. Worse, this game
sends you back through areas you have already cleared, so a treasure in
a late corner of an early area looks reachable long before it is.

That endangers a run only when an ability lands somewhere unreachable,
which is why `safe_ability_placement` is on by default: the nine
abilities stay in the first five areas, the part of the order a
walkthrough states outright and that a real save file independently
confirms. Ordinary items are free to go anywhere, since finding one late
costs nothing.

**The goal is not "defeat Dark Bowser".** Over 800,000 script commands
were read, field and battle alike, and the ending leaves no mark a
client could recognise. Rather than guess at an address, the run either
ends when the nine abilities are gathered, or when the player types
`/bis_goal`.

**Never played to completion.** The loop, the multiworld and
reconnection are all measured, but no seed has been played through to
the end. That is the next thing that will happen, and it will also
supply the two missing measurements.

## What is in here

| Path | Contents |
|---|---|
| `mlbis/` | the world itself: locations, items, regions, options, client |
| `data/` | tables extracted from the ROM, all regenerable |
| `tools/` | extraction, RAM dumping, diff analysis, the three test suites |
| `formats-bis.md` | every confirmed structure, with file and line references |
| `reference-mlss.md` | study of the Superstar Saga world bundled with Archipelago |
| `MEMOIRE.md` | project memory: fixed decisions, constraints, open questions |
| `JOURNAL.md` | dated log, including the dead ends and the bugs |

Three test suites, all runnable from the repository root:

```
venv\Scripts\python.exe tools\test_generation.py    a seed generates
venv\Scripts\python.exe tools\test_client.py        bits, addresses, delivery
venv\Scripts\python.exe tools\test_archipelago.py   Archipelago's own 206 tests
```

## Evidence conventions

Every claim in this repository carries one of three labels, and the rule
is enforced throughout:

- **Vérifié / Verified** — read in source code or measured, cited with
  file and line
- **Hypothèse / Hypothesis** — inferred from another game or a pattern,
  not yet confirmed
- **À tester / To test** — nothing settles it either way

Anything without a file-and-line source is a hypothesis, not a fact. A
plausible but wrong memory address costs hours of debugging, and this
repository has the dead ends to prove it.

## Reproducing the tables

You need your own legally obtained ROM. The static analysis targets one
exact revision:

- Mario & Luigi: Bowser's Inside Story, NDS, North America, pre-DSi
- SHA-256 `9126963d6c6b6f81a9a666ba766e223781ff286634486e2a56d07a4c82eef4f1`

```
py -3.13 -m venv venv
venv\Scripts\python.exe -m pip install ndspy capstone .\vendor\mnllib.py
venv\Scripts\python.exe tools\extract_names.py
venv\Scripts\python.exe tools\build_location_table.py
venv\Scripts\python.exe tools\build_apworld_data.py
```

## About the ROM

**No ROM is included in this repository, and none will be provided.**
The `.gitignore` excludes `.nds`, `.7z`, `.zip` and save files. Every
table under `data/` is regenerated from a local ROM you supply yourself;
nothing was entered by hand.

## Credits and sources

This work stands entirely on prior community research.
**[SOURCES.md](SOURCES.md) lists every source with its URL, the exact
commit consulted, its licence, and what was taken from it.**

- The [MnL-Modding](https://github.com/MnL-Modding) community and its
  [Discord](https://discord.gg/rhJ6HGyymJ) — Randoglobin for the
  treasure and item tables, Cheatoglobin for the save structure,
  `mnllib` for the internal formats, BIS-docs for the script commands
- [8y8x's MLBIS manual](https://inf.gg/mlbis/manual), CC0 — named the
  `Exxx` bitfield we had located by measurement, along with the global
  register block and the ARM9 memory map
- [Archipelago](https://github.com/ArchipelagoMW/Archipelago), and in
  particular its bundled `worlds/mlss`, the Superstar Saga world, which
  had already solved this class of problem for the first game in the
  series

Randoglobin and Cheatoglobin are GPL-3.0-or-later. They were **read to
understand**, and facts were drawn from them — offsets, file formats,
field layouts. **No code was copied.** Reusing their code would impose
the GPL on the resulting APWorld. `mnllib` is LGPL-3.0 and *is* used as
a dependency, which its licence permits.

If you believe anything here reproduces your code rather than restating
a fact learned from it, open an issue and it will be removed.

## Licence

[MIT](LICENSE) for the original work here — the world, the tools, the
documentation and the tables they generate. It cannot cover the
underlying game: the names and identifiers under `data/` are extracted
from a commercial ROM and remain the property of their rights holders.
Third-party projects keep their own licences, listed in
[SOURCES.md](SOURCES.md).
