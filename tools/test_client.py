"""Verifie la conversion bit -> location du client, sur de vrais dumps.

Le client lui-meme demande BizHawk et un serveur Archipelago. Sa partie
decisive, elle, est une fonction pure : le champ de bits en entree, les
identifiants de location en sortie. Elle se controle sur les dumps deja
pris, sans rien lancer.

Les attendus viennent des mesures consignees dans formats-bis.md :
  run06  aucun tresor
  run08  546 seul, premiere piece du bloc multi-coups
  run12  544, 545, 546, 547, les quatre blocs de la salle 258
  run13  identique a run12, apres sauvegarde

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
from data import BASE_ID, TREASURES  # noqa: E402

LOCATION_TO_BIT = {nom: ident for ident, nom, _, _ in TREASURES}
location_name_to_id = {nom: BASE_ID + ident for ident, nom, _, _ in TREASURES}

ATTENDUS = {
    "run06": set(),
    "run08": {546},
    "run12": {544, 545, 546, 547},
    "run13": {544, 545, 546, 547},
}

echecs = 0
for run, identifiants in sorted(ATTENDUS.items()):
    chemin = RACINE / "dumps" / f"{run}_Main_RAM.bin"
    if not chemin.exists():
        print(f"{run} : dump absent, ignore ({chemin.name})")
        continue

    champ = chemin.read_bytes()[CHAMP_TRESORS:CHAMP_TRESORS + CHAMP_TAILLE]
    obtenu = locations_du_champ(champ, BASE_ID)
    attendu = {BASE_ID + i for i in identifiants}

    if obtenu == attendu:
        print(f"{run} : OK, {len(obtenu)} location(s)")
    else:
        echecs += 1
        print(f"{run} : ECHEC")
        print(f"   attendu {sorted(hex(x) for x in attendu)}")
        print(f"   obtenu  {sorted(hex(x) for x in obtenu)}")

# Controle de coherence : toute location produite doit exister dans le
# monde, et son identifiant doit valoir BASE_ID + son rang de bit.
ids_connus = set(location_name_to_id.values())
for nom, bit in LOCATION_TO_BIT.items():
    if location_name_to_id[nom] != BASE_ID + bit:
        print(f"ECHEC : {nom} a l'id {location_name_to_id[nom]:#x}, "
              f"attendu {BASE_ID + bit:#x}")
        echecs += 1
        break
else:
    print(f"correspondance id = BASE_ID + rang de bit : OK sur "
          f"{len(LOCATION_TO_BIT)} locations")

champ_run13 = (RACINE / "dumps" / "run13_Main_RAM.bin")
if champ_run13.exists():
    obtenu = locations_du_champ(
        champ_run13.read_bytes()[CHAMP_TRESORS:CHAMP_TRESORS + CHAMP_TAILLE], BASE_ID
    )
    inconnues = obtenu - ids_connus
    if inconnues:
        print(f"ECHEC : {len(inconnues)} location(s) hors du monde : "
              f"{sorted(hex(x) for x in inconnues)}")
        echecs += 1
    else:
        print("toutes les locations produites existent dans le monde : OK")

print()
if echecs:
    print(f"{echecs} echec(s)")
    sys.exit(1)
print("OK.")
