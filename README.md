# Archipelago APWorld for Mario & Luigi: Bowser's Inside Story

Research toward an [Archipelago](https://archipelago.gg) world for
*Mario & Luigi: Bowser's Inside Story* (Nintendo DS, 2009). No such
world exists yet for this game.

*[Version française](README.fr.md)*

## Status: feasibility, and it is now established

**No APWorld code has been written yet.** This repository currently
holds research, extracted data tables, and the tools that produce them.

The question that blocked the whole project was simple to state and had
no answer in any available source: **how does the game record that a
treasure has already been collected?** Without that, there is no way to
mark an Archipelago `location` as checked, and no world can be built.

That question is now answered.

### The treasure bitfield

Collected treasures are tracked by a bitfield in the NDS main RAM:

```
treasure with identifier N  ->  byte 0x0560C8 + N/8, bit N%8   (LSB first)
field spans 0x0560C8 to 0x056126, 95 bytes, 758 identifiers
```

The bit rank is the identifier stored in bytes 4-5 of each
`Treasure/TreasureInfo.dat` entry — a field the existing randomizer
never reads.

Verified against the four blocks of one room, identifiers 544 to 547,
all packed into byte `0x05610C`, across five successive RAM dumps:

| Dump | Byte | Bits set | Identifiers |
|---|---|---|---|
| 1 | `0x00` | — | none |
| 2 | `0x01` | 0 | 544 |
| 3 | `0x03` | 0, 1 | 544, 545 |
| 4 | `0x0B` | 0, 1, 3 | 544, 545, 547 |
| 5 | `0x0F` | 0, 1, 2, 3 | 544, 545, 546, 547 |

The last two blocks were hit in reverse order, so bit 3 was set before
bit 2. The bits follow the table identifiers, not the order of the
player's actions — which rules out the competing explanation of a
sequential pickup counter.

## What is in here

| Path | Contents |
|---|---|
| `data/locations_bis.csv` | 685 decoded treasure entries: identifier, type, named item, amount, room, coordinates |
| `data/noms_items.csv` | 204 item names extracted from the ROM |
| `data/noms_zones.csv` | The game's 32 named zones |
| `tools/` | ROM extraction, RAM dumping, diff analysis |
| `formats-bis.md` | Every confirmed structure, with file and line references |
| `reference-mlss.md` | Study of the Superstar Saga world that ships with Archipelago |
| `CLAUDE.md` | Project memory: fixed decisions, constraints, open questions |
| `JOURNAL.md` | Dated log, including the dead ends and the bugs |

### Scale

647 usable treasure entries: 281 `?` blocks, 197 beans, 149 brick
blocks, 20 grass tufts, spread over 272 rooms and 32 named zones. For
comparison, the Superstar Saga world declares 634 locations, so the two
games are the same size.

## Evidence conventions

Every claim in this repository carries one of three labels, and the
rule is enforced throughout:

- **Vérifié / Verified** — read in source code or measured, cited with
  file and line
- **Hypothèse / Hypothesis** — inferred from another game or a pattern,
  not yet confirmed
- **À tester / To test** — nothing settles it either way

Anything without a file-and-line source is a hypothesis, not a fact. A
plausible but wrong memory address costs hours of debugging.

## Reproducing the results

You need your own legally obtained ROM. The static analysis targets one
exact revision:

- Mario & Luigi: Bowser's Inside Story, NDS, North America, pre-DSi
- SHA-256 `9126963d6c6b6f81a9a666ba766e223781ff286634486e2a56d07a4c82eef4f1`

```
py -3.13 -m venv venv
venv\Scripts\python.exe -m pip install ndspy .\vendor\mnllib.py
venv\Scripts\python.exe tools\extract_names.py
venv\Scripts\python.exe tools\build_location_table.py
```

For the live measurement, open `tools/dump_ram.lua` in the Lua console
of BizHawk **2.10 exactly** — the Archipelago Lua connector refuses
anything older than 2.7.0 and warns above 2.10 — then compare dumps
with `tools/cherche_champ_bits.py`.

## About the ROM

**No ROM is included in this repository, and none will be provided.**
The `.gitignore` excludes `.nds`, `.7z`, `.zip` and save files. Every
table under `data/` is regenerated from a local ROM you supply
yourself; nothing was entered by hand.

## Credits

This work stands entirely on prior community research:

- The [MnL-Modding](https://github.com/MnL-Modding) ecosystem —
  Randoglobin for the treasure and item tables, Cheatoglobin for the
  save structure, `mnllib` for the internal formats, BIS-docs for the
  script commands
- [Archipelago](https://github.com/ArchipelagoMW/Archipelago), and in
  particular its bundled `worlds/mlss`, the Superstar Saga world, which
  had already solved this class of problem for the first game in the
  series

Randoglobin and Cheatoglobin are GPL-3.0-or-later. They were **read to
understand**, and facts were drawn from them — offsets, file formats,
field layouts. **No code was copied.** Reusing their code would impose
the GPL on the resulting APWorld.
