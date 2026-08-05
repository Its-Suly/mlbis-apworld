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
from data import ATTACK_PIECES, BASE_ID, LOCATIONS, TREASURES  # noqa: E402

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

print()
if echecs:
    print(f"{echecs} echec(s)")
    sys.exit(1)
print("OK.")
