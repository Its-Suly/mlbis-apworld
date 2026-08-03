"""Genere mlbis/data.py depuis data/locations_bis.csv.

Rien n'est saisi a la main : le monde se regenere entierement depuis la
ROM, via extract_names.py puis build_location_table.py puis ce script.

Choix d'identifiants, A FIGER avant la premiere seed publiee :

    BASE_ID = 0xB15000
    location d'un tresor de TreasureInfo.dat  ->  BASE_ID + identifiant
    identifiants 0 a 757 utilises, 758 a 1023 laisses libres
    BASE_ID + 1024 et au-dela  ->  locations hors TreasureInfo.dat

Le decalage reproduit volontairement l'espace d'index du tableau Exxx,
dont les tresors occupent 0 a 1023 d'apres le decoupage de la
communaute. Un identifiant de location se lit donc directement comme un
index de bit, sans table de correspondance.

Usage :
    venv\\Scripts\\python.exe tools\\build_apworld_data.py
"""
import csv
from collections import Counter
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
LOCATIONS = RACINE / "data" / "locations_bis.csv"
SORTIE = RACINE / "mlbis" / "data.py"

BASE_ID = 0xB15000
RESERVE_HORS_TABLE = 1024

# Les noms de location sont en anglais, comme la ROM NA et comme les
# autres mondes Archipelago. Ils sont provisoires tant que la
# correspondance salle -> zone nommee n'est pas etablie.
TYPES_EN = {
    "bloc ?": "Block",
    "bloc brique": "Brick",
    "bloc brique variante": "Brick",
    "haricot": "Bean",
    "touffe d'herbe": "Grass",
}

lignes = []
with open(LOCATIONS, encoding="utf-8") as f:
    for r in csv.DictReader(f):
        if r["exploitable"] != "1":
            continue
        lignes.append(r)

lignes.sort(key=lambda r: int(r["identifiant"]))

tresors = []
noms_vus = Counter()
for r in lignes:
    ident = int(r["identifiant"])
    type_en = TYPES_EN.get(r["type_tresor"], "Treasure")
    nom_location = f"{type_en} {ident}"
    noms_vus[nom_location] += 1

    if r["type_item"] == "pieces":
        item = f"{r['montant']} Coins"
    else:
        item = r["nom_item"]
    tresors.append((ident, nom_location, item, int(r["salle"])))

doublons = [n for n, c in noms_vus.items() if c > 1]
if doublons:
    raise SystemExit(f"noms de location en double : {doublons[:5]}")

maxi = max(t[0] for t in tresors)
if maxi >= RESERVE_HORS_TABLE:
    raise SystemExit(
        f"identifiant {maxi} au-dela de la reserve {RESERVE_HORS_TABLE}, "
        f"le plan d'identifiants ne tient plus"
    )

items = Counter(t[2] for t in tresors)

lignes_py = [
    '"""Donnees du monde, GENEREES. Ne pas editer a la main.',
    "",
    "Regenerer avec tools/build_apworld_data.py, qui lit",
    "data/locations_bis.csv, lui-meme regenere depuis la ROM.",
    '"""',
    "",
    f"BASE_ID = {BASE_ID:#x}",
    f"RESERVE_HORS_TABLE = {RESERVE_HORS_TABLE}",
    "",
    "# (identifiant TreasureInfo, nom de location, item d'origine, salle)",
    "TREASURES = [",
]
for ident, nom, item, salle in tresors:
    lignes_py.append(f"    ({ident}, {nom!r}, {item!r}, {salle}),")
lignes_py.append("]")
lignes_py.append("")
lignes_py.append("# nom d'item -> nombre d'exemplaires dans le jeu d'origine")
lignes_py.append("VANILLA_ITEMS = {")
for nom, n in sorted(items.items()):
    lignes_py.append(f"    {nom!r}: {n},")
lignes_py.append("}")
lignes_py.append("")

SORTIE.parent.mkdir(exist_ok=True)
SORTIE.write_text("\n".join(lignes_py), encoding="utf-8")

print(f"ecrit : {SORTIE.relative_to(RACINE)}")
print(f"  {len(tresors)} locations, identifiants {tresors[0][0]} a {maxi}")
print(f"  {len(items)} items distincts, {sum(items.values())} exemplaires")
print(f"  plage de location : {BASE_ID:#x} a {BASE_ID + maxi:#x}")
print(f"  libre pour le hors-table : {BASE_ID + RESERVE_HORS_TABLE:#x} et au-dela")
