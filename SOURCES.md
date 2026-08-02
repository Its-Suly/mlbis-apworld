# Sources and attribution

*Sources et attribution. Ce fichier est en anglais pour être lisible par
les auteurs des projets cités, qui sont internationaux.*

Every finding in this repository rests on prior community work. This
file lists what was used, where it came from, under which licence, and
exactly what was taken from it.

Commit hashes are the revisions actually consulted, so that anyone can
check a claim against the same code we read.

## Community

**MnL-Modding Discord** — <https://discord.gg/rhJ6HGyymJ>

The hub for Mario & Luigi modding. Link taken from the BIS-docs site
configuration, `hugo/hugo.yaml` line 35. Every tool below comes from
this community.

**Archipelago** — <https://archipelago.gg>

## Code and data sources

### Archipelago

- Repository: <https://github.com/ArchipelagoMW/Archipelago>
- Licence: MIT
- Revision consulted: `72dbfcc1d367df4dd03681052e845b4e9f5a93af` (2026-07-20), release 0.6.8

Used for:

- `worlds/mlss`, the Mario & Luigi: Superstar Saga world, **studied as
  the reference model**. Same series, same studio. Our
  `reference-mlss.md` is a study of it, with file and line references.
  No code copied.
- `data/lua/connector_bizhawk_generic.lua` — the authoritative
  reference for the BizHawk Lua memory API used by `tools/dump_ram.lua`
  (`memory.read_bytes_as_array`, `memory.getmemorydomainsize`), and for
  the emulator version constraint at lines 633-638.
- `data/lua/base64.lua` line 61 — confirms that byte arrays returned by
  the memory API are 1-indexed.

### Randoglobin

- Repository: <https://github.com/MnL-Modding/Randoglobin>
- Licence: **GPL-3.0-or-later**
- Revision consulted: `b40481cbe5f5157bc56788efd026dadebc6d234c` (2026-04-05)

A standalone randomizer for this game. **Read to understand, never
copied.** Facts drawn from it:

- `randoglobin/data_classes.py` lines 38-43 — layout of the
  `TreasureInfo.dat` bitfield: `is_last_entry_in_room`, `treasure_type`,
  `max_hits`, `quantity`
- `randoglobin/data_classes.py` lines 83-87 — how coin amounts encode
- `randoglobin/treasure.py` lines 328-331 — meaning of `treasure_type`
- `randoglobin/treasure.py` lines 290-304 — item type from `item >> 12`
- `randoglobin/main.py` line 929 — location of `Treasure/TreasureInfo.dat`
- `randoglobin/main.py` lines 960-1000 — method for reading the ROM text
  tables
- `randoglobin/mnlscript_skips.py` lines 535, 1568 — actor variable
  field, and the Vacuum Block progression flag
- `randoglobin/palette.py` lines 743-778 — established that
  `EObjSave.dat` holds palettes, not save state

### Cheatoglobin

- Repository: <https://github.com/MnL-Modding/Cheatoglobin>
- Licence: **GPL-3.0-or-later**
- Revision consulted: `daa427311f50995b6cc2cff5fa96cf867157fb9a` (2025-06-16)

A save editor. **Read to understand, never copied.** The entire save
file layout in `formats-bis.md` comes from `cheatoglobin/window.py`,
cited line by line: magic, slot offsets, checksum algorithm, backup
copy.

### mnllib.py

- Repository: <https://github.com/MnL-Modding/mnllib.py>
- Licence: **LGPL-3.0-or-later**
- Revision consulted: `d31d92522a7e2774b1f28db20f0e346a5201738b` (2025-07-11)

Unlike the two above, this one is **actually imported as a dependency**
by `tools/extract_names.py`, for `LanguageTable`, `TextTable` and
`BIS_ENCODING`. The LGPL permits this: using an unmodified library
through its public interface does not impose copyleft on the calling
code. `mnllib/bis/text.py` lines 100-107 also documents that
`text_tables` mixes parsed objects and raw bytes.

### BIS-docs

- Repository: <https://github.com/MnL-Modding/BIS-docs>
- Site: <https://mnl-modding.github.io/BIS-docs/>
- Licences: **GPL-3.0 for the code** (`LICENSE.code`), **CC BY-SA 4.0
  for the documentation** (`LICENSE.docs`)
- Revision consulted: `ec5f05f4c541c358596bf5eaa70f287c8e9118cd` (2025-06-17)

Documentation of the game's internals. Used for the script command
table location in `overlay_0006.bin`, the shared command range, and the
`0x0043` / `0x0044` item commands, all regenerated from
`cutscene_code/bisdocs.py`.

The CC BY-SA 4.0 licence on the documentation requires attribution,
which this file provides. Note that the copy of the command
documentation circulating on the MnL-Modding Google Drive dates from
September 2024 and is **out of date** — regenerate from `bisdocs.py`.

### BizHawk

- Repository: <https://github.com/TASEmulators/BizHawk>
- Version used: tag `2.10`, exactly

Not a source of facts, but the measurement instrument. The version is
pinned because the Archipelago Lua connector refuses anything below
2.7.0 and warns above 2.10.

### ndspy

- Repository: <https://github.com/RoadrunnerWMC/ndspy>

Imported by the extraction tools to read the ROM filesystem. Same role
as in Cheatoglobin and Randoglobin.

## On licences

Randoglobin and Cheatoglobin are GPL-3.0-or-later. They were read to
understand how the game stores its data. **Facts — offsets, file
formats, field layouts — were taken; no source code was.** Copying
their code would impose the GPL on any resulting APWorld, which is a
deliberate design constraint of this project, recorded in `CLAUDE.md`.

If you believe any part of this repository reproduces your code rather
than restating a fact learned from it, open an issue and it will be
removed or relicensed.

## On data extracted from the ROM

`data/noms_items.csv` and `data/noms_zones.csv` contain item and place
names read out of a commercial ROM. `data/locations_bis.csv` contains
structural data — identifiers, types, coordinates.

These are short factual identifiers, published for interoperability, in
the same way Archipelago itself ships the item and location names of
the games it supports — see `worlds/mlss/Names/LocationName.py` in the
Archipelago repository, which is distributed under MIT.

**No ROM, no ROM fragment, and no link to one is present in this
repository, and none will be provided.** Every table here regenerates
from a ROM you supply yourself. If a rights holder objects to the
presence of these name tables, open an issue and they will be removed;
the tools that regenerate them are enough to keep the project working.

## Verification

`data/preuve_champ_bits.txt` holds the 95 bytes of the treasure
bitfield across the five RAM dumps that established the central result.
The full 4 MB dumps are not published; regenerate them with
`tools/dump_ram.lua`.
