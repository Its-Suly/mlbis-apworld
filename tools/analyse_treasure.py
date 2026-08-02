"""Analyse des 8 octets de queue d'une entree TreasureInfo.

Hypothese a tester : octets 4-5 = identifiant unique du tresor,
octets 6-7 / 8-9 / 10-11 = coordonnees X / Y / Z.
"""
import struct
from collections import Counter

import ndspy.rom

ROM = r"C:\Users\sulyv\Documents\Projet BIS\4171 - Mario & Luigi - Bowser's Inside Story (US)(M3)(XenoPhobia).nds"
rom = ndspy.rom.NintendoDSRom.fromFile(ROM)
data = rom.getFileByName('Treasure/TreasureInfo.dat')

rows = []
for i in range(685):  # jusqu'a la premiere entree nulle
    raw = data[i * 12:(i + 1) * 12]
    bitfield, item, f45, f67, f89, fab = struct.unpack('<6H', raw)
    rows.append((i, bitfield, item, f45, f67, f89, fab))

ids = [r[3] for r in rows]
print("=== champ octets 4-5, sur les 685 entrees ===")
print(f"min {min(ids)}  max {max(ids)}  distincts {len(set(ids))}  total {len(ids)}")
manquants = sorted(set(range(min(ids), max(ids) + 1)) - set(ids))
print(f"valeurs manquantes dans l'intervalle : {len(manquants)}")
if manquants[:20]:
    print(f"  premieres manquantes : {manquants[:20]}")
dupes = [v for v, n in Counter(ids).items() if n > 1]
print(f"valeurs en double : {len(dupes)}")
if dupes[:10]:
    print(f"  exemples : {dupes[:10]}")
print()

print("=== les trois derniers champs (hypothese coordonnees) ===")
for nom, idx in (("octets 6-7", 4), ("octets 8-9", 5), ("octets 10-11", 6)):
    vals = [r[idx] for r in rows]
    print(f"{nom} : min {min(vals):6d}  max {max(vals):6d}  distincts {len(set(vals)):5d}"
          f"  multiples de 8 : {sum(1 for v in vals if v % 8 == 0)}/{len(vals)}")
print()

print("=== entrees a item == 0 (ignorees par Randoglobin) : ont-elles un id ? ===")
z = [r for r in rows if r[2] == 0]
print(f"nombre : {len(z)}")
for r in z[:8]:
    print(f"  index {r[0]:4d}  bitfield 0x{r[1]:04X}  id {r[3]:5d}  xyz {r[4]},{r[5]},{r[6]}")
print()

print("=== l'id suit-il l'ordre des salles ? 20 premieres entrees ===")
for r in rows[:20]:
    print(f"  index {r[0]:3d}  id {r[3]:5d}  last_in_room {r[1] & 1}  item 0x{r[2]:04X}")
