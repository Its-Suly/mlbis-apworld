"""Extrait la table des 10 Bros Attacks depuis l'overlay 123.

Lecture seule de la ROM, aucune ecriture.

Pourquoi cette table. Une piece d'attaque est une `location` (bits Exxx),
et l'attaque elle-meme est un `item` a livrer. Cette table donne, pour
chaque attaque, la variable qui compte ses pieces et la variable qui
marque son deblocage. C'est la correspondance dont le pool d'items a
besoin.

Structure, lue dans vendor/randoglobin/randoglobin/special.py lignes 25
a 40 : 10 entrees de 18 octets, `struct.unpack('<H2x3H4xH2x')`, soit
[nom de zone, nom de zone, variable de pieces, variable d'attaque,
identifiant d'objet]. Les octets 2-3, 10-13 et 16-17 ne sont pas lus par
Randoglobin ; on les affiche quand meme plutot que de les ignorer.

Offsets, base NA, main.py lignes 1196 et 1197, rom_base 1 :
    table des attaques   overlay 123, offset 0x000304D4
    table d'objets arm9  0x0004EA68, pas 24, index = itemID - 0x1000
                         string_id en tete, cout en SP a +20 (special.py:36)

Les noms de zone indexent MData/mfset_MenuMes.dat, table 2 pour
l'anglais NA, meme convention que tools/extract_names.py.

Verification croisee faite par le script : la table d'objets a 0x4EA68
doit etre celle que le pointeur arm9 des attaques designe deja.

Sortie : data/bros_attacks.csv
"""
import csv
import struct
from pathlib import Path

import ndspy.rom
import ndspy.codeCompression
from mnllib.bis import LanguageTable, TextTable, BIS_ENCODING

RACINE = Path(__file__).resolve().parent.parent
ROM = RACINE / "4171 - Mario & Luigi - Bowser's Inside Story (US)(M3)(XenoPhobia).nds"

OVERLAY_MENU = 123
TABLE_ATTAQUES = 0x000304D4       # main.py:1196, base NA
TABLE_OBJETS_ARM9 = 0x0004EA68    # main.py:1197, base NA
PAS_OBJET = 24                    # special.py:34
NB_ATTAQUES = 10                  # special.py:26
TAILLE_ENTREE = 18

TABLE_POINTEURS = 0x000145C0      # main.py:1169, base NA
TABLE_ANGLAIS = 2                 # extract_names.py:46

rom = ndspy.rom.NintendoDSRom.fromFile(str(ROM))
arm9 = bytes(ndspy.codeCompression.decompress(rom.arm9))

pointeur_attaques = int.from_bytes(arm9[TABLE_POINTEURS:TABLE_POINTEURS + 4], "little")
base_attendue = pointeur_attaques - 0x2004000
if base_attendue != TABLE_OBJETS_ARM9:
    raise SystemExit(
        f"recoupement echoue : le pointeur arm9 des attaques donne "
        f"0x{base_attendue:05X}, Randoglobin annonce 0x{TABLE_OBJETS_ARM9:05X}"
    )
print(f"recoupement : pointeur arm9 des attaques = 0x{base_attendue:05X}, "
      f"conforme a main.py:1197")

overlay = rom.loadArm9Overlays([OVERLAY_MENU])[OVERLAY_MENU].data
print(f"overlay {OVERLAY_MENU} : {len(overlay)} octets")


def entrees(chemin, index, is_dialog=False):
    table = LanguageTable.from_bytes(rom.getFileByName(chemin), is_dialog)
    st = table.text_tables[index]
    if not isinstance(st, TextTable):
        raise SystemExit(f"{chemin} table {index} : {type(st).__name__} au lieu de TextTable")
    out = []
    for brut in st.entries:
        fin = brut.rindex(0xFF) if 0xFF in brut else len(brut)
        out.append(brut[:fin].decode(BIS_ENCODING, "ignore"))
    return out


noms_zones = entrees("MData/mfset_MenuMes.dat", TABLE_ANGLAIS)
noms_attaques = entrees("BData/mfset_AItmN.dat", TABLE_ANGLAIS)
print(f"textes : {len(noms_zones)} entrees de menu, {len(noms_attaques)} noms d'attaque")


def texte(liste, i):
    return liste[i] if 0 <= i < len(liste) else f"<hors table {i}>"


lignes = []
print()
print(f"{'#':>2}  {'attaque':<16} {'item':>6} {'pieces':>7} {'unlock':>7} {'SP':>3}  zone")
for i in range(NB_ATTAQUES):
    debut = TABLE_ATTAQUES + i * TAILLE_ENTREE
    brut = overlay[debut:debut + TAILLE_ENTREE]
    zone_a, zone_b, var_pieces, var_attaque, id_objet = struct.unpack("<H2x3H4xH2x", brut)

    record = TABLE_OBJETS_ARM9 + (id_objet - 0x1000) * PAS_OBJET
    string_id = int.from_bytes(arm9[record:record + 2], "little")
    cout_sp = int.from_bytes(arm9[record + 20:record + 22], "little")

    nom = texte(noms_attaques, string_id)
    print(f"{i:>2}  {nom:<16} 0x{id_objet:04X} 0x{var_pieces:04X}  0x{var_attaque:04X} "
          f"{cout_sp:>3}  {texte(noms_zones, zone_a)} / {texte(noms_zones, zone_b)}")

    lignes.append({
        "index": i,
        "nom": nom,
        "item_brut": f"0x{id_objet:04X}",
        "var_pieces": f"0x{var_pieces:04X}",
        "var_attaque": f"0x{var_attaque:04X}",
        "cout_sp": cout_sp,
        "zone_a": texte(noms_zones, zone_a),
        "zone_b": texte(noms_zones, zone_b),
        "string_id": string_id,
        "octets_bruts": brut.hex(),
    })

print()
print("octets non lus par Randoglobin, offsets 2-3, 10-13 et 16-17 :")
for l in lignes:
    b = bytes.fromhex(l["octets_bruts"])
    print(f"  {l['nom']:<16} 2-3 {b[2:4].hex()}  10-13 {b[10:14].hex()}  16-17 {b[16:18].hex()}")

(RACINE / "data").mkdir(exist_ok=True)
sortie = RACINE / "data" / "bros_attacks.csv"
with open(sortie, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(lignes[0].keys()))
    w.writeheader()
    w.writerows(lignes)
print(f"\necrit : data/bros_attacks.csv  ({len(lignes)} attaques)")
