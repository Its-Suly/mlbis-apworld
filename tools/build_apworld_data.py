"""Genere mlbis/data.py depuis data/locations_bis.csv et pieces_attaque.csv.

Rien n'est saisi a la main : le monde se regenere entierement depuis la
ROM, via extract_names.py puis build_location_table.py puis ce script.

Choix d'identifiants, A FIGER avant la premiere seed publiee :

    BASE_ID = 0xB15000
    location d'un tresor de TreasureInfo.dat  ->  BASE_ID + identifiant
    identifiants 0 a 757 utilises, 758 a 1023 laisses libres
    BASE_ID + 1024 et au-dela  ->  locations hors TreasureInfo.dat
    piece d'attaque  ->  BASE_ID + rang de bit, 1792 a 2081

La regle est la meme pour les deux familles : l'identifiant de location
vaut BASE_ID plus le rang du bit dans le tableau Exxx. Un identifiant se
lit donc directement comme un index de bit, sans table de correspondance.
Les pieces d'attaque tombent naturellement au-dela de la reserve, leur
plage etant celle de l'histoire.

Usage :
    venv\\Scripts\\python.exe tools\\build_apworld_data.py
"""
import csv
from collections import Counter
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
LOCATIONS = RACINE / "data" / "locations_bis.csv"
PIECES = RACINE / "data" / "pieces_attaque.csv"
NOMS_ITEMS = RACINE / "data" / "noms_items.csv"
ATTAQUES = RACINE / "data" / "bros_attacks.csv"
SORTIE = RACINE / "mlbis" / "data.py"

BASE_ID = 0xB15000
RESERVE_HORS_TABLE = 1024

# Nom du lot de pieces, lu dans l'overlay 123 -> zone nommee du jeu.
#
# Neuf entrees sur dix sont evidentes, le nom du lot reprend celui de la
# zone. Une seule ne l'est pas et elle est etiquetee comme telle.
#
# **Hypothese** pour 'Clinic Pieces' : aucune des 32 zones nommees ne
# s'appelle Toadley Clinic, et la clinique est un batiment de Toad Town.
# Rien ne le prouve dans les donnees, aucune access_rule n'en depend, et
# la corriger ne coutera qu'une ligne ici.
LOT_VERS_ZONE = {
    "Trash Pieces": "Trash Pit",
    "Pump Pieces": "Pump Works",
    "Flab Pieces": "Flab Zone",
    "Energy Pieces": "Energy Hold",
    "Plack Pieces": "Plack Beach",
    "Dimble Pieces": "Dimble Wood",
    "Castle Pieces": "Bowser Castle",
    "Peach Pieces": "Peach's Castle",
    "Clinic Pieces": "Toad Town",       # Hypothese, voir plus haut
    "Toad Pieces": "Toad Town",         # Yoo Who Cannon, aucune piece
}

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
    zone = r["zone"] or "Unknown Area"
    # L'identifiant suffit a l'unicite ; la zone et le type sont la pour
    # que le nom soit lisible par un joueur dans le client Archipelago.
    nom_location = f"{zone} - {type_en} {ident}"
    noms_vus[nom_location] += 1

    if r["type_item"] == "pieces":
        item = f"{r['montant']} Coins"
    else:
        item = r["nom_item"]
    tresors.append((ident, nom_location, item, zone))

doublons = [n for n, c in noms_vus.items() if c > 1]
if doublons:
    raise SystemExit(f"noms de location en double : {doublons[:5]}")

maxi = max(t[0] for t in tresors)
if maxi >= RESERVE_HORS_TABLE:
    raise SystemExit(
        f"identifiant {maxi} au-dela de la reserve {RESERVE_HORS_TABLE}, "
        f"le plan d'identifiants ne tient plus"
    )

# Les regions du monde sont les zones portant au moins un tresor. Une
# piece d'attaque doit tomber dans l'une d'elles, sinon sa region
# n'existe pas.
vues_zones_tresors = []
for _, _, _, zone in tresors:
    if zone not in vues_zones_tresors:
        vues_zones_tresors.append(zone)

