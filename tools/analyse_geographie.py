"""Les identifiants de tresor suivent-ils la geographie du jeu ?

Question pratique : si des identifiants proches designent des tresors
proches en jeu, alors un test en jeu peut couvrir plusieurs identifiants
consecutifs sans traverser la carte, et une plage d'identifiants se lit
comme une zone. Sinon, chaque test doit etre choisi tresor par tresor.

Mesure trois choses, sans toucher a la ROM :

1. pour chaque plage de 64 identifiants, les salles concernees
2. si les identifiants d'une meme salle sont contigus
3. si l'ordre des identifiants suit l'ordre des salles

Rappel de lecture : la salle est reconstruite par le bit
`is_last_entry_in_room`, donc son numero suit l'ordre du fichier. Une
correlation entre identifiant et salle signifie donc que l'identifiant
suit l'ordre du fichier, qui lui-meme groupe les tresors par salle.

Usage :
    venv\\Scripts\\python.exe tools\\analyse_geographie.py
"""
import csv
from collections import defaultdict
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
CSV_LOCATIONS = RACINE / "data" / "locations_bis.csv"
PAS = 64

if not CSV_LOCATIONS.exists():
    raise SystemExit(f"introuvable : {CSV_LOCATIONS}. "
                     f"Regenerer avec tools/build_location_table.py.")

lignes = []
with open(CSV_LOCATIONS, encoding="utf-8") as f:
    for r in csv.DictReader(f):
        if r["exploitable"] == "1":
            lignes.append((int(r["identifiant"]), int(r["salle"])))

par_identifiant = sorted(lignes)
salles_par_id = dict(par_identifiant)
ids_par_salle = defaultdict(list)
for ident, salle in par_identifiant:
    ids_par_salle[salle].append(ident)

print(f"{len(lignes)} tresors exploitables, "
      f"{len(ids_par_salle)} salles, identifiants de "
      f"{par_identifiant[0][0]} a {par_identifiant[-1][0]}")
print()

print("=" * 72)
print("1. Salles concernees par plage de 64 identifiants")
print("=" * 72)
print()
for debut in range(0, 768, PAS):
    plage = [s for i, s in par_identifiant if debut <= i < debut + PAS]
    if not plage:
        print(f"  {debut:3d}-{debut + PAS - 1:3d}  aucun identifiant")
        continue
    distinctes = sorted(set(plage))
    apercu = ", ".join(str(s) for s in distinctes[:12])
    if len(distinctes) > 12:
        apercu += f", ... ({len(distinctes)} salles)"
    print(f"  {debut:3d}-{debut + PAS - 1:3d}  {len(plage):3d} tresors, "
          f"salles {min(distinctes)} a {max(distinctes)}")
    print(f"            {apercu}")
print()

print("=" * 72)
print("2. Les identifiants d'une meme salle sont-ils contigus ?")
print("=" * 72)
print()
contigues = [s for s, ids in ids_par_salle.items()
             if ids == list(range(min(ids), min(ids) + len(ids)))]
eclatees = {s: ids for s, ids in ids_par_salle.items() if s not in contigues}
print(f"  salles a identifiants contigus : {len(contigues)} sur "
      f"{len(ids_par_salle)}")
if eclatees:
    print(f"  salles eclatees : {len(eclatees)}")
    for s, ids in list(sorted(eclatees.items()))[:10]:
        print(f"    salle {s:3d} : {ids}")
    if len(eclatees) > 10:
        print(f"    ... et {len(eclatees) - 10} autres")
print()

print("=" * 72)
print("3. L'ordre des identifiants suit-il l'ordre des salles ?")
print("=" * 72)
print()
salles_ordonnees = [s for _, s in par_identifiant]
inversions = sum(1 for a, b in zip(salles_ordonnees, salles_ordonnees[1:])
                 if b < a)
print(f"  en parcourant les identifiants dans l'ordre croissant, le numero "
      f"de salle recule {inversions} fois sur {len(salles_ordonnees) - 1} pas")

premiers = sorted((min(ids), s) for s, ids in ids_par_salle.items())
recules = sum(1 for (_, a), (_, b) in zip(premiers, premiers[1:]) if b < a)
print(f"  en triant les salles par leur plus petit identifiant, l'ordre des "
      f"salles recule {recules} fois sur {len(premiers) - 1}")

sauts = [b - a for (a, _), (b, _) in zip(par_identifiant, par_identifiant[1:])]
print(f"  ecart entre identifiants consecutifs : "
      f"{sum(1 for e in sauts if e == 1)} pas de 1, "
      f"{sum(1 for e in sauts if e > 1)} sauts, plus grand saut {max(sauts)}")
