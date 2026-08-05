"""Verifie la conversion bit -> location du client, sur de vrais dumps.

Le client lui-meme demande BizHawk et un serveur Archipelago. Sa partie
decisive, elle, est une fonction pure : le champ de bits en entree, les
identifiants de location en sortie. Elle se controle sur les dumps deja
pris, sans rien lancer.

Depuis le 5 aout 2026 le client lit les 0x200 octets du tableau Exxx et
non plus 95. Il voit donc les drapeaux d'histoire et d'ennemis, qui ne
sont pas des locations. Le test verifie les deux familles separement et
compte ce qui est ecarte, plutot que d'exiger une egalite sur tout le
tableau, qui ne serait pas tenable.

Les attendus viennent des mesures consignees dans formats-bis.md :
  run06  aucun tresor
  run08  546 seul, premiere piece du bloc multi-coups
  run12  544, 545, 546, 547, les quatre blocs de la salle 258
  run13  identique a run12, apres sauvegarde
  run46  neuf pieces du Green Shell, 0xE700 a 0xE708
  run51  les dix, apres deblocage, combat et porte ouverte

Usage :
    venv\\Scripts\\python.exe tools\\test_client.py
"""
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
# On charge bitfield et data comme modules autonomes, sans passer par le
# package : mlbis/__init__.py importe Archipelago, qui n'est pas dans ce
# venv. C'est justement pour ca que bitfield.py ne depend de rien.
sys.path.insert(0, str(RACINE / "mlbis"))

from bitfield import CHAMP_TAILLE, CHAMP_TRESORS, locations_du_champ  # noqa: E402
from data import (  # noqa: E402
    ATTACK_PIECES, BASE_ID, ITEM_DELIVERY, LOCATIONS, TREASURES, VANILLA_ITEMS,
)
from delivery import (  # noqa: E402
    BASE_CONSOMMABLES, CATEGORIES_ETABLIES, COMPTEUR_PIECES, ecriture_de_flag,
    couverture, livraison_de, livraison_de_lot, seuils_de_lot,
)

LOCATION_TO_BIT = {nom: rang for rang, nom, _, _ in LOCATIONS}
location_name_to_id = {nom: BASE_ID + rang for rang, nom, _, _ in LOCATIONS}

IDS_TRESORS = {BASE_ID + rang for rang, _, _, _ in TREASURES}
IDS_PIECES = {BASE_ID + rang for rang, _, _, _ in ATTACK_PIECES}
IDS_CONNUS = IDS_TRESORS | IDS_PIECES

# run -> (rangs de tresor attendus, rangs de piece attendus)
# None signifie « pas de mesure pour cette famille dans ce dump ».
ATTENDUS = {
    "run06": (set(), None),
    "run08": ({546}, None),
    "run12": ({544, 545, 546, 547}, None),
    "run13": ({544, 545, 546, 547}, None),
    "run46": (None, set(range(1792, 1801))),
    "run51": (None, set(range(1792, 1802))),
}

echecs = 0
for run, (tresors_attendus, pieces_attendues) in sorted(ATTENDUS.items()):
    chemin = RACINE / "dumps" / f"{run}_Main_RAM.bin"
    if not chemin.exists():
        print(f"{run} : dump absent, ignore ({chemin.name})")
        continue

    champ = chemin.read_bytes()[CHAMP_TRESORS:CHAMP_TRESORS + CHAMP_TAILLE]
    tout = locations_du_champ(champ, BASE_ID)
    hors_monde = len(tout - IDS_CONNUS)

    for libelle, attendus, univers in (
        ("tresor", tresors_attendus, IDS_TRESORS),
        ("piece", pieces_attendues, IDS_PIECES),
    ):
        if attendus is None:
            continue
        obtenu = tout & univers
        attendu = {BASE_ID + r for r in attendus}
        if obtenu == attendu:
            print(f"{run} : OK, {len(obtenu)} {libelle}(s), "
                  f"{hors_monde} bit(s) hors du monde ecarte(s)")
        else:
            echecs += 1
            print(f"{run} : ECHEC sur les {libelle}s")
            print(f"   manquants {sorted(hex(x) for x in attendu - obtenu)}")
            print(f"   en trop   {sorted(hex(x) for x in obtenu - attendu)}")

# Controle de coherence : l'identifiant d'une location vaut BASE_ID plus
# le rang de son bit, dans les deux familles.
for nom, bit in LOCATION_TO_BIT.items():
    if location_name_to_id[nom] != BASE_ID + bit:
        print(f"ECHEC : {nom} a l'id {location_name_to_id[nom]:#x}, "
              f"attendu {BASE_ID + bit:#x}")
        echecs += 1
        break
else:
    print(f"correspondance id = BASE_ID + rang de bit : OK sur "
          f"{len(LOCATION_TO_BIT)} locations")

# Les deux familles ne doivent jamais se recouvrir.
if IDS_TRESORS & IDS_PIECES:
    print(f"ECHEC : {len(IDS_TRESORS & IDS_PIECES)} identifiant(s) partage(s) "
          f"entre tresors et pieces d'attaque")
    echecs += 1
else:
    print(f"tresors et pieces d'attaque disjoints : OK, "
          f"{len(IDS_TRESORS)} + {len(IDS_PIECES)} = {len(IDS_CONNUS)}")