# --- pieces d'attaque -------------------------------------------------
#
# Meme forme de tuple que les tresors : (rang de bit, nom, item, zone).
# Le rang de bit tient lieu d'identifiant, comme pour un tresor.
pieces = []
with open(PIECES, encoding="utf-8") as f:
    for r in csv.DictReader(f):
        rang = int(r["rang_bit"])
        attaque = r["attaque"]
        zone = LOT_VERS_ZONE.get(r["lot"])
        if zone is None:
            raise SystemExit(f"lot inconnu, pas de zone : {r['lot']!r}")
        if zone not in vues_zones_tresors:
            raise SystemExit(
                f"la zone {zone!r} ne porte aucun tresor, elle n'existe pas "
                f"comme region. Ajouter la region avant de l'utiliser."
            )
        # Un bloc peut rendre plusieurs pieces d'un coup : Jump Helmet en
        # a deux qui en donnent quatre, Super Bouncer un. Le nom le dit,
        # sinon un joueur croirait avoir perdu six pieces en route.
        indices = [int(x) for x in r["pieces"].split()]
        if len(indices) == 1:
            nom = f"{zone} - {attaque} Piece {indices[0] + 1}"
        else:
            nom = f"{zone} - {attaque} Pieces {indices[0] + 1}-{indices[-1] + 1}"
        pieces.append((rang, nom, f"{attaque} Piece", zone))

pieces.sort(key=lambda p: p[0])

if pieces:
    mini_piece = min(p[0] for p in pieces)
    if mini_piece < RESERVE_HORS_TABLE:
        raise SystemExit(
            f"piece d'attaque au rang {mini_piece}, sous la reserve "
            f"{RESERVE_HORS_TABLE} : collision avec les tresors"
        )

collisions = {t[0] for t in tresors} & {p[0] for p in pieces}
if collisions:
    raise SystemExit(f"identifiants partages : {sorted(collisions)[:5]}")

noms_pieces = Counter(p[1] for p in pieces)
doublons = [n for n, c in noms_pieces.items() if c > 1] + \
           [p[1] for p in pieces if p[1] in noms_vus]
if doublons:
    raise SystemExit(f"noms de location en double : {doublons[:5]}")

items = Counter(t[2] for t in tresors)
items.update(p[2] for p in pieces)

# --- comment livrer chaque item ---------------------------------------
#
# Trois familles seulement dans le pool actuel, et deux d'entre elles ont
# une adresse verifiee. La categorie dit ce que le client doit ecrire, la
# valeur dit ou. Ce qui n'est pas etabli est marque, pas devine.
#
#   'coins'      montant a ajouter au u32 a 02056400        Verifie
#   'consumable' index du compteur, 02056406 + index        Verifie
#   'gear'       identifiant, compteur a 02056427 + id - 1  Verifie
#   'attack_piece'  variable de deblocage de l'attaque      Verifie
#
# Verifie pour les consommables : un Nut ecrit a 02056406 + 7 est apparu
# au menu et s'est consomme, 4 aout 2026, et l'index 7 est bien celui du
# Nut dans data/noms_items.csv. Recoupement independant au run13, index 0
# a 3 et index 16 a 1, soit trois Mushroom et un 1-Up Mushroom.
#
# Verifie pour l'equipement, 5 aout 2026 : 1 ecrit au compteur 4 fait
# apparaitre Heart Wear, identifiant 5. Les 127 compteurs couvrent donc
# les identifiants 1 a 127, et les deux objets sans compteur sont
# « No gear » et « Rental Shell », qui n'ont pas a etre stockes.
par_nom = {}
with open(NOMS_ITEMS, encoding="utf-8") as f:
    for r in csv.DictReader(f):
        par_nom.setdefault(r["type_item"], {})[r["nom"]] = int(r["id_item"])

deblocage = {}
with open(ATTAQUES, encoding="utf-8") as f:
    for r in csv.DictReader(f):
        deblocage[f"{r['nom']} Piece"] = int(r["var_attaque"], 16)

livraison = {}
for nom in sorted(items):
    if nom.endswith(" Coins"):
        livraison[nom] = ("coins", int(nom.split(" ", 1)[0]))
    elif nom in deblocage:
        livraison[nom] = ("attack_piece", deblocage[nom])
    elif nom in par_nom.get("consommable", {}):
        livraison[nom] = ("consumable", par_nom["consommable"][nom])
    elif nom in par_nom.get("equipement", {}):
        livraison[nom] = ("gear", par_nom["equipement"][nom])
    else:
        raise SystemExit(
            f"item {nom!r} d'aucune famille connue : le pool a change sans "
            f"que la table de livraison suive"
        )

