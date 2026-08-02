"""Croise trois dumps de RAM pour isoler les flags de tresor.

Usage :
    venv\\Scripts\\python.exe tools\\analyse_flags.py \\
        dumps\\run01_Main_RAM.bin dumps\\run02_Main_RAM.bin dumps\\run03_Main_RAM.bin

Contexte : run01 avant tout, run02 apres le bloc A, run03 apres le bloc B.

Un flag « tresor ramasse » a une signature tres particuliere : il monte a 1
et il y reste. On cherche donc deux motifs sur trois etats :

    bloc A -> 0, 1, 1
    bloc B -> 0, 0, 1

Le bruit (animations, timers, aleatoire, position) oscille et ne produit ces
motifs monotones que par accident. On croise ensuite les deux ensembles par
proximite : si les deux flags appartiennent au meme champ de bits, ils sont a
quelques octets l'un de l'autre.
"""
import csv
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
VOISINAGE = 256  # octets de part et d'autre pour considerer deux bits voisins


def bits_montants(avant, apres, taille):
    """Bits passes de 0 a 1 entre deux dumps."""
    res = set()
    for i in range(taille):
        a, b = avant[i], apres[i]
        if a == b:
            continue
        montes = (a ^ b) & b
        for j in range(8):
            if montes & (1 << j):
                res.add((i, j))
    return res


def bits_stables(d1, d2, taille):
    """Bits identiques entre deux dumps."""
    return {(i, j) for i in range(taille) for j in range(8)
            if (d1[i] >> j & 1) == (d2[i] >> j & 1)}


def main():
    if len(sys.argv) != 4:
        print(__doc__)
        return 1

    dumps = [Path(p).read_bytes() for p in sys.argv[1:4]]
    taille = min(len(d) for d in dumps)
    print(f"trois dumps de {taille} octets\n")

    d1, d2, d3 = dumps

    # Motif A : 0 -> 1 -> reste a 1
    monte_12 = bits_montants(d1, d2, taille)
    flags_a = {(i, j) for (i, j) in monte_12 if (d3[i] >> j & 1) == 1}
    # Motif B : reste a 0 -> 1
    monte_23 = bits_montants(d2, d3, taille)
    flags_b = {(i, j) for (i, j) in monte_23 if (d1[i] >> j & 1) == 0}

    print(f"bits 0->1 entre run01 et run02 : {len(monte_12)}")
    print(f"   dont encore a 1 dans run03  : {len(flags_a)}   <- candidats bloc A")
    print(f"bits 0->1 entre run02 et run03 : {len(monte_23)}")
    print(f"   dont a 0 des run01          : {len(flags_b)}   <- candidats bloc B")
    print()

    # Croisement par proximite
    paires = []
    liste_b = sorted(flags_b)
    for (ia, ja) in sorted(flags_a):
        for (ib, jb) in liste_b:
            if abs(ib - ia) <= VOISINAGE:
                rang_a = ia * 8 + ja
                rang_b = ib * 8 + jb
                paires.append((abs(rang_b - rang_a), ia, ja, ib, jb, rang_b - rang_a))

    print(f"paires de candidats a moins de {VOISINAGE} octets l'un de l'autre : {len(paires)}")
    if not paires:
        print("\nAucune paire. Soit les deux flags sont loin l'un de l'autre,")
        print("soit l'hypothese du champ de bits contigu ne tient pas ici.")
        return 0

    paires.sort()
    print("\nles 40 paires les plus proches, triees par ecart de rang de bit :")
    print(f"{'ecart':>7}  {'octet A':>9} {'bit':>3}  {'octet B':>9} {'bit':>3}  {'rangB-rangA':>12}")
    for ecart, ia, ja, ib, jb, signe in paires[:40]:
        print(f"{ecart:7d}  0x{ia:07X} {ja:3d}  0x{ib:07X} {jb:3d}  {signe:12d}")

    # Ecarts d'identifiants observes entre tresors d'une meme salle,
    # pour comparaison avec les ecarts de rang ci-dessus
    csv_loc = RACINE / "data" / "locations_bis.csv"
    if csv_loc.exists():
        salles = {}
        with open(csv_loc, encoding="utf-8") as f:
            for r in csv.DictReader(f):
                if r["exploitable"] == "1":
                    salles.setdefault(r["salle"], []).append(int(r["identifiant"]))
        ecarts = set()
        for ids in salles.values():
            ids.sort()
            for k in range(len(ids) - 1):
                ecarts.add(ids[k + 1] - ids[k])
        print(f"\necarts d'identifiants entre tresors consecutifs d'une meme salle,")
        print(f"observes dans locations_bis.csv : {sorted(ecarts)[:20]}")
        print("Si un ecart de rang ci-dessus figure dans cette liste, c'est le candidat.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
