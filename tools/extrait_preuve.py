"""Extrait la preuve du champ de bits, sous une forme publiable.

Les dumps font 4 Mo chacun et sont exclus du depot. Sans eux, personne ne
peut verifier l'affirmation centrale du projet. Ce script en tire les
95 octets du champ, pour les cinq dumps, dans un fichier texte de quelques
kilooctets.

Usage :
    venv\\Scripts\\python.exe tools\\extrait_preuve.py

Sortie : data/preuve_champ_bits.txt
"""
import csv
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
DUMPS = RACINE / "dumps"
BASE = 0x0560C8
TAILLE = 95  # 758 identifiants
SORTIE = RACINE / "data" / "preuve_champ_bits.txt"

runs = sorted(DUMPS.glob("run??_Main_RAM.bin"))
if not runs:
    raise SystemExit(f"Aucun dump dans {DUMPS}. Voir tools/dump_ram.lua.")

noms = {}
fichier = RACINE / "data" / "locations_bis.csv"
if fichier.exists():
    with open(fichier, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["exploitable"] == "1":
                nom = r["nom_item"] if r["nom_item"] != "pieces" else f"{r['montant']} coins"
                noms[int(r["identifiant"])] = (r["type_tresor"], nom)

lignes = []
lignes.append("Champ de bits des tresors ramasses / collected-treasure bitfield")
lignes.append("=" * 70)
lignes.append("")
lignes.append(f"Domaine  : Main RAM (BizHawk 2.10, coeur NDS)")
lignes.append(f"Base     : 0x{BASE:06X}")
lignes.append(f"Taille   : {TAILLE} octets, 758 identifiants")
lignes.append(f"Formule  : identifiant N -> octet 0x{BASE:06X} + N//8, bit N%8, LSB en premier")
lignes.append("")
lignes.append("Les dumps de 4 Mo dont sont tires ces octets ne sont pas publies.")
lignes.append("Ils se regenerent avec tools/dump_ram.lua. Voir README.md.")
lignes.append("")

for chemin in runs:
    data = chemin.read_bytes()
    champ = data[BASE:BASE + TAILLE]
    actifs = []
    for i, octet in enumerate(champ):
        for j in range(8):
            if octet >> j & 1:
                actifs.append(i * 8 + j)
    lignes.append("-" * 70)
    lignes.append(f"{chemin.name}")
    lignes.append("")
    for offset in range(0, TAILLE, 16):
        bloc = champ[offset:offset + 16]
        lignes.append(f"  0x{BASE + offset:06X}  {bloc.hex(' ')}")
    lignes.append("")
    if actifs:
        lignes.append(f"  identifiants a 1 : {actifs}")
        for n in actifs:
            t, nom = noms.get(n, ("?", "?"))
            lignes.append(f"     {n:4d}  octet 0x{BASE + n // 8:06X} bit {n % 8}   {t} {nom!r}")
    else:
        lignes.append("  identifiants a 1 : aucun")
    lignes.append("")

SORTIE.parent.mkdir(exist_ok=True)
SORTIE.write_text("\n".join(lignes), encoding="utf-8")
print(f"ecrit : {SORTIE.relative_to(RACINE)}  ({len(runs)} dumps, {SORTIE.stat().st_size} octets)")
print()
print("\n".join(lignes[-14:]))
