"""Installe le monde dans Archipelago et genere une seed de controle.

C'est le seul test qui vaut pour le squelette : soit Archipelago charge
le monde et sort une seed, soit non.

Le monde vit dans mlbis/ a la racine du projet. Archipelago, lui, ne sait
charger que ce qui est dans son propre dossier worlds/, donc ce script
recopie mlbis/ dans vendor/Archipelago/worlds/ avant de generer. La copie
est ecrasee a chaque passage ; vendor/ est exclu du depot.

Usage :
    venv\\Scripts\\python.exe tools\\test_generation.py

Sortie attendue, en fin de course :
    Mario & Luigi Bowser's Inside Story  : ... | Items: 95 | Locations: 725
    seed generee : AP_....zip
"""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
MONDE = RACINE / "mlbis"
AP = RACINE / "vendor" / "Archipelago"
PYTHON_AP = AP / "venv" / "Scripts" / "python.exe"
JEU = "Mario & Luigi Bowser's Inside Story"

for chemin, quoi in ((MONDE, "le monde"), (AP, "Archipelago"), (PYTHON_AP, "le venv d'Archipelago")):
    if not chemin.exists():
        raise SystemExit(f"introuvable : {quoi} a {chemin}")

cible = AP / "worlds" / MONDE.name
if cible.exists():
    shutil.rmtree(cible)
shutil.copytree(MONDE, cible, ignore=shutil.ignore_patterns("__pycache__"))
print(f"monde installe : {cible.relative_to(RACINE)}")

with tempfile.TemporaryDirectory() as tmp:
    tmp = Path(tmp)
    joueurs = tmp / "players"
    sortie = tmp / "out"
    joueurs.mkdir()
    sortie.mkdir()
    (joueurs / "test.yaml").write_text(
        f"name: TestBIS\ndescription: squelette BIS\ngame: {JEU}\n{JEU}: {{}}\n",
        encoding="utf-8",
    )

    res = subprocess.run(
        [str(PYTHON_AP), "Generate.py",
         "--player_files_path", str(joueurs),
         "--outputpath", str(sortie),
         "--seed", "1", "--spoiler", "3"],
        cwd=str(AP), capture_output=True, text=True,
    )

    sortie_texte = res.stdout + res.stderr
    ligne_monde = [l for l in sortie_texte.splitlines() if JEU in l and "Locations:" in l]
    seeds = list(sortie.glob("*.zip"))

    if ligne_monde:
        print(ligne_monde[0].strip())
    else:
        print("ATTENTION : Archipelago n'a pas liste le monde.")

    if res.returncode != 0 or not seeds:
        print(f"\nECHEC, code {res.returncode}")
        print("\n".join(sortie_texte.splitlines()[-25:]))
        sys.exit(1)

    print(f"seed generee : {seeds[0].name}")
    print("\nOK. Le monde se charge et genere.")
