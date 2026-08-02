"""Construit la table des locations candidates a partir de TreasureInfo.dat.

Lecture seule de la ROM, aucune ecriture.

Decodage :
  - bitfield et treasure_type : Randoglobin/randoglobin/data_classes.py 38-43
    et Randoglobin/randoglobin/treasure.py 328-331
  - type d'item : item >> 12, d'apres set_item_prices dans treasure.py 290-304
    1 objet d'attaque, 2 consommable, 3 badge, 4 equipement
  - pieces : item > 0xEFFF, montant [1,5,10,50,100][quantity] * max_hits,
    d'apres to_script_command dans data_classes.py 83-87
  - autres objets : quantite (quantity + 1) * max_hits, meme source
  - regroupement en salles : bit is_last_entry_in_room ferme la salle

Sortie : data/locations_bis.csv
"""
import csv
import struct
from collections import Counter
from pathlib import Path

import ndspy.rom

RACINE = Path(__file__).resolve().parent.parent
ROM = RACINE / "4171 - Mario & Luigi - Bowser's Inside Story (US)(M3)(XenoPhobia).nds"
SORTIE = RACINE / "data" / "locations_bis.csv"

TYPES_TRESOR = {
    0: "haricot",
    1: "bloc ?",
    4: "bloc brique",
    5: "touffe d'herbe",
    7: "bloc brique variante",
}
TYPES_ITEM = {1: "attaque", 2: "consommable", 3: "badge", 4: "equipement"}
VALEURS_PIECE = [1, 5, 10, 50, 100]

rom = ndspy.rom.NintendoDSRom.fromFile(str(ROM))
data = rom.getFileByName("Treasure/TreasureInfo.dat")

# Noms produits par tools/extract_names.py. Facultatif : sans le fichier,
# la colonne reste vide plutot que de faire echouer le dump.
NOMS = {}
fichier_noms = RACINE / "data" / "noms_items.csv"
if fichier_noms.exists():
    with open(fichier_noms, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            NOMS[r["item_brut"]] = r["nom"]
else:
    print("data/noms_items.csv absent, colonne nom_item vide. "
          "Lancer tools/extract_names.py d'abord.")

lignes = []
salle = 0
for index in range(685):  # borne : premiere entree nulle
    bitfield, item, ident, x, y, z = struct.unpack("<6H", data[index * 12:(index + 1) * 12])
    dernier = bitfield & 0b1
    type_tresor = (bitfield >> 1) & 0b1111
    max_hits = (bitfield >> 5) & 0b11111
    quantity = (bitfield >> 10) & 0b11111

    if item > 0xEFFF:
        type_item = "pieces"
        id_item = ""
        montant = VALEURS_PIECE[quantity] * max_hits if quantity < 5 else ""
    elif item == 0:
        type_item = "vide"
        id_item = ""
        montant = ""
    else:
        type_item = TYPES_ITEM.get(item >> 12, f"inconnu_{item >> 12}")
        id_item = item & 0xFFF
        montant = (quantity + 1) * max_hits

    lignes.append({
        "index": index,
        "salle": salle,
        "identifiant": ident,
        "type_tresor": TYPES_TRESOR.get(type_tresor, f"inconnu_{type_tresor}"),
        "type_tresor_brut": type_tresor,
        "type_item": type_item,
        "item_brut": f"0x{item:04X}",
        "id_item": id_item,
        "nom_item": NOMS.get(f"0x{item:04X}", "pieces" if type_item == "pieces" else ""),
        "montant": montant,
        "max_hits": max_hits,
        "quantity": quantity,
        "x": x, "y": y, "z": z,
        "exploitable": int(item != 0),
    })
    if dernier:
        salle += 1

SORTIE.parent.mkdir(exist_ok=True)
with open(SORTIE, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(lignes[0].keys()))
    w.writeheader()
    w.writerows(lignes)

exploitables = [l for l in lignes if l["exploitable"]]
print(f"ecrit : {SORTIE.relative_to(RACINE)}")
print(f"entrees totales {len(lignes)}, exploitables {len(exploitables)}")
print(f"salles distinctes : {salle + (0 if lignes[-1]['salle'] == salle else 1)}")
print()
print("repartition par type d'item (exploitables) :")
for t, n in Counter(l["type_item"] for l in exploitables).most_common():
    print(f"  {t:14s} {n:5d}")
print()
tailles = Counter(l["salle"] for l in exploitables)
print(f"salles contenant au moins un tresor exploitable : {len(tailles)}")
print(f"tresors par salle : min {min(tailles.values())}, max {max(tailles.values())}, "
      f"moyenne {sum(tailles.values()) / len(tailles):.1f}")
print()
print("les 12 salles les plus fournies :")
for s, n in tailles.most_common(12):
    print(f"  salle {s:3d} : {n:2d} tresors")
