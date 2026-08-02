"""Extrait les noms d'objets et de zones depuis la ROM, en anglais NA.

Lecture seule de la ROM, aucune ecriture.

Methode reprise de Randoglobin/randoglobin/main.py lignes 960 a 1000 :
LanguageTable.from_bytes, puis .text_tables[i].entries, chaque entree se
terminant par 0xFF et se decodant en BIS_ENCODING.

Indices etablis par inspection le 2 aout 2026, pas par deduction :
  - tables d'objets, is_dialog=False, l'anglais NA est la table 2
    (table 3 francais, table 6 espagnol, verifie sur 'Mushroom' /
    'Champignon' / 'Champinon')
  - table des zones, is_dialog=True, l'anglais est la table 0x44
    (0x45 francais, 0x48 espagnol)

Pas de generique sur le pas des entrees, il differe par table :
  - attaque : une entree par objet
  - consommable, badge, equipement : triplets singulier / pluriel /
    message 'Full!', donc une entree sur trois

Sortie : data/noms_items.csv et data/noms_zones.csv
"""
import csv
from pathlib import Path

import ndspy.rom
from mnllib.bis import LanguageTable, TextTable, BIS_ENCODING

RACINE = Path(__file__).resolve().parent.parent
ROM = RACINE / "4171 - Mario & Luigi - Bowser's Inside Story (US)(M3)(XenoPhobia).nds"
TABLE_ANGLAIS_ITEMS = 2
TABLE_ANGLAIS_ZONES = 0x44

# type d'item : (libelle, fichier, pas entre deux objets)
TABLES_ITEMS = {
    1: ("attaque", "BData/mfset_AItmN.dat", 1),
    2: ("consommable", "BData/mfset_UItmN.dat", 3),
    3: ("badge", "BData/mfset_BadgeN.dat", 3),
    4: ("equipement", "BData/mfset_WearN.dat", 3),
}

rom = ndspy.rom.NintendoDSRom.fromFile(str(ROM))


def entrees(chemin, index, is_dialog):
    table = LanguageTable.from_bytes(rom.getFileByName(chemin), is_dialog)
    st = table.text_tables[index]
    if not isinstance(st, TextTable):
        raise SystemExit(f"{chemin} table {index} : attendu un TextTable, obtenu {type(st).__name__}")
    resultat = []
    for brut in st.entries:
        fin = brut.rindex(0xFF) if 0xFF in brut else len(brut)
        resultat.append(brut[:fin].decode(BIS_ENCODING, "ignore"))
    return resultat


lignes = []
for type_item, (libelle, chemin, pas) in TABLES_ITEMS.items():
    noms = entrees(chemin, TABLE_ANGLAIS_ITEMS, False)
    retenus = noms[::pas]
    print(f"{libelle:12s} : {len(noms):4d} entrees, pas {pas} -> {len(retenus):3d} objets")
    for id_item, nom in enumerate(retenus):
        lignes.append({
            "item_brut": f"0x{(type_item << 12) | id_item:04X}",
            "type_item_brut": type_item,
            "type_item": libelle,
            "id_item": id_item,
            "nom": nom,
        })

(RACINE / "data").mkdir(exist_ok=True)
sortie_items = RACINE / "data" / "noms_items.csv"
with open(sortie_items, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(lignes[0].keys()))
    w.writeheader()
    w.writerows(lignes)
print(f"\necrit : data/noms_items.csv  ({len(lignes)} objets)")

zones = entrees("EDataSave/mfset_EMesPlace.dat", TABLE_ANGLAIS_ZONES, True)
sortie_zones = RACINE / "data" / "noms_zones.csv"
with open(sortie_zones, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["index", "nom"])
    for i, nom in enumerate(zones):
        w.writerow([i, nom])
print(f"ecrit : data/noms_zones.csv  ({len(zones)} zones)")

print("\nles 32 zones :")
for i, nom in enumerate(zones):
    print(f"  {i:2d}  {nom}")
