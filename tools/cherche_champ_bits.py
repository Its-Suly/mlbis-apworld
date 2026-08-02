"""Cherche l'adresse de base du champ de bits des tresors.

Usage :
    venv\\Scripts\\python.exe tools\\cherche_champ_bits.py \\
        dumps\\run01_Main_RAM.bin dumps\\run02_Main_RAM.bin dumps\\run03_Main_RAM.bin

Principe. Chercher « un bit qui a bouge » ne discrimine rien, la RAM en est
pleine. On predit donc une adresse au lieu de la chercher.

Si le champ de bits existe a l'adresse de base A et qu'il est indexe par
l'identifiant du tresor (octets 4-5 de TreasureInfo.dat), alors le bit du
tresor d'identifiant `id` se trouve au rang absolu A * 8 + id.

Contraintes cumulees, chacune tres selective :
  1. le bit du bloc A suit le motif 0, 1, 1 sur les trois dumps
  2. le bit du bloc B suit le motif 0, 0, 1
  3. l'ecart entre leurs rangs vaut exactement id_B - id_A
  4. A est une adresse d'octet, donc rang - id doit etre divisible par 8
  5. les deux tresors appartiennent a la meme salle de locations_bis.csv

On essaie les deux ordres de bits dans l'octet, LSB d'abord et MSB d'abord,
parce que rien ne dit lequel le jeu utilise.
"""
import csv
import sys
from collections import defaultdict
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent


def rangs_par_motif(d1, d2, d3, taille, msb_first):
    """Renvoie deux ensembles de rangs de bits absolus, motifs 011 et 001."""
    p011, p001 = set(), set()
    for i in range(taille):
        a, b, c = d1[i], d2[i], d3[i]
        if a == b == c:
            continue
        for j in range(8):
            m = 1 << j
            va, vb, vc = (a & m) != 0, (b & m) != 0, (c & m) != 0
            if va or not vc:
                continue  # doit partir de 0 et finir a 1
            rang = i * 8 + (7 - j if msb_first else j)
            if vb:
                p011.add(rang)
            else:
                p001.add(rang)
    return p011, p001


def paires_meme_salle():
    """Toutes les paires ordonnees d'identifiants partageant une salle."""
    salles = defaultdict(list)
    with open(RACINE / "data" / "locations_bis.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["exploitable"] == "1":
                salles[r["salle"]].append((int(r["identifiant"]), r["nom_item"], r["type_tresor"]))
    paires = []
    for salle, tresors in salles.items():
        for x in tresors:
            for y in tresors:
                if x[0] != y[0]:
                    paires.append((salle, x, y))
    return paires


def main():
    if len(sys.argv) != 4:
        print(__doc__)
        return 1

    d1, d2, d3 = [Path(p).read_bytes() for p in sys.argv[1:4]]
    taille = min(len(d1), len(d2), len(d3))
    paires = paires_meme_salle()
    print(f"dumps de {taille} octets")
    print(f"paires ordonnees de tresors partageant une salle : {len(paires)}\n")

    for msb_first in (False, True):
        ordre = "MSB en premier" if msb_first else "LSB en premier"
        p011, p001 = rangs_par_motif(d1, d2, d3, taille, msb_first)
        print(f"--- ordre des bits : {ordre} ---")
        print(f"  bits motif 0,1,1 (bloc A) : {len(p011)}")
        print(f"  bits motif 0,0,1 (bloc B) : {len(p001)}")

        trouves = []
        for salle, (id_a, nom_a, type_a), (id_b, nom_b, type_b) in paires:
            delta = id_b - id_a
            for rang_a in p011:
                base_bits = rang_a - id_a
                if base_bits < 0 or base_bits % 8 != 0:
                    continue
                if (rang_a + delta) in p001:
                    trouves.append((base_bits // 8, salle, id_a, nom_a, type_a, id_b, nom_b, type_b))

        print(f"  bases candidates : {len(trouves)}")
        if trouves:
            vues = set()
            print(f"\n  {'base':>10}  {'salle':>5}  {'id A':>5} {'id B':>5}   contenu")
            for base, salle, id_a, nom_a, type_a, id_b, nom_b, type_b in sorted(trouves):
                cle = (base, id_a, id_b)
                if cle in vues:
                    continue
                vues.add(cle)
                print(f"  0x{base:08X}  {salle:>5}  {id_a:5d} {id_b:5d}   "
                      f"{type_a} {nom_a!r} puis {type_b} {nom_b!r}")
                if len(vues) >= 40:
                    print("  ... tronque a 40")
                    break
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
