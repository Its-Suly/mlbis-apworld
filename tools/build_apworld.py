"""Empaquette le monde en `.apworld` et verifie qu'il se suffit a lui-meme.

L'empaquetage passe par le composant officiel du launcher,
`Launcher.py "Build APWorlds" -- "<jeu>"`, et non par un zip fait main :
c'est lui qui ajoute `version` et `compatible_version` au manifeste,
`docs/apworld specification.md:41-46`. Les ecrire nous-memes serait
exactement le piege liste dans empaquetage-apworld.md.

Les quatre autres pieges de ce fichier sont verifies ici plutot que
supposes : nom entierement en minuscules, un seul dossier racine portant
le nom du zip, pas de `__pycache__` embarque, et surtout le controle qui
compte, **generer une seed avec la source retiree**. Un `.apworld` qui
marche uniquement parce que le dossier source traine a cote n'est pas
empaquete, il est deguise.

Usage :
    venv\\Scripts\\python.exe tools\\build_apworld.py
"""
import json
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
MONDE = RACINE / "mlbis"
AP = RACINE / "vendor" / "Archipelago"
PYTHON_AP = AP / "venv" / "Scripts" / "python.exe"
JEU = "Mario & Luigi Bowser's Inside Story"
DIST = RACINE / "dist"

if not PYTHON_AP.exists():
    raise SystemExit(f"venv d'Archipelago introuvable : {PYTHON_AP}")

source = AP / "worlds" / MONDE.name
paquet = AP / "custom_worlds" / f"{MONDE.name}.apworld"
construit = AP / "build" / "apworlds" / f"{MONDE.name}.apworld"

# 1. installer la source, puis construire
if source.exists():
    shutil.rmtree(source)
shutil.copytree(MONDE, source, ignore=shutil.ignore_patterns("__pycache__"))
if paquet.exists():
    paquet.unlink()

res = subprocess.run(
    [str(PYTHON_AP), "Launcher.py", "Build APWorlds", "--", JEU],
    cwd=str(AP), capture_output=True, text=True,
)
if not construit.exists():
    print(res.stdout + res.stderr)
    raise SystemExit("le composant Build APWorlds n'a rien produit")

# 2. controler la forme du paquet
echecs = []
if construit.name != construit.name.lower():
    echecs.append(f"nom non minuscule : {construit.name}")
with zipfile.ZipFile(construit) as z:
    noms = z.namelist()
    racines = {n.split("/")[0] for n in noms}
    if racines != {MONDE.name}:
        echecs.append(f"racines du zip {racines}, attendu {{{MONDE.name!r}}}")
    if any("__pycache__" in n for n in noms):
        echecs.append("__pycache__ embarque")
    manifeste = json.loads(z.read(f"{MONDE.name}/archipelago.json"))
    for champ in ("game", "version", "compatible_version"):
        if champ not in manifeste:
            echecs.append(f"manifeste sans {champ}")
    if manifeste.get("game") != JEU:
        echecs.append(f"manifeste : jeu {manifeste.get('game')!r}")
    docs = [n for n in noms if "/docs/" in n]
    if len(docs) < 2:
        echecs.append(f"docs manquantes dans le paquet : {docs}")

print(f"paquet : {construit.name}, {len(noms)} entrees, "
      f"world_version {manifeste.get('world_version')}")

# 3. le seul controle qui prouve quelque chose : generer sans la source
paquet.parent.mkdir(exist_ok=True)
shutil.copy(construit, paquet)
shutil.rmtree(source)
joueurs = RACINE / "seeds" / "players"
sortie = AP / "build" / "essai_apworld"
if sortie.exists():
    shutil.rmtree(sortie)
sortie.mkdir(parents=True)
essai = subprocess.run(
    [str(PYTHON_AP), "Generate.py", "--player_files_path", str(joueurs),
     "--outputpath", str(sortie), "--seed", "1"],
    cwd=str(AP), capture_output=True, text=True,
)
lignes = [l for l in (essai.stdout + essai.stderr).splitlines() if JEU in l]
if essai.returncode != 0 or not lignes:
    echecs.append("generation impossible avec le seul .apworld")
    print((essai.stdout + essai.stderr)[-1500:])
else:
    print("sans la source :", lignes[0].strip())

# 4. remettre l'environnement comme on l'a trouve, et livrer
paquet.unlink()
shutil.copytree(MONDE, source, ignore=shutil.ignore_patterns("__pycache__"))
DIST.mkdir(exist_ok=True)
shutil.copy(construit, DIST / construit.name)
print(f"livre : dist/{construit.name}")

if echecs:
    print("\nECHECS :")
    for e in echecs:
        print(f"  {e}")
    sys.exit(1)
print("\nOK. Le paquet se suffit a lui-meme.")