# --- capacites, les seuls items de progression ------------------------
#
# Une capacite est un bit du champ 2xxx. Deux mesures la rendent
# utilisable comme `item` :
#
#   5 aout 2026  lever le bit donne la capacite, sans sa cinematique
#   7 aout 2026  l'abaisser la retire proprement, le marteau disparait
#                de la commande de combat puis revient
#
# La seconde est celle qui compte. Sans patch de ROM, le jeu octroie la
# capacite au moment prevu de toute facon ; c'est le client qui doit
# abaisser ce que le serveur n'a pas encore envoye. Une capacite qui ne
# se retire pas ne peut pas etre un item.
#
# LA LISTE EST VOLONTAIREMENT COURTE. Neuf capacites de deplacement et de
# combat, celles qui ouvrent des passages. Sont ecartees, et pourquoi :
#
#   0x2000 MINI_MARIO      etat, pas deblocage : le joueur prend et quitte
#                          la forme a volonte, temoignage du 7 aout 2026
#   0x2004 FIRE_BREATH     sens inverse, et sa salle d'octroi est ambigue,
#                          8 salles la posent et 9 la retirent
#   0x200B 0x200C 0x200D   menus, pas passages
#   0x2026 a 0x202C        ameliorations de boutique
#   0x2010 a 0x2022        attaques, deja livrees par leurs pieces
CAPACITES = {
    "Hammer": 0x2001,
    "Spin Jump": 0x2002,
    "Drill Bros": 0x2003,
    "Sliding Haymaker": 0x2005,
    "Body Slam": 0x2006,
    "Spike Ball": 0x2007,
    "Vacuum Block": 0x200E,
    "Blue Shell Blocks": 0x2025,
    "Air Vents": 0x202D,
}

FEVENT = RACINE / "data" / "capacites_fevent.csv"
ORDRE = RACINE / "data" / "ordre_zones.csv"

zone_octroi = {}
with open(FEVENT, encoding="utf-8") as f:
    for r in csv.DictReader(f):
        zone_octroi[int(r["variable"], 16)] = r["zones_octroi"]

ordre_zones = []
with open(ORDRE, encoding="utf-8") as f:
    for r in csv.DictReader(f):
        ordre_zones.append((int(r["rang"]), r["zone"], r["confiance"]))
ordre_zones.sort()

zones_ordonnees = [z for _, z, _ in ordre_zones]
manquantes = [z for z in vues_zones_tresors if z not in zones_ordonnees]
if manquantes:
    raise SystemExit(
        f"zones sans rang dans data/ordre_zones.csv : {manquantes}. "
        f"Une region sans rang n'a pas de place dans la chaine."
    )

capacites = []
for nom, variable in sorted(CAPACITES.items(), key=lambda kv: kv[1]):
    zones = zone_octroi.get(variable, "")
    # Une capacite posee dans plusieurs zones n'a pas de rang unique. On
    # retient LA PLUS PRECOCE, et le sens de l'erreur est ce qui decide.
    #
    # La regle d'acces dit : une zone de rang r exige les capacites de
    # rang < r. Ce qui est demontre par le jeu d'origine, c'est qu'on
    # traverse les zones jusqu'a Z SANS la capacite octroyee en Z ; au
    # dela, on ne sait pas, donc on exige, par prudence.
    #
    # Situer l'octroi trop tot ajoute des exigences : le placement est
    # plus contraint, le joueur ne l'est jamais. Le situer trop tard en
    # retire, et la un item necessaire peut atterrir derriere le mur
    # qu'il ouvre. Une seule des deux erreurs bloque une partie.
    candidates = [z.strip() for z in zones.split("|") if z.strip() in zones_ordonnees]
    if not candidates:
        raise SystemExit(
            f"capacite {nom!r} : aucune de ses zones d'octroi {zones!r} "
            f"n'a de rang. Completer data/ordre_zones.csv."
        )
    zone = min(candidates, key=zones_ordonnees.index)
    capacites.append((nom, variable, zone))

for nom, variable, _ in capacites:
    livraison[nom] = ("capability", variable)

couverture = Counter(cat for cat, _ in livraison.values())

lignes_py = [
    '"""Donnees du monde, GENEREES. Ne pas editer a la main.',
    "",
    "Regenerer avec tools/build_apworld_data.py, qui lit",
    "data/locations_bis.csv et data/pieces_attaque.csv, eux-memes",
    "regeneres depuis la ROM.",
    '"""',
    "",
    f"BASE_ID = {BASE_ID:#x}",
    f"RESERVE_HORS_TABLE = {RESERVE_HORS_TABLE}",
    "",
    "# (identifiant TreasureInfo, nom de location, item d'origine, zone)",
    "TREASURES = [",
]
for ident, nom, item, zone in tresors:
    lignes_py.append(f"    ({ident}, {nom!r}, {item!r}, {zone!r}),")