# La fenetre de lecture doit couvrir la derniere location du monde.
rang_max = max(LOCATION_TO_BIT.values())
if rang_max // 8 >= CHAMP_TAILLE:
    print(f"ECHEC : rang max {rang_max} a l'octet {rang_max // 8}, "
          f"hors de la fenetre de {CHAMP_TAILLE} octets")
    echecs += 1
else:
    print(f"fenetre de lecture : OK, rang max {rang_max} a l'octet "
          f"{rang_max // 8}, fenetre de {CHAMP_TAILLE} octets")

# --- livraison des items ----------------------------------------------
#
# Chaque item du pool doit avoir une categorie, et chaque categorie
# etablie doit produire une adresse dans le bloc d'inventaire.

sans_categorie = [nom for nom in VANILLA_ITEMS if nom not in ITEM_DELIVERY]
if sans_categorie:
    print(f"ECHEC : {len(sans_categorie)} item(s) sans categorie de "
          f"livraison : {sans_categorie[:5]}")
    echecs += 1
else:
    print(f"categorie de livraison : OK sur {len(VANILLA_ITEMS)} items")

adresses = {}
mauvaises = []
for nom, (categorie, _) in sorted(ITEM_DELIVERY.items()):
    ecriture = livraison_de(nom, ITEM_DELIVERY)
    if categorie == "attack_piece":
        # Une piece ne se livre pas seule : c'est le lot complet qui leve
        # le drapeau de l'attaque, via livraison_de_lot.
        if ecriture is not None:
            mauvaises.append(f"{nom} : une piece seule ne doit rien ecrire")
        lot = livraison_de_lot(nom, ITEM_DELIVERY)
        if len(lot) != 2 or any(e.operation != "bit" for e in lot):
            mauvaises.append(f"{nom} : lot mal forme, {lot}")
        continue
    if categorie in CATEGORIES_ETABLIES:
        if ecriture is None:
            mauvaises.append(f"{nom} : categorie etablie mais aucune ecriture")
            continue
        if categorie == "consumable":
            attendu = BASE_CONSOMMABLES + ITEM_DELIVERY[nom][1]
            if ecriture.adresse != attendu:
                mauvaises.append(f"{nom} : adresse {ecriture.adresse:#x}")
            # Deux consommables ne peuvent pas partager un compteur.
            if ecriture.adresse in adresses:
                mauvaises.append(
                    f"{nom} partage {ecriture.adresse:#x} avec {adresses[ecriture.adresse]}"
                )
            adresses[ecriture.adresse] = nom
        elif categorie == "coins" and ecriture.adresse != COMPTEUR_PIECES:
            mauvaises.append(f"{nom} : adresse {ecriture.adresse:#x}")
    elif ecriture is not None:
        mauvaises.append(f"{nom} : categorie non etablie mais une ecriture produite")

if mauvaises:
    print(f"ECHEC sur la livraison : {mauvaises[:5]}")
    echecs += 1
else:
    detail = ", ".join(
        f"{cat} {n}{'' if cat in CATEGORIES_ETABLIES else ' (non etabli)'}"
        for cat, n in sorted(couverture(ITEM_DELIVERY).items())
    )
    print(f"ecritures de livraison : OK, {detail}")

# L'equipement doit retomber sur l'ecriture mesuree en jeu le 5 aout
# 2026 : 1 ecrit au compteur 0x05642B fait apparaitre Heart Wear.
heart = livraison_de("Heart Wear", ITEM_DELIVERY)
if heart is None or heart.adresse != 0x05642B:
    print(f"ECHEC : Heart Wear calcule {heart}, mesure 0x5642b")
    echecs += 1
else:
    print("equipement : OK, Heart Wear retombe sur l'ecriture mesuree")

# Le drapeau de Fire Flower doit retomber sur l'ecriture mesuree en jeu
# le 5 aout 2026 : adresse 0x05603B, octet 00 -> 02.
flag = ecriture_de_flag(0x2019, "Fire Flower")
if (flag.adresse, flag.valeur(0x00)) != (0x05603B, 0x02):
    print(f"ECHEC : Fire Flower calcule {flag.adresse:#x} valeur "
          f"{flag.valeur(0):#04x}, mesure 0x5603b et 0x02")
    echecs += 1
elif flag.valeur(0x02) != 0x02:
    print("ECHEC : lever un bit deja leve doit etre sans effet")
    echecs += 1
else:
    seuils = seuils_de_lot(ITEM_DELIVERY, VANILLA_ITEMS)
    detail = ", ".join(f"{n.removesuffix(' Piece')} {s}"
                       for n, s in sorted(seuils.items()) if s != 10)
    print(f"drapeaux 2xxx : OK, Fire Flower retombe sur l'ecriture mesuree ; "
          f"seuils hors 10 : {detail or 'aucun'}")

# Le plafond doit ecreter au lieu de deborder.
nut = livraison_de("Nut", ITEM_DELIVERY)
if nut is None or nut.valeur(0) != 1 or nut.valeur(99) != 99:
    print(f"ECHEC : plafond du consommable, {nut}")
    echecs += 1
else:
    exemplaires_ok = sum(
        n for nom, n in VANILLA_ITEMS.items()
        if ITEM_DELIVERY[nom][0] in CATEGORIES_ETABLIES
    )
    print(f"plafonds : OK, {exemplaires_ok} exemplaires sur "
          f"{sum(VANILLA_ITEMS.values())} livrables aujourd'hui")

print()
if echecs:
    print(f"{echecs} echec(s)")
    sys.exit(1)
print("OK.")
