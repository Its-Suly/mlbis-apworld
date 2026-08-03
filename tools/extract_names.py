"""Extrait les noms d'objets et de zones depuis la ROM, en anglais NA.

Lecture seule de la ROM, aucune ecriture.

CORRIGE LE 4 AOUT 2026. La version precedente supposait que l'identifiant
d'un objet valait sa position dans la table de texte, divisee par le pas
des triplets. C'est FAUX, et ca produisait des noms decales : 129 noms
d'equipement sur 129 etaient errones, 22 attaques sur 28, 20
consommables. Detail dans JOURNAL.md.

La verite, lue dans vendor/Randoglobin/randoglobin/treasure.py lignes 135
a 142 : l'identifiant indexe une table d'enregistrements de l'arm9
DECOMPRESSE, et c'est cette table qui porte le numero de chaine.

    item      = (type << 12) | id
    pointeurs = 4 mots a l'offset 0x000145C0 de l'arm9 decompresse
                (main.py:1169, base NA)
    adresse   = pointeur - 0x2004000
    record    = adresse + id * [24, 24, 16, 32][type - 1]
    string_id = u16 en tete du record
    nom       = entrees_de_texte[string_id]      (pluriel a string_id + 1,
                                                  treasure.py:162)

L'arm9 doit etre decompresse, sinon l'offset n'existe pas : le brut fait
219452 octets, le decompresse 341144. Methode main.py:391,
ndspy.codeCompression.decompress.

Indices de langue etablis par inspection le 2 aout 2026 :
  - tables d'objets, is_dialog=False, l'anglais NA est la table 2
    (table 3 francais, table 6 espagnol, verifie sur 'Mushroom' /
    'Champignon' / 'Champinon')
  - table des zones, is_dialog=True, l'anglais est la table 0x44

Sortie : data/noms_items.csv et data/noms_zones.csv
"""
import csv
from io import BytesIO
from pathlib import Path

import ndspy.rom
import ndspy.codeCompression
from mnllib.bis import LanguageTable, TextTable, BIS_ENCODING

RACINE = Path(__file__).resolve().parent.parent
ROM = RACINE / "4171 - Mario & Luigi - Bowser's Inside Story (US)(M3)(XenoPhobia).nds"
TABLE_ANGLAIS_ITEMS = 2
TABLE_ANGLAIS_ZONES = 0x44

TABLE_POINTEURS = 0x000145C0      # main.py:1169, base NA
PAS_RECORD = [24, 24, 16, 32]     # treasure.py:140, indexe par type - 1

# type : (libelle, fichier de noms, nombre d'objets, source de ce nombre)
#
# Les trois derniers comptes sont corrobores par Cheatoglobin, qui les
# tient de son cote : constants.py ligne 85 ITEM_DATA 26 entrees,
# ligne 114 GEAR_DATA 129, ligne 264 BADGE_NAMES 8. Les 26 consommables
# se recoupent en plus avec les 26 compteurs de la sauvegarde et avec
# l'ecart entre deux tables de l'arm9, (0x4EA68 - 0x4E7F8) / 24 = 26.
#
# Le compte des attaques est le seul sans source externe : 28 est la
# borne au-dela de laquelle le string_id lu sort de la table de texte.
TABLES_ITEMS = {
    1: ("attaque", "BData/mfset_AItmN.dat", 28, "borne string_id"),
    2: ("consommable", "BData/mfset_UItmN.dat", 26, "Cheatoglobin ITEM_DATA"),
    3: ("badge", "BData/mfset_BadgeN.dat", 8, "Cheatoglobin BADGE_NAMES"),
    4: ("equipement", "BData/mfset_WearN.dat", 129, "Cheatoglobin GEAR_DATA"),
}

rom = ndspy.rom.NintendoDSRom.fromFile(str(ROM))
arm9 = bytes(ndspy.codeCompression.decompress(rom.arm9))
print(f"arm9 : {len(rom.arm9)} octets brut, {len(arm9)} decompresse")

pointeurs = [
    int.from_bytes(arm9[TABLE_POINTEURS + i * 4:TABLE_POINTEURS + i * 4 + 4], "little")
    for i in range(4)
]
print("tables d'objets :", ", ".join(f"0x{p:07X}" for p in pointeurs))


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
for type_item, (libelle, chemin, nb_objets, source) in TABLES_ITEMS.items():
    noms = entrees(chemin, TABLE_ANGLAIS_ITEMS, False)
    base = pointeurs[type_item - 1] - 0x2004000
    pas = PAS_RECORD[type_item - 1]
    print(f"{libelle:12s} : table arm9 a 0x{base:05X}, pas {pas}, "
          f"{nb_objets:3d} objets ({source}), {len(noms):3d} entrees de texte")

    for id_item in range(nb_objets):
        record = base + id_item * pas
        string_id = int.from_bytes(arm9[record:record + 2], "little")
        if string_id >= len(noms):
            raise SystemExit(
                f"{libelle} id {id_item} : string_id {string_id} hors de la "
                f"table de texte ({len(noms)} entrees). Le nombre d'objets "
                f"ou le pas est faux."
            )
        lignes.append({
            "item_brut": f"0x{(type_item << 12) | id_item:04X}",
            "type_item_brut": type_item,
            "type_item": libelle,
            "id_item": id_item,
            "string_id": string_id,
            "nom": noms[string_id],
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
