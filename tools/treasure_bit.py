"""Convertit un identifiant de tresor en adresse de bit, et l'inverse.

Le flag d'un tresor est un bit du tableau `Exxx` des variables de script,
4096 bits soit 0x200 octets, a l'adresse absolue 020560C8. Les tresors en
occupent les index bas. Voir formats-bis.md.

    bit du tresor N  ->  octet 020560C8 + N // 8, bit N % 8

L'adresse absolue vaut l'offset dans le domaine `Main RAM` de BizHawk
augmente de 0x02000000. Ce n'est pas une supposition : l'octet mesure a
l'offset 0x05610C correspond au 020560C8 du manuel, aux 68 octets pres
qu'imposent les identifiants 544 a 547.

Usage :
    venv\\Scripts\\python.exe tools\\treasure_bit.py 544 545 546
    venv\\Scripts\\python.exe tools\\treasure_bit.py --inverse 0x05610C 3
    venv\\Scripts\\python.exe tools\\treasure_bit.py --inverse 0x020560C8 0

Les deux formes d'adresse sont acceptees a l'inverse, offset dans le
domaine ou adresse absolue : elles ne peuvent pas etre confondues, le
tableau tenant entre 0x0560C8 et 0x0562C8.
"""
import argparse
import csv
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
CSV_LOCATIONS = RACINE / "data" / "locations_bis.csv"

BASE_MAIN_RAM = 0x02000000      # debut du domaine Main RAM, coeur NDS
BASE_OFFSET = 0x0560C8          # offset du tableau Exxx dans ce domaine
BASE_ABS = BASE_MAIN_RAM + BASE_OFFSET
TAILLE_EXXX = 0x200             # manuel : 4096 elements
NB_ELEMENTS = TAILLE_EXXX * 8   # 4096 bits
ID_MAX = 757                    # plus grand identifiant de TreasureInfo.dat
VAR_BASE = 0xE000               # hypothese H1 : index -> variable Exxx


def charge_locations():
    """Renvoie {identifiant: ligne du CSV}, ou {} si le CSV est absent."""
    if not CSV_LOCATIONS.exists():
        return {}
    lignes = {}
    with open(CSV_LOCATIONS, encoding="utf-8") as f:
        for ligne in csv.DictReader(f):
            if ligne["exploitable"] != "1":
                continue
            lignes[int(ligne["identifiant"])] = ligne
    return lignes


def decrit_location(ligne):
    if ligne is None:
        return "aucune entree exploitable a cet identifiant"
    nom = ligne["nom_item"]
    if nom == "pieces":
        montant = int(ligne["montant"])
        nom = f"{montant} piece" + ("s" if montant > 1 else "")
    return (f"{ligne['type_tresor']} / {nom} / salle {ligne['salle']}"
            f" / max_hits {ligne['max_hits']}"
            f" / xyz {ligne['x']},{ligne['y']},{ligne['z']}")


def verifie_index(index):
    """Un index hors du tableau Exxx sort de la structure documentee."""
    if not 0 <= index < NB_ELEMENTS:
        raise SystemExit(
            f"index {index} hors du tableau Exxx (0 a {NB_ELEMENTS - 1}). "
            f"Le tableau ne fait que {TAILLE_EXXX} octets."
        )


def direct(identifiants, locations):
    for n in identifiants:
        if not 0 <= n <= ID_MAX:
            raise SystemExit(
                f"identifiant {n} hors de TreasureInfo.dat (0 a {ID_MAX})."
            )
        verifie_index(n)
        octet, bit = divmod(n, 8)
        offset = BASE_OFFSET + octet
        print(f"identifiant {n}")
        print(f"  Main RAM offset  0x{offset:06X}")
        print(f"  adresse absolue  {BASE_ABS + octet:08X}")
        print(f"  bit              {bit}")
        print(f"  masque           0x{1 << bit:02X}")
        print(f"  variable Exxx    0x{VAR_BASE + n:04X}   (hypothese H1)")
        print(f"  location         {decrit_location(locations.get(n))}")
        print()


def inverse(adresse, bit, locations):
    if not 0 <= bit <= 7:
        raise SystemExit(f"rang de bit {bit} hors de 0 a 7.")
    offset = adresse - BASE_MAIN_RAM if adresse >= BASE_MAIN_RAM else adresse
    if not BASE_OFFSET <= offset < BASE_OFFSET + TAILLE_EXXX:
        raise SystemExit(
            f"adresse 0x{adresse:X} hors du tableau Exxx, qui va de "
            f"0x{BASE_OFFSET:06X} a 0x{BASE_OFFSET + TAILLE_EXXX:06X} "
            f"en offset Main RAM, soit {BASE_ABS:08X} a "
            f"{BASE_ABS + TAILLE_EXXX:08X} en absolu."
        )
    index = (offset - BASE_OFFSET) * 8 + bit
    verifie_index(index)
    print(f"Main RAM offset 0x{offset:06X} bit {bit}")
    print(f"  adresse absolue  {BASE_MAIN_RAM + offset:08X}")
    print(f"  index dans Exxx  {index}")
    print(f"  variable Exxx    0x{VAR_BASE + index:04X}   (hypothese H1)")
    if index > ID_MAX:
        print(f"  identifiant      aucun, les tresors s'arretent a {ID_MAX}")
        print(f"  index probablement utilise par un script d'evenement")
        return
    print(f"  identifiant      {index}")
    print(f"  location         {decrit_location(locations.get(index))}")


def main(argv=None):
    p = argparse.ArgumentParser(
        description="Identifiant de tresor <-> bit du tableau Exxx.",
        epilog="Sans --inverse, prend un ou plusieurs identifiants.",
    )
    p.add_argument("valeurs", nargs="+",
                   help="identifiants, ou adresse et rang de bit avec --inverse")
    p.add_argument("--inverse", action="store_true",
                   help="adresse puis rang de bit -> identifiant")
    args = p.parse_args(argv)

    try:
        nombres = [int(v, 0) for v in args.valeurs]
    except ValueError as e:
        raise SystemExit(f"valeur illisible : {e}")

    locations = charge_locations()
    if not locations:
        print(f"note : {CSV_LOCATIONS.name} absent, pas de correspondance "
              f"location. Regenerer avec tools/build_location_table.py.\n",
              file=sys.stderr)

    if args.inverse:
        if len(nombres) != 2:
            raise SystemExit("--inverse attend deux valeurs : adresse et bit.")
        inverse(nombres[0], nombres[1], locations)
    else:
        direct(nombres, locations)


if __name__ == "__main__":
    main()
