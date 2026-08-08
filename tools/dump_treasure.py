"""Dump read-only de Treasure/TreasureInfo.dat.

N'ecrit JAMAIS dans la ROM : ndspy charge en memoire, on ne fait pas .saveToFile().
Decodage du bitfield d'apres Randoglobin/randoglobin/data_classes.py lignes 38 a 43.
"""
import struct
from pathlib import Path
import sys
from collections import Counter

import ndspy.rom

RACINE = Path(__file__).resolve().parent.parent
ROM = RACINE / "4171 - Mario & Luigi - Bowser's Inside Story (US)(M3)(XenoPhobia).nds"

rom = ndspy.rom.NintendoDSRom.fromFile(ROM)
print(f"nom interne ROM : {rom.name!r}   idCode : {rom.idCode!r}")

data = rom.getFileByName('Treasure/TreasureInfo.dat')
print(f"TreasureInfo.dat : {len(data)} octets, soit {len(data) / 12} entrees de 12 octets")
print()

TYPE_NAMES = {
    0: "haricot",
    1: "bloc ?",
    4: "bloc brique",
    5: "touffe d'herbe",
    7: "bloc brique (variante)",
}

entries = []
i = 0
first_empty = None
while (i + 1) * 12 <= len(data):
    raw = data[i * 12:(i + 1) * 12]
    if raw == bytes(12) and first_empty is None:
        first_empty = i
    bitfield, item = struct.unpack('<HH', raw[:4])
    entries.append({
        "index": i,
        "raw": raw,
        "is_last_in_room": bitfield & 0b1,
        "type": (bitfield >> 1) & 0b1111,
        "max_hits": (bitfield >> 5) & 0b11111,
        "quantity": (bitfield >> 10) & 0b11111,
        "item": item,
        "tail": raw[4:],
    })
    i += 1

print(f"premiere entree entierement nulle : index {first_empty}")
print(f"total d'entrees dans le fichier   : {len(entries)}")
print()

# Randoglobin s'arrete a la premiere entree nulle. On compte les deux facons.
stop = first_empty if first_empty is not None else len(entries)
live = [e for e in entries[:stop] if e["item"] != 0]

print(f"entrees avant la premiere nulle   : {stop}")
print(f"dont item != 0 (donc exploitables): {len(live)}")
print()

print("repartition par treasure_type (entrees exploitables) :")
for t, n in sorted(Counter(e["type"] for e in live).items()):
    print(f"  type {t:2d}  {TYPE_NAMES.get(t, 'INCONNU'):24s} {n:5d}")
print()

print("repartition par max_hits :")
for h, n in sorted(Counter(e["max_hits"] for e in live).items()):
    print(f"  max_hits {h:2d} : {n:5d}")
print()

print("les 8 octets de queue, sont-ils utilises ?")
tails_nonzero = sum(1 for e in live if e["tail"] != bytes(8))
print(f"  entrees avec queue non nulle : {tails_nonzero} / {len(live)}")
print()

print("10 premieres entrees exploitables, brut :")
for e in live[:10]:
    print(f"  #{e['index']:4d} {e['raw'].hex(' ')}  type={e['type']:2d} "
          f"hits={e['max_hits']:2d} qty={e['quantity']:2d} item=0x{e['item']:04X} "
          f"last={e['is_last_in_room']}")