lignes_py.append("]")
lignes_py.append("")
lignes_py.append("# (rang de bit dans Exxx, nom de location, item d'origine, zone)")
lignes_py.append("# Une piece d'attaque ; le rang tient lieu d'identifiant.")
lignes_py.append("ATTACK_PIECES = [")
for rang, nom, item, zone in pieces:
    lignes_py.append(f"    ({rang}, {nom!r}, {item!r}, {zone!r}),")
lignes_py.append("]")
lignes_py.append("")
lignes_py.append("# toutes les locations, tresors puis pieces d'attaque")
lignes_py.append("LOCATIONS = TREASURES + ATTACK_PIECES")
lignes_py.append("")
lignes_py.append("# zones portant au moins un tresor, dans l'ordre d'apparition")
lignes_py.append("ZONES = [")
for zone in vues_zones_tresors:
    lignes_py.append(f"    {zone!r},")
lignes_py.append("]")
lignes_py.append("")
lignes_py.append("# les regions dans l'ordre du parcours, avec la confiance")
lignes_py.append("# qu'on a dans ce rang. Source : data/ordre_zones.csv")
lignes_py.append("ZONE_ORDER = [")
for rang, zone, confiance in ordre_zones:
    lignes_py.append(f"    ({rang}, {zone!r}, {confiance!r}),")
lignes_py.append("]")
lignes_py.append("")
lignes_py.append("# (nom d'item, variable 2xxx, zone ou le jeu l'octroie)")
lignes_py.append("# Les seuls items de progression du monde.")
lignes_py.append("CAPABILITIES = [")
for nom, variable, zone in capacites:
    lignes_py.append(f"    ({nom!r}, {variable:#06x}, {zone!r}),")
lignes_py.append("]")
lignes_py.append("")
lignes_py.append("# nom d'item -> nombre d'exemplaires dans le jeu d'origine")
lignes_py.append("VANILLA_ITEMS = {")
for nom, n in sorted(items.items()):
    lignes_py.append(f"    {nom!r}: {n},")
lignes_py.append("}")
lignes_py.append("")
lignes_py.append("# nom d'item -> (categorie de livraison, valeur)")
lignes_py.append("#   'coins'        montant a ajouter au u32 a 02056400   Verifie")
lignes_py.append("#   'consumable'   index du compteur, 02056406 + index   Verifie")
lignes_py.append("#   'gear'         compteur a 02056427 + id - 1          Verifie")
lignes_py.append("#   'attack_piece' bit du champ 2xxx a 02056038          Verifie")
lignes_py.append("ITEM_DELIVERY = {")
for nom in sorted(livraison):
    cat, val = livraison[nom]
    lignes_py.append(f"    {nom!r}: ({cat!r}, {val}),")
lignes_py.append("}")
lignes_py.append("")

SORTIE.parent.mkdir(exist_ok=True)
SORTIE.write_text("\n".join(lignes_py), encoding="utf-8")

par_attaque = Counter(p[2] for p in pieces)

print(f"ecrit : {SORTIE.relative_to(RACINE)}")
print(f"  {len(tresors)} tresors, identifiants {tresors[0][0]} a {maxi}")
print(f"  {len(pieces)} pieces d'attaque, rangs {pieces[0][0]} a {pieces[-1][0]}")
for nom, n in sorted(par_attaque.items()):
    print(f"      {nom:<24} {n:>2}")
print(f"  {len(tresors) + len(pieces)} locations au total")
print(f"  {len(items)} items distincts, {sum(items.values())} exemplaires")
print(f"  plage de location : {BASE_ID:#x} a {BASE_ID + pieces[-1][0]:#x}")
print(f"  reserve hors-table : {BASE_ID + RESERVE_HORS_TABLE:#x} et au-dela")
print()
print("  livraison, par categorie :")
etabli = {"coins", "consumable", "gear", "attack_piece"}
exemplaires_ok = 0
for cat, n_noms in sorted(couverture.items()):
    n_ex = sum(items[nom] for nom, (c, _) in livraison.items() if c == cat)
    statut = "verifie" if cat in etabli else "NON ETABLI"
    if cat in etabli:
        exemplaires_ok += n_ex
    print(f"    {cat:<14} {n_noms:>3} noms, {n_ex:>4} exemplaires   {statut}")
print(f"    livrables aujourd'hui : {exemplaires_ok} sur {sum(items.values())}")
