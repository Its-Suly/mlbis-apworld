"""Etablit la correspondance salle -> zone nommee, et tresor -> salle.

C'est le verrou qui empechait d'avoir de vraies region : le numero de
salle de locations_bis.csv est un regroupement dans l'ordre du fichier,
et les 32 zones de mfset_EMesPlace.dat sont une autre numerotation.

Chaine lue dans vendor/Randoglobin/randoglobin/treasure.py lignes 396 a
425, offsets dans main.py lignes 1035, 1036, 1046, 1089 et 1169 a 1172,
structure MapMetadata dans data_classes.py lignes 89 a 97. Base NA.

    pour chaque carte j de 0 a 0x2A8 :
      overlay3[map_group + j*20 + 16]        -> treasure_index (u32)
      overlay4[treasure_data + 4 + ti*4]     -> debut, fin dans TreasureInfo
      overlay3[map_metadata + j*12]          -> select_map = (u32[0] >> 2) & 0x3FF
      overlay129, 0x23 entrees de 12 octets  -> si select_map figure dans
        les 3 u16 a +4, alors le u16 a +0 indexe les noms de zone
      sinon, zone 0xA : l'interieur du lac Blubble n'est pas liste sur
        l'ecran de selection de fichier, d'ou viennent ces chaines

Un tresor d'index i appartient a la carte j si debut <= i*12 < fin.

Sortie : data/salles_zones.csv
"""
import csv
import struct
from pathlib import Path

import ndspy.rom

RACINE = Path(__file__).resolve().parent.parent
ROM = RACINE / "4171 - Mario & Luigi - Bowser's Inside Story (US)(M3)(XenoPhobia).nds"
SORTIE = RACINE / "data" / "salles_zones.csv"

NB_CARTES = 0x2A9
MAP_METADATA = 0x000098A0     # overlay 3
MAP_GROUP = 0x19FD0           # overlay 3, overlay_FMap_offsets[1]
TREASURE_DATA = 0x0004AA30    # overlay 4
MAP_ICON_DATA = 0x0000864C    # overlay 129
NB_ICONES = 0x23
ZONE_DEFAUT = 0xA             # interieur du lac Blubble

rom = ndspy.rom.NintendoDSRom.fromFile(str(ROM))
overlays = rom.loadArm9Overlays([3, 4, 129])
ov3 = overlays[3].data
ov4 = overlays[4].data
ov129 = overlays[129].data
print(f"overlays : 3 = {len(ov3)} octets, 4 = {len(ov4)}, 129 = {len(ov129)}")

zones = {}
with open(RACINE / "data" / "noms_zones.csv", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        zones[int(r["index"])] = r["nom"]

# index d'icone -> index de zone, et les select_map qu'elle couvre
icones = []
for k in range(NB_ICONES):
    off = MAP_ICON_DATA + k * 12
    index_zone = int.from_bytes(ov129[off:off + 2], "little")
    couverts = struct.unpack("<HHH", ov129[off + 4:off + 10])
    icones.append((index_zone, couverts))


def zone_de(select_map):
    for index_zone, couverts in icones:
        if select_map in couverts:
            return index_zone
    return ZONE_DEFAUT


lignes = []
for j in range(NB_CARTES):
    off = MAP_GROUP + j * 20 + 16
    treasure_index = int.from_bytes(ov3[off:off + 4], "little")
    if treasure_index == 0xFFFFFFFF:
        continue

    off = TREASURE_DATA + 4 + treasure_index * 4
    debut, fin = struct.unpack("<II", ov4[off:off + 8])

    meta = struct.unpack("<III", ov3[MAP_METADATA + j * 12:MAP_METADATA + j * 12 + 12])
    select_map = (meta[0] >> 2) & 0x3FF
    index_zone = zone_de(select_map)

    lignes.append({
        "carte": j,
        "select_map": select_map,
        "index_zone": index_zone,
        "zone": zones.get(index_zone, f"?{index_zone}"),
        "tresor_debut": debut // 12,
        "tresor_fin": fin // 12,
        "nb_tresors": (fin - debut) // 12,
        "musique": meta[2] >> 12,
    })

SORTIE.parent.mkdir(exist_ok=True)
with open(SORTIE, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(lignes[0].keys()))
    w.writeheader()
    w.writerows(lignes)

print(f"ecrit : {SORTIE.relative_to(RACINE)}")
print(f"  {len(lignes)} cartes portent des tresors sur {NB_CARTES}")
print(f"  {sum(l['nb_tresors'] for l in lignes)} entrees de tresor couvertes")

par_zone = {}
for l in lignes:
    par_zone.setdefault(l["zone"], [0, 0])
    par_zone[l["zone"]][0] += 1
    par_zone[l["zone"]][1] += l["nb_tresors"]
print(f"\n  {len(par_zone)} zones distinctes :")
for zone, (cartes, tresors) in sorted(par_zone.items(), key=lambda kv: -kv[1][1]):
    print(f"    {zone:24s} {cartes:3d} cartes, {tresors:4d} tresors")
