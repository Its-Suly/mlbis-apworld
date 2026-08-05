"""Genere une seed jouable dans seeds/ et affiche comment la lancer.

test_generation.py verifie qu'une seed sort, puis jette tout : il valide
l'empaquetage, pas le jeu. Ce script-ci garde la seed, parce que la
prochaine etape est de jouer la chaine complete, serveur compris.

La seed contient un seul joueur. En solo, chaque item que le joueur
trouve lui revient, ce qui suffit a valider la livraison : le client doit
detecter le check, le serveur renvoyer l'item, et le jeu l'afficher.

Usage :
    venv\\Scripts\\python.exe tools\\seed_de_test.py
"""
import shutil
import subprocess
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
MONDE = RACINE / "mlbis"
AP = RACINE / "vendor" / "Archipelago"
PYTHON_AP = AP / "venv" / "Scripts" / "python.exe"
SEEDS = RACINE / "seeds"
JEU = "Mario & Luigi Bowser's Inside Story"
JOUEUR = "TestBIS"

for chemin, quoi in ((MONDE, "le monde"), (AP, "Archipelago"),
                     (PYTHON_AP, "le venv d'Archipelago")):
    if not chemin.exists():
        raise SystemExit(f"introuvable : {quoi} a {chemin}")

cible = AP / "worlds" / MONDE.name
if cible.exists():
    shutil.rmtree(cible)
shutil.copytree(MONDE, cible, ignore=shutil.ignore_patterns("__pycache__"))
print(f"monde installe : {cible.relative_to(RACINE)}")

SEEDS.mkdir(exist_ok=True)
joueurs = SEEDS / "players"
joueurs.mkdir(exist_ok=True)
(joueurs / "test.yaml").write_text(
    f"name: {JOUEUR}\ndescription: seed de test BIS\ngame: {JEU}\n{JEU}: {{}}\n",
    encoding="utf-8",
)

res = subprocess.run(
    [str(PYTHON_AP), "Generate.py",
     "--player_files_path", str(joueurs),
     "--outputpath", str(SEEDS),
     "--seed", "1", "--spoiler", "3"],
    cwd=str(AP), capture_output=True, text=True,
)

sortie = res.stdout + res.stderr
ligne = [l for l in sortie.splitlines() if JEU in l and "Locations:" in l]
if ligne:
    print(ligne[0].strip())

zips = sorted(SEEDS.glob("*.zip"), key=lambda p: p.stat().st_mtime)
if res.returncode != 0 or not zips:
    print(f"\nECHEC, code {res.returncode}")
    print("\n".join(sortie.splitlines()[-25:]))
    sys.exit(1)

seed = zips[-1]
print(f"seed : {seed.relative_to(RACINE)}")

print(f"""
Trois choses a lancer, dans cet ordre.

1. Le serveur, dans un terminal a part :

   {PYTHON_AP} MultiServer.py "{seed}"

   Depuis {AP}. Il ecoute sur 38281 et affiche le mot de passe s'il y en
   a un. Le laisser tourner.

2. BizHawk avec la ROM chargee, puis Tools > Lua Console, Ctrl+O sur :

   {AP / "data" / "lua" / "connector_bizhawk_generic.lua"}

3. Le client Archipelago, dans un troisieme terminal :

   {PYTHON_AP} BizHawkClient.py

   Se connecter a localhost:38281, nom de slot : {JOUEUR}

Ce qui doit se passer, et ce qu'il faut regarder :

  - le client dit « Connected » et annonce le jeu
  - ramasser un bloc en jeu : le serveur affiche le check
  - en solo l'item revient au joueur, donc le compteur ou le menu du jeu
    doit bouger dans la seconde
  - les pieces d'or sont le controle le plus lisible : le compteur est a
    l'ecran en permanence
""")
