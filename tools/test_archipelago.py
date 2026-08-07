"""Lance la suite generale d'Archipelago sur notre monde installe.

POURQUOI CE TROISIEME TEST. `test_generation.py` verifie qu'une seed
sort, `test_client.py` verifie la conversion bit vers location et les
ecritures de livraison. Ni l'un ni l'autre ne verifie ce qu'Archipelago
attend d'un monde : identifiants uniques, noms valides, toutes les
locations accessibles, remplissage possible, options bien formees.

`contributing.md` en fait une exigence : ne pas introduire d'echec de
test. Ces tests tournent sur **tous** les mondes installes, donc un echec
peut venir d'ailleurs que de nous ; le script le dit plutot que de
laisser croire le contraire.

Le monde doit avoir ete installe dans vendor/Archipelago/worlds par
tools/seed_de_test.py ou tools/test_generation.py, sinon il n'est pas
teste du tout et la suite passe pour de mauvaises raisons.

Usage :
    venv\\Scripts\\python.exe tools\\test_archipelago.py
"""
import shutil
import subprocess
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
MONDE = RACINE / "mlbis"
AP = RACINE / "vendor" / "Archipelago"
PYTHON_AP = AP / "venv" / "Scripts" / "python.exe"

MODULES = [
    "test.general.test_reachability",
    "test.general.test_items",
    "test.general.test_locations",
    "test.general.test_ids",
    "test.general.test_names",
    "test.general.test_fill",
    "test.general.test_options",
    "test.general.test_implemented",
    "test.general.test_world_manifest",
    "test.general.test_packages",
    "test.general.test_state",
]

if not PYTHON_AP.exists():
    raise SystemExit(f"venv d'Archipelago introuvable : {PYTHON_AP}")

# Reinstaller avant de tester : tester la copie de la veille pendant
# qu'on modifie la source est le genre de faux positif qui coute cher.
cible = AP / "worlds" / MONDE.name
if cible.exists():
    shutil.rmtree(cible)
shutil.copytree(MONDE, cible, ignore=shutil.ignore_patterns("__pycache__"))
print(f"monde installe : {cible.relative_to(RACINE)}")

res = subprocess.run(
    [str(PYTHON_AP), "-m", "unittest", *MODULES],
    cwd=str(AP), capture_output=True, text=True,
)
sortie = res.stdout + res.stderr
lignes = [l for l in sortie.splitlines()
          if l.startswith(("Ran ", "OK", "FAILED", "ERROR:", "FAIL:"))]
print("\n".join(lignes) or sortie[-2000:])

if res.returncode != 0:
    print("\nEchec. Le detail complet :")
    print(sortie[-4000:])
    sys.exit(1)
print("\nOK. Le monde passe la suite generale d'Archipelago.")
